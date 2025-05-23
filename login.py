import gradio as gr
from ui import get_chatbot_ui  # ✅ ui.py 함수 가져옴

users = {}

# 로그인
def login(username, password):
    if username in users and users[username] == password:
        # 로그인 성공: UI 전환
        return "✅ 로그인 성공! 챗봇 화면으로 이동합니다.", gr.update(visible=False), gr.update(visible=True)
        
    else:
        return "❌ 로그인 실패", gr.update(visible=True), gr.update(visible=False)

# 회원 가입
def signup(username, password, confirm):
    if username in users:
        return "❌ 이미 존재하는 아이디입니다."
    elif password != confirm:
        return "❌ 비밀번호가 일치하지 않습니다."
    elif len(password) < 4:
        return "❌ 비밀번호는 최소 4자 이상이어야 합니다."
    else:
        users[username] = password
        return "✅ 회원가입 성공! 로그인 해주세요."

def show_signup():
    return gr.update(visible=False), gr.update(visible=True)

def show_login():
    return gr.update(visible=True), gr.update(visible=False)

with gr.Blocks(css=".gr-button {background-color: #0077B6 !important; color: white !important;}") as app:
    gr.Markdown("<h1 style='color:#0077B6;'>MedicalDeep 인증</h1>")

    with gr.Column(visible=True) as login_panel:
        username = gr.Textbox(label="아이디")
        password = gr.Textbox(label="비밀번호", type="password")
        login_btn = gr.Button("로그인")
        login_msg = gr.Textbox(label="결과", interactive=False)
        switch_to_signup = gr.Button("회원가입으로")

    with gr.Column(visible=False) as signup_panel:
        new_username = gr.Textbox(label="새 아이디")
        new_password = gr.Textbox(label="비밀번호", type="password")
        new_confirm = gr.Textbox(label="비밀번호 확인", type="password")
        signup_btn = gr.Button("회원가입")
        signup_msg = gr.Textbox(label="결과", interactive=False)
        switch_to_login = gr.Button("로그인으로")

    with gr.Column(visible=False) as main_panel:
        get_chatbot_ui()  # ✅ 이게 핵심

    login_btn.click(fn=login, inputs=[username, password],
                    outputs=[login_msg, login_panel, main_panel])
    signup_btn.click(fn=signup, inputs=[new_username, new_password, new_confirm],
                     outputs=[signup_msg])
    switch_to_signup.click(fn=show_signup, outputs=[login_panel, signup_panel])
    switch_to_login.click(fn=show_login, outputs=[login_panel, signup_panel])

app.launch()
