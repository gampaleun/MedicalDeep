import gradio as gr

# 사용자별 대화 저장소
user_sessions = {}

def simple_reply(msg):
    msg = msg.lower()
    if "안녕" in msg:
        return "안녕하세요! 무엇을 도와드릴까요?"
    elif "이름" in msg:
        return "저는 MedicalDeep 챗봇입니다!"
    elif "날씨" in msg:
        return "오늘은 맑고 따뜻합니다."
    else:
        return "죄송합니다. 아직 그 질문은 이해하지 못해요."

def chat_fn(message, selected_user, sessions):
    if selected_user not in sessions:
        sessions[selected_user] = []
    sessions[selected_user].append({"role": "user", "content": message})
    response = simple_reply(message)
    sessions[selected_user].append({"role": "assistant", "content": response})
    return "", sessions[selected_user], sessions

def add_user(name, birth, sessions):
    if not name or not birth:
        return gr.update(), "❗ 이름과 생년월일을 모두 입력하세요.", sessions
    user_key = f"{name} ({birth})"
    if user_key not in sessions:
        sessions[user_key] = []
    return gr.update(choices=list(sessions.keys()), value=user_key), "✅ 사용자 추가됨", sessions

def switch_user(user_key, sessions):
    if user_key in sessions:
        return sessions[user_key], sessions
    else:
        return [], sessions

# ✅ 여기 추가: 함수로 감싸기
def get_chatbot_ui():
    with gr.Column() as panel:
        sessions = gr.State(user_sessions)

        with gr.Row():
            # 좌측 사용자 관리 패널
            with gr.Column(scale=1):
                gr.Markdown("### 👤 사용자 목록")
                name = gr.Textbox(label="이름")
                birth = gr.Textbox(label="생년월일", placeholder="YYYY-MM-DD")
                add_btn = gr.Button("➕ 사용자 추가")
                user_msg = gr.Textbox(label="상태 메시지", interactive=False)
                selector = gr.Radio(choices=list(user_sessions.keys()), label="사용자 선택", interactive=True)

            # 우측 챗봇 영역
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(label="MedicalDeep 챗봇", height=500, type="messages")
                msg = gr.Textbox(placeholder="메시지를 입력하세요...", label="", lines=1)
                clear = gr.Button("대화 초기화")

        # 이벤트 연결
        add_btn.click(fn=add_user, inputs=[name, birth, sessions],
                      outputs=[selector, user_msg, sessions])
        selector.change(fn=switch_user, inputs=[selector, sessions],
                        outputs=[chatbot, sessions])
        msg.submit(fn=chat_fn, inputs=[msg, selector, sessions],
                   outputs=[msg, chatbot, sessions])
        clear.click(fn=lambda: ("", []), outputs=[msg, chatbot])

    return panel  # ✅ 이걸 login.py에서 끼워 넣을 수 있음
