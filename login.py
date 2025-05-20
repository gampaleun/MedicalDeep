import gradio as gr
import subprocess  # chat.py 실행용

# 간단한 사용자 저장소 (메모리 기반)
users = {}

# 로그인 처리
def login(username, password):
    if username in users and users[username] == password:
        return "✅ 로그인 성공!", gr.update(visible=False), gr.update(visible=True)
    
    else:
        return "❌ 로그인 실패", gr.update(visible=True), gr.update(visible=False)

# 회원가입 처리
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

# 로그인 ↔ 회원가입 전환
def show_signup():
    return gr.update(visible=False), gr.update(visible=True)

def show_login():
    return gr.update(visible=True), gr.update(visible=False)

with gr.Blocks(css=".gr-button {background-color: #0077B6 !important; color: white !important;}") as app:
    gr.Markdown("<h1 style='color:#0077B6;'>MedicalDeep 인증</h1>")

    # 로그인 화면
    with gr.Column(visible=True) as login_panel:
        username = gr.Textbox(label="아이디")
        password = gr.Textbox(label="비밀번호", type="password")
        login_btn = gr.Button("로그인")
        login_msg = gr.Textbox(label="결과", interactive=False)
        switch_to_signup = gr.Button("회원가입으로")

    # 회원가입 화면
    with gr.Column(visible=False) as signup_panel:
        new_username = gr.Textbox(label="새 아이디")
        new_password = gr.Textbox(label="비밀번호", type="password")
        new_confirm = gr.Textbox(label="비밀번호 확인", type="password")
        signup_btn = gr.Button("회원가입")
        signup_msg = gr.Textbox(label="결과", interactive=False)
        switch_to_login = gr.Button("로그인으로")

    # 로그인 성공 시 메인 화면 (예시)
    subprocess.Popen(["python", "chat.py"])


    # 기능 연결
    login_btn.click(fn=login, inputs=[username, password],
                    outputs=[login_msg, login_panel, main_panel])
    
    signup_btn.click(fn=signup, inputs=[new_username, new_password, new_confirm],
                     outputs=[signup_msg])
    
    switch_to_signup.click(fn=show_signup, inputs=[], outputs=[login_panel, signup_panel])
    switch_to_login.click(fn=show_login, inputs=[], outputs=[login_panel, signup_panel])

app.launch(share=True)
