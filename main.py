import gradio as gr
from login import login, signup, show_login, show_signup
from chat import get_chatbot_ui, chatbot_response

def switch_patient(name, sessions):
    if name not in sessions:
        return [], sessions
    return sessions[name]["chat"], sessions

def build_ui():
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
        <div style="display: flex; justify-content: center; align-items: center; padding: 20px;">
            <img src="https://i.ibb.co/7x6sVzXN/logo2.png" style="width: 200px;" />
        </div>
        """)

        with gr.Column(visible=True) as login_panel:
            username = gr.Textbox(label="아이디")
            password = gr.Textbox(label="비밀번호", type="password")
            login_btn = gr.Button("로그인")
            login_msg = gr.Textbox(interactive=False)
            switch_to_signup = gr.Button("회원가입")

        with gr.Column(visible=False) as signup_panel:
            new_username = gr.Textbox(label="새 아이디")
            new_password = gr.Textbox(label="비밀번호", type="password")
            new_confirm = gr.Textbox(label="비밀번호 확인", type="password")
            signup_btn = gr.Button("회원가입")
            signup_msg = gr.Textbox(label="결과", interactive=False)
            switch_to_login = gr.Button("로그인으로")

        with gr.Column(visible=False) as main_panel:
            ui = get_chatbot_ui()

        login_btn.click(fn=login, inputs=[username, password], outputs=[login_msg, login_panel, main_panel])
        signup_btn.click(fn=signup, inputs=[new_username, new_password, new_confirm], outputs=[signup_msg])
        switch_to_signup.click(fn=show_signup, outputs=[login_panel, signup_panel])
        switch_to_login.click(fn=show_login, outputs=[login_panel, signup_panel])

        ui["selector"].change(
            fn=switch_patient,
            inputs=[ui["selector"], ui["sessions"]],
            outputs=[ui["chatbot"], ui["sessions"]]
        )

        ui["msg"].submit(
            fn=chatbot_response,
            inputs=[ui["msg"], ui["selector"], ui["sessions"]],
            outputs=[ui["msg"], ui["chatbot"], ui["sessions"]],
        )

    return app

if __name__ == "__main__":
    build_ui().launch(server_name="0.0.0.0", server_port=7860, share=True)
