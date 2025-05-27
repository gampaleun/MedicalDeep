import gradio as gr
from chat import get_chatbot_ui

users = {
    "123": "1234",      # ✅ 아이디: admin / 비밀번호: 1234
}
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

with gr.Blocks(css="""
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
#toggle-btn {
  position: fixed;
  top: 20px;
  left: 20px;
  z-index: 1000;
  background: white;
  border: 1px solid #ccc;
  padding: 5px 10px;
  border-radius: 5px;
  cursor: pointer;
}
""") as app:
    gr.HTML("""
        <div style='text-align:center; background-color: #e6e7eb; padding: 15px; border-radius: 10px;'>
            <img src='https://i.ibb.co/7x6sVzXN/logo2.png' style='width: 200px;' />
        </div>
        """)

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
