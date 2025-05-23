# ui.py
import gradio as gr

def get_chatbot_ui():
    with gr.Row():  # 좌우 분할
        with gr.Column(scale=1):  # 왼쪽 설정 패널
            gr.Markdown("### 🧑 사용자 정보 설정")
            name_input = gr.Textbox(label="이름")
            birth_input = gr.Textbox(label="생년월일 (YYYY-MM-DD)")
            info_output = gr.Textbox(label="입력된 정보", interactive=False)

            def save_info(name, birth):
                return f"이름: {name}\n생년월일: {birth}"

            save_btn = gr.Button("저장")
            save_btn.click(fn=save_info, inputs=[name_input, birth_input], outputs=[info_output])

        with gr.Column(scale=3):  # 오른쪽 챗봇 영역
            gr.Markdown("🤖 MedicalDeep 챗봇에 오신 것을 환영합니다!")
            chatbot = gr.Chatbot(label="🤖 챗봇", height=400, type="messages")
            msg = gr.Textbox(placeholder="메시지를 입력하세요...", label="입력")
            clear = gr.Button("대화 초기화")

            def bot_response(message, history):
                history.append({"role": "user", "content": message})
                history.append({"role": "assistant", "content": "대답 예시입니다"})
                return "", history

            msg.submit(fn=bot_response, inputs=[msg, chatbot], outputs=[msg, chatbot])
            clear.click(fn=lambda: ("", []), outputs=[msg, chatbot])

    return gr.Column()  # 아무거나 리턴하지 않아도 되지만 형태상 wrap
