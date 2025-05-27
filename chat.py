import gradio as gr
from hf_call import call_huggingface  # ✅ 새로운 함수 사용
# 환자 세션 저장소
chat_sessions = {
    "원지니 천재": [],
    "박수민 똥강아지": []
}

def chatbot_response(msg, selected, sessions):
    if selected not in sessions:
        sessions[selected] = []

    # 간단한 프롬프트 구성 (이전 대화 활용 X, 단순 버전)
    prompt = f"사용자: {msg}\nAI:"
    reply = call_huggingface(prompt)

    sessions[selected].append(("🙋‍♂️: " + msg, "🤖: " + reply))
    return "", sessions[selected], sessions



def switch_patient(name, sessions):
    return sessions[name], sessions

def add_patient(sessions):
    new_name = f"새환자 {len(sessions)+1}"
    sessions[new_name] = []
    return gr.update(choices=list(sessions.keys()), value=new_name), sessions[new_name], sessions

# ✅ login.py에서 호출할 함수 (gr.Blocks❌, gr.Column✅)
def get_chatbot_ui():
    sessions = gr.State(chat_sessions)

    gr.HTML("<div id='toggle-btn' onclick='document.getElementById(\"sidebar\").classList.toggle(\"visible\")'>☰ 환자 목록</div>")

    with gr.Column(elem_id="sidebar"):
        gr.Markdown("### 🧑 환자 목록")
        selector = gr.Radio(choices=list(chat_sessions.keys()), value="원지니 천재", label="환자 목록", interactive=True)
        add_btn = gr.Button("➕ 새 환자 추가")

    with gr.Column():
        gr.HTML("""
        <div style='text-align:center; background-color: #e6e7eb; padding: 15px; border-radius: 10px;'>
            <img src='https://i.ibb.co/7x6sVzXN/logo2.png' style='width: 200px;' />
        </div>
        """)
        chatbot = gr.Chatbot(label="🤖 MedicalDeep 챗봇", height=400)
        msg = gr.Textbox(placeholder="메시지를 입력하세요...", label="입력")
        clear = gr.Button("대화 초기화")

    # 이벤트 연결
    msg.submit(fn=chatbot_response, inputs=[msg, selector, sessions], outputs=[msg, chatbot, sessions])
    selector.change(fn=switch_patient, inputs=[selector, sessions], outputs=[chatbot, sessions])
    add_btn.click(fn=add_patient, inputs=[sessions], outputs=[selector, chatbot, sessions])
    clear.click(lambda: ("", []), outputs=[msg, chatbot])
