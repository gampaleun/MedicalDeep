# login.py
import gradio as gr

# 사용자 저장소 (간단한 예시용 딕셔너리)
users = {"admin": "1234"}

# ✅ 로그인 로직
def login(username, password):
    if username in users and users[username] == password:
        return "✅ 로그인 성공! 챗봇 화면으로 이동합니다.", gr.update(visible=False), gr.update(visible=True)
    else:
        return "로그인 실패", gr.update(visible=True), gr.update(visible=False)

# ✅ 회원가입 로직
def signup(username, password, confirm):
    if username in users:
        return "이미 존재하는 아이디입니다."
    elif password != confirm:
        return "비밀번호가 일치하지 않습니다."
    elif len(password) < 4:
        return "비밀번호는 최소 4자 이상이어야 합니다."
    else:
        users[username] = password
        return "✅ 회원가입 성공! 로그인 해주세요."

# ✅ 화면 전환 로직
def show_signup():
    return gr.update(visible=False), gr.update(visible=True)

def show_login():
    return gr.update(visible=True), gr.update(visible=False)

# ✅ 로그인/회원가입 UI 반환
def get_login_ui():
    with gr.Column(visible=True) as login_panel:
        username = gr.Textbox(label="아이디")
        password = gr.Textbox(label="비밀번호", type="password")
        login_btn = gr.Button("로그인")
        login_msg = gr.Textbox(interactive=False)
        switch_to_signup = gr.Button("회원가입으로")

    with gr.Column(visible=False) as signup_panel:
        new_username = gr.Textbox(label="새 아이디")
        new_password = gr.Textbox(label="비밀번호", type="password")
        new_confirm = gr.Textbox(label="비밀번호 확인", type="password")
        signup_btn = gr.Button("회원가입")
        signup_msg = gr.Textbox(interactive=False)
        switch_to_login = gr.Button("로그인으로")

    return {
        "login_panel": login_panel,
        "signup_panel": signup_panel,
        "username": username,
        "password": password,
        "login_btn": login_btn,
        "login_msg": login_msg,
        "switch_to_signup": switch_to_signup,
        "new_username": new_username,
        "new_password": new_password,
        "new_confirm": new_confirm,
        "signup_btn": signup_btn,
        "signup_msg": signup_msg,
        "switch_to_login": switch_to_login,
    }
