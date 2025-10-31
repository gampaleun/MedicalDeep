import os
import re
import gc
from llama_cpp import Llama

# ─────────────────────────────
# 기본 설정 (Nano friendly)
# ─────────────────────────────
MODEL_PATH = os.getenv("MODEL_PATH", "/home/haneum/Documents/medicalQA-q4_k_m.gguf")
N_THREADS = 2
N_CTX = int(os.getenv("N_CTX", "2048"))
N_GPU_LAYERS = int(os.getenv("N_GPU_LAYERS", "0"))
MAX_NEW_TOKENS = int(os.getenv("MAX_NEW_TOKENS", "2048"))

THINK_CLEAN_RE = re.compile(r"(?s)<\s*think\s*>.*?<\s*/\s*think\s*>")

# ─────────────────────────────
# 모델 초기화 / 해제
# ─────────────────────────────
def init_model():
    try:
        print(f"🔹 Loading model from {MODEL_PATH}")
        llm = Llama(
            model_path=MODEL_PATH,
            n_threads=N_THREADS,
            n_ctx=N_CTX,
            n_gpu_layers=N_GPU_LAYERS,
            verbose=True,  # Enable verbose for more detailed logging
        )
        print("✅ Model loaded successfully!")
        return llm
    except ValueError as e:
        if "unknown pre-tokenizer type: 'deepseek-r1-qwen'" in str(e):
            print(f"❌ Error: This model has a custom tokenizer 'deepseek-r1-qwen' that is not supported.")
            print("❌ Try using a different model or converting the model to a compatible format.")
        else:
            print(f"❌ Model loading failed: {e}")
        raise e
    except Exception as e:
        print(f"❌ Unexpected error loading model: {e}")
        raise e

def release_model(llm):
    try:
        del llm
    except Exception:
        pass
    gc.collect()

# ─────────────────────────────
# 프롬프트 구성
# ─────────────────────────────
def build_prompt(system_prompt, history, user_msg):
    parts = []
    if system_prompt:
        parts.append(f"<<SYS>>\n{system_prompt}\n<</SYS>>\n")
    for u, b in history or []:
        if u:
            parts.append(f"<|user|>\n{u}\n")
        if b:
            parts.append(f"<|assistant|>\n{b}\n")
    parts.append(f"<|user|>\n{user_msg}\n<|assistant|>\n")
    return "".join(parts)

# ─────────────────────────────
# 출력 후처리
# ─────────────────────────────
def clean_output(text):
    # Remove unnecessary tokens like <think> tags if present
    text = THINK_CLEAN_RE.sub("", text)   

    # Remove excessive spaces
    text = re.sub(r"\s+", " ", text).strip()  # Extra spaces handling

    # Ensure we don't end on an incomplete sentence
    if text and not text.endswith(('.', '!', '?')):
        text += "."

    return text


# ─────────────────────────────
# 응답 생성
# ─────────────────────────────
def generate_reply(user_msg, history=None, system_prompt=None, llm=None):
    if llm is None:
        raise RuntimeError("Model not initialized")

    # Build the prompt with user input and history
    prompt = build_prompt(system_prompt, history, user_msg)

    try:
        # Generate output from the model with max tokens and some control over response length
        out = llm(
            prompt,
            max_tokens=MAX_NEW_TOKENS,
            temperature=0.7,
            top_p=0.8,
            repeat_penalty=1.05,
            stop=["<|user|>", "<<SYS>>", "<</SYS>>"],
        )
    except Exception as e:
        print(f"[ERROR] 모델 호출 실패: {e}")
        return "죄송합니다. 현재 모델이 응답을 생성할 수 없습니다."

    try:
        text = out["choices"][0]["text"]
        # Remove unnecessary tokens or characters, clean the output
        text = clean_output(text)
    except Exception as e:
        print(f"[ERROR] 출력 파싱 실패: {e}")
        text = "출력 처리 중 오류가 발생했습니다."

    if not text:
        text = "말씀하신 내용을 이해하지 못했습니다. 다시 한 번 구체적으로 말씀해 주세요."

    return text

