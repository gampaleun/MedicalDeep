import os
import torch
import gradio as gr
from unsloth import FastLanguageModel
from transformers import TextStreamer

# ✅ 환경 설정
os.environ["CUDA_VISIBLE_DEVICES"] = "5"
os.environ["HF_TOKEN"] = "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"

# ✅ 모델 설정
max_seq_length = 2048
load_in_4bit = True
token = os.environ["HF_TOKEN"]

# ✅ 모델 로드
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="nanyaas/deepseek-r1-medicalQA-Qwen_first",
    max_seq_length=max_seq_length,
    load_in_4bit=load_in_4bit,
    token=token,
)

FastLanguageModel.for_inference(model)
streamer = TextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)

# ✅ 프롬프트 템플릿
def build_prompt(user_message):
    return f"""You are a medical expert with advanced knowledge in clinical reasoning, diagnostics, and treatment planning.
Respond carefully and step-by-step.

### Question:
{user_message}

### Response:
<think>"""

# ✅ 응답 생성 함수
def generate_llm_reply(user_message: str) -> str:
    prompt = build_prompt(user_message)
    inputs = tokenizer([prompt], return_tensors="pt").to("cuda")
    outputs = model.generate(
        input_ids=inputs.input_ids,
        attention_mask=inputs.attention_mask,
        max_new_tokens=512,
        temperature=0.7,
        top_p=0.9,
        do_sample=True,
        use_cache=True,
    )
    decoded = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
    if "### Response:" in decoded:
        return decoded.split("### Response:")[1].strip()
    elif "<think>" in decoded:
        return decoded.split("<think>")[-1].strip()
    return decoded.strip()

# ✅ 초기 채팅 세션
chat_sessions = {}

# ✅ 채팅 응답
def chatbot_response(msg, selected, sessions):
    reply = generate_llm_reply(msg)
    sessions[selected]["chat"].append([msg, reply])
    return "", sessions[selected]["chat"], sessions

# ✅ 환자 전환
def switch_patient(name, sessions):
    if name not in sessions:
        return [], sessions
    return sessions[name]["chat"], sessions

# ✅ 새 환자 추가
def confirm_add_patient(name, gender, birth, symptom, sessions):
    if name in sessions:
        return gr.update(), sessions
    sessions[name] = {"birth": birth, "gender": gender, "symptom": symptom, "chat": []}
    return name, sessions

# ✅ 상단 텍스트 갱신
def get_patient_header(name):
    return f"### {name}"

# ✅ Gradio UI 구성
def get_chatbot_ui():
    sessions = gr.State(chat_sessions)
    selector = gr.State("")

    gr.HTML(""" 
    <div id='toggle-btn' onclick='document.getElementById("sidebar").classList.toggle("visible")'
        style='position: fixed; top: 20px; left: 20px; z-index: 1000; background: white; border: 1px solid #ccc; padding: 5px 10px; border-radius: 5px; cursor: pointer;'>
        ☰ 환자 목록
    </div>
    <style>
    #sidebar {
        position: fixed;
        top: 0;
        left: 0;
        height: 100%;
        width: 220px;
        background-color: #f0f0f0;
        padding: 15px;
        box-shadow: 2px 0 5px rgba(0,0,0,0.1);
        transform: translateX(-100%);
        transition: transform 0.3s ease;
        z-index: 999;
    }
    #sidebar.visible {
        transform: translateX(0%);
    }
    .selected-patient-button {
        background-color: #e0e0e0 !important;
        font-weight: bold;
    }
    </style>
    <script>
    function highlightPatientButton(id) {
        document.querySelectorAll('button[id^="patient-btn-"]').forEach(btn => btn.classList.remove('selected-patient-button'));
        const el = document.getElementById(id);
        if (el) {
            el.classList.add('selected-patient-button');
            document.getElementById("sidebar").classList.remove("visible");
        }
    }
    </script>
    """)

    with gr.Column():
        selected_text = gr.Markdown("")
        chatbot = gr.Chatbot(label=None, height=400)
        msg = gr.Textbox(placeholder="메시지를 입력하세요...", label="입력")
        clear = gr.Button("대화 초기화")

    with gr.Column(elem_id="sidebar"):
        gr.Markdown("###환자 목록")
        patient_buttons = [gr.Button(visible=False, elem_id=f"patient-btn-{i}") for i in range(10)]

        with gr.Accordion("새 환자 추가", open=False):
            new_name = gr.Textbox(label="이름")
            new_gender = gr.Radio(label="성별", choices=["남자", "여자"])
            new_birth = gr.Textbox(label="생년월일 (YYYY-MM-DD)")
            new_symptom = gr.Textbox(label="증상")
            confirm_btn = gr.Button("환자추가")

    # 버튼 동작 정의
    def setup_patient_button(btn, name):
        btn.click(
            fn=lambda name=name: name,
            outputs=selector
        ).then(
            fn=switch_patient,
            inputs=[selector, sessions],
            outputs=[chatbot, sessions]
        ).then(
            fn=get_patient_header,
            inputs=[selector],
            outputs=[selected_text]
        )

    # 초기 버튼 세팅
    for i, btn in enumerate(patient_buttons):
        if i < len(chat_sessions):
            name = list(chat_sessions.keys())[i]
            btn.visible = True
            btn.value = name
            setup_patient_button(btn, name)

    # 새 환자 추가 후 버튼 업데이트
    def update_patient_buttons(sessions):
        names = list(sessions.keys())
        updates = []
        for i, btn in enumerate(patient_buttons):
            if i < len(names):
                updates.append(gr.update(value=names[i], visible=True))
            else:
                updates.append(gr.update(visible=False))
        return updates

    msg.submit(fn=chatbot_response, inputs=[msg, selector, sessions], outputs=[msg, chatbot, sessions])
    clear.click(fn=lambda: ("", []), outputs=[msg, chatbot])
    confirm_btn.click(
        fn=confirm_add_patient,
        inputs=[new_name, new_gender, new_birth, new_symptom, sessions],
        outputs=[selector, sessions]
    ).then(
        fn=update_patient_buttons,
        inputs=[sessions],
        outputs=patient_buttons
    ).then(
        fn=get_patient_header,
        inputs=[selector],
        outputs=[selected_text]
    )

    return {
        "sessions": sessions,
        "selector": selector,
        "chatbot": chatbot,
        "msg": msg,
        "clear": clear
    }
