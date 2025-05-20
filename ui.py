import gradio as gr

# 환자 세션 저장소
chat_sessions = {
    "원지니 천재": [],
    "박수민 똥강아지": []
}

def chatbot_response(msg, selected, sessions):
    reply = simple_reply(msg)
    sessions[selected].append(("🙋‍♂️: " + msg, "🤖: " + reply))
    return "", sessions[selected], sessions

def simple_reply(msg):
    msg = msg.lower()
    if "안녕" in msg:
        return "안녕하세요! 무엇을 도와드릴까요?"
    elif "날씨" in msg:
        return "오늘 날씨는 맑고 따뜻해요."
    elif "이름" in msg:
        return "저는 MedicalDeep 챗봇이에요!"
    else:
        return "뭐라는겨? 안녕 / 날씨 / 이름 중 선택하세요 저는 바보똥개라서요"

def switch_patient(name, sessions):
    return sessions[name], sessions

def add_patient(sessions):
    new_name = f"새환자 {len(sessions)+1}"
    sessions[new_name] = []
    return gr.update(choices=list(sessions.keys()), value=new_name), sessions[new_name], sessions

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
""") as demo:
    sessions = gr.State(chat_sessions)

    gr.HTML("<div id='toggle-btn' onclick='document.getElementById(\"sidebar\").classList.toggle(\"visible\")'>☰ 환자 목록</div>")

    # Sidebar
    with gr.Column(elem_id="sidebar"):
        gr.Markdown("### 🧑 환자 목록")
        selector = gr.Radio(choices=list(chat_sessions.keys()), value="원지니 천재", label="환자 목록", interactive=True)
        add_btn = gr.Button("➕ 새 환자 추가")

    # Main chat UI
    with gr.Column():
        gr.HTML("""
        <div style='text-align:center; background-color: #e6e7eb; padding: 15px; border-radius: 10px;'>
            <img src='https://i.ibb.co/7x6sVzXN/logo2.png' style='width: 200px;' />
        </div>
        """)
        chatbot = gr.Chatbot(label="🤖 MedicalDeep 챗봇", height=400)
        msg = gr.Textbox(placeholder="메시지를 입력하세요...", label="입력")
        clear = gr.Button("대화 초기화")

    # Event handling
    msg.submit(fn=chatbot_response, inputs=[msg, selector, sessions], outputs=[msg, chatbot, sessions])
    selector.change(fn=switch_patient, inputs=[selector, sessions], outputs=[chatbot, sessions])
    add_btn.click(fn=add_patient, inputs=[sessions], outputs=[selector, chatbot, sessions])
    clear.click(lambda: ("", []), outputs=[msg, chatbot])

demo.launch(share=True)
