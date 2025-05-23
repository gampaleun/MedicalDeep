# ui.py
import gradio as gr

def get_chatbot_ui():
    with gr.Column():
        gr.Markdown("🤖 MedicalDeep 챗봇에 오신 것을 환영합니다!")
        chatbot = gr.Chatbot(label="🤖 챗봇", height=400)
        msg = gr.Textbox(placeholder="메시지를 입력하세요...", label="입력")
        clear = gr.Button("대화 초기화")

        def bot_response(message, history):
            history.append((message, "대답 예시입니다"))
            return "", history

        msg.submit(fn=bot_response, inputs=[msg, chatbot], outputs=[msg, chatbot])
        clear.click(fn=lambda: ("", []), outputs=[msg, chatbot])

    return gr.update(visible=True), gr.update(visible=False)
