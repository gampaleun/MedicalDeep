# main.py
import gradio as gr
from chat import generate_reply, init_model, release_model

APP_TITLE = "🩺 Medical Deep (On Device)"

SYSTEM_PROMPT = (
    "당신은 전문 의료 상담 챗봇입니다. "
    "모든 답변은 한국어로 작성하고, 일반 환자가 이해할 수 있도록 쉽게 설명하세요. "
    "답변은 간결하고 명확하게 작성해주세요. 불필요한 예시나 설명은 생략하고, 중요한 핵심 내용만 간단하게 설명해주세요. "
)


# 모델 한 번만 로드
llm = init_model()

def on_chat(user_msg, history):
    if not user_msg or not user_msg.strip():
        return gr.update(value=""), history

    # history를 최근 6개만 유지
    short_history = history[-6:] if history else []
    messages = []
    for msg in short_history:
        if isinstance(msg, dict):
            if msg["role"] == "user":
                messages.append((msg["content"], None))
            else:
                messages[-1] = (messages[-1][0], msg["content"])
        else:
            messages.append(msg)

    reply = generate_reply(
        user_msg=user_msg,
        history=messages,
        system_prompt=SYSTEM_PROMPT,
        llm=llm,
    )

    user_entry = {"role": "user", "content": user_msg}
    bot_entry = {"role": "assistant", "content": reply}
    history = short_history + [user_entry, bot_entry]

    return gr.update(value=""), history

with gr.Blocks(css="""
    .wrap {max-width: 880px; margin: 0 auto;}
    .title {text-align:center; padding: 8px 0 2px; font-size: 22px;}
""") as app:
    gr.HTML(f"<div class='wrap'><div class='title'>{APP_TITLE}</div></div>")

    with gr.Group():
        chatbot = gr.Chatbot(type="messages", height=600, label=None)
        with gr.Row():
            msg = gr.Textbox(placeholder="메시지를 입력하세요…", scale=10)
            send = gr.Button("보내기", scale=1)

    msg.submit(on_chat, [msg, chatbot], [msg, chatbot])
    send.click(on_chat, [msg, chatbot], [msg, chatbot])

    app.unload(lambda: release_model(llm))

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860, share=False)

