import os

os.environ["CUDA_VISIBLE_DEVICES"] = "5"
os.environ["HF_TOKEN"] = "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"

import gradio as gr
from unsloth import FastLanguageModel
from transformers import TextStreamer
import torch
from rag import embed_rag_context
from datetime import datetime

os.environ["CUDA_VISIBLE_DEVICES"] = "5"
os.environ["HF_TOKEN"] = "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"

# ✅ 모델 설정
max_seq_length = 2048
load_in_4bit = True
token = os.environ["HF_TOKEN"]

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="nanyaas/deepseek-r1-medicalQA-Qwen_first",
    max_seq_length=max_seq_length,
    load_in_4bit=load_in_4bit,
    token=token,
)

FastLanguageModel.for_inference(model)
streamer = TextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)

def build_prompt(user_message: str, prev_user: str = None, prev_bot: str = None, patient_info: dict = None) -> str:
    try:
        # 기본 지시사항
        sections = [
            "### 지시사항:\n"
            "한국말로만 설명하세요."
            "아래 환자 정보를 최우선으로 참고하여 답변을 작성하세요. "
            "이전 대화를 참고하여 흐름에 맞게 대화를 하세요."
            "환자가 설명을 이해할 수 있도록 추가맥락을 참고하여 쉽게 설명하세요."
        ]

        # 환자 정보
        if patient_info:
            gender = patient_info.get("gender", "Unknown")
            birth = patient_info.get("birth")
            age = calculate_age(birth) if birth else "Unknown"
            symptom = patient_info.get("symptom", "Unknown")

            sections.append(
                "### 환자 정보:\n"
                f"- 성별: {gender}\n"
                f"- 나이: {age}\n"
                f"- 증상: {symptom}\n"
            )

        # 이전 대화
        if prev_user and prev_bot:
            sections.append(
                "\n### 이전 대화:\n"
                f"[사용자] {prev_user}\n"
                f"[의사] {prev_bot}\n"
            )

        # RAG 기반 추가 맥락
        rag_context = embed_rag_context(user_message)
        if rag_context:
            sections.append(f"\n### 추가 맥락:\n{rag_context}\n")

        # 질문
        sections.append(f"\n### 질문:\n{user_message}\n\n### 응답:")

        return "\n".join(sections)

    except Exception as e:
        return f"❌ 에러 발생: {str(e)}"


def calculate_age(birth_date_str):
    try:
        if not birth_date_str:
            return 0

        birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d")
        today = datetime.today()

        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

        if age < 0:
            return 0
        return age
    except Exception:
        return 0

def generate_llm_reply(user_message: str, prev_user: str = None, prev_bot: str = None, patient_info: dict = None) -> str:
    try:
        prompt = build_prompt(user_message, prev_user, prev_bot, patient_info)
        inputs = tokenizer([prompt], return_tensors="pt").to("cuda")
        outputs = model.generate(
            input_ids=inputs.input_ids,
            attention_mask=inputs.attention_mask,
            max_new_tokens=1024,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            use_cache=True,
        )
        torch.cuda.synchronize()
        torch.cuda.empty_cache()
        decoded = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
        print(f"Decoded output:\n{decoded}")

        # 프롬프트 제거
        decoded = decoded.replace(prompt, "").strip()

        # </think> 뒤만 추출
        end_tag = "</think>"
        end_idx = decoded.find(end_tag)

        if end_idx != -1:
            reply = decoded[end_idx + len(end_tag):].strip()
        else:
            reply = decoded.strip()

        return reply

    except Exception as e:
        return f"❌ 에러 발생: {str(e)}"



chat_sessions = {}

import copy

def chatbot_response(msg, selected, sessions):
    new_sessions = copy.deepcopy(sessions)

    history = new_sessions.get(selected, {}).get("chat", [])
    prev_user = None
    prev_bot = None
    for turn in reversed(history):
        if turn["role"] == "assistant" and prev_bot is None:
            prev_bot = turn["content"]
        elif turn["role"] == "user" and prev_user is None:
            prev_user = turn["content"]
        if prev_user and prev_bot:
            break

    patient_info = new_sessions.get(selected, {}).copy()
    patient_info["name"] = selected  # selected가 이름

    # ❗️ 여기서 patient_info 넘기기
    reply = generate_llm_reply(msg, prev_user, prev_bot, patient_info=patient_info)

    if selected in new_sessions:
        new_sessions[selected]["chat"].append({"role": "user", "content": msg})
        new_sessions[selected]["chat"].append({"role": "assistant", "content": reply})

    return "", new_sessions[selected]["chat"], new_sessions


def switch_patient(name, sessions):
    if name not in sessions:
        return [], sessions
    return sessions[name]["chat"], sessions

def confirm_add_patient(name, gender, birth, symptom, sessions):
    if name in sessions:
        return gr.update(), sessions
    sessions[name] = {"birth": birth, "gender": gender, "symptom": symptom, "chat": []}
    return name, sessions

def edit_patient_info(new_name, birth, gender, symptom, selected, sessions):
    if selected in sessions:
        sessions[new_name] = sessions.pop(selected)
        sessions[new_name]["birth"] = birth
        sessions[new_name]["gender"] = gender
        sessions[new_name]["symptom"] = symptom
    return new_name, sessions

def delete_patient(selected, sessions):
    if selected in sessions:
        del sessions[selected]
    return "", [], sessions

def load_patient_info(selected, sessions):
    if selected in sessions:
        data = sessions[selected]
        return selected, data.get("birth", ""), data.get("gender", None), data.get("symptom", "")
    return "", "", None, ""

def get_patient_header(name):
    return f"### {name}"

def get_chatbot_ui():
    sessions = gr.State(chat_sessions)
    selector = gr.State("")

    gr.HTML(""" 
    <div id='toggle-btn' onclick='document.getElementById("sidebar").classList.toggle("visible")'
        style='position: fixed; top: 20px; left: 20px; z-index: 1000; background: white; border: 1px solid #ccc; padding: 5px 10px; border-radius: 5px; cursor: pointer;'>
        ☰ 환자 목록
    </div>
    <style>
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
    </style>
    <script>
    function highlightPatientButton(id) {
        document.querySelectorAll('button[id^="patient-btn-"]').forEach(btn => btn.classList.remove('selected-patient-button'));
        const el = document.getElementById(id);
        if (el) {
            el.classList.add('selected-patient-button');
            document.getElementById("sidebar").classList.remove("visible");
        }
    }
    </script>
    """)

    has_patients = bool(chat_sessions)
    chatbot_container = gr.Column(visible=has_patients)
    empty_notice = gr.HTML(
        """
        <div style='height: 400px; display: flex; justify-content: center; align-items: center; text-align: center; font-size: 1.2rem; color: gray;'>
            <div>
                <p>🩺 환자를 먼저 추가하세요.</p>
            </div>
        </div>
        """,
        visible=not has_patients
    )

    with chatbot_container:
        with gr.Tabs():
            with gr.Tab("대화"):
                selected_text = gr.Markdown("")
                chatbot = gr.Chatbot(label=None, height=700, type="messages")

                msg = gr.Textbox(placeholder="메시지를 입력하세요...", label="입력")

            with gr.Tab("환자 정보 수정"):
                edit_gender = gr.Radio(label="성별", choices=["남자", "여자"])
                edit_birth = gr.Textbox(label="생년월일")
                edit_symptom = gr.Textbox(label="증상")
                save_btn = gr.Button("저장")
                save_result = gr.Textbox(interactive=False)

    with gr.Column(elem_id="sidebar"):
        gr.Markdown("###환자 목록")
        patient_buttons = [gr.Button(visible=False, elem_id=f"patient-btn-{i}") for i in range(10)]

        with gr.Accordion("새 환자 추가", open=False):
            new_name = gr.Textbox(label="이름")
            new_gender = gr.Radio(label="성별", choices=["남자", "여자"])
            new_birth = gr.Textbox(label="생년월일 (YYYY-MM-DD)")
            new_symptom = gr.Textbox(label="증상")
            confirm_btn = gr.Button("환자추가")

    def setup_patient_button(btn):
        btn.click(
            fn=lambda name: name,
            inputs=[btn],
            outputs=selector
        ).then(
            fn=switch_patient,
            inputs=[selector, sessions],
            outputs=[chatbot, sessions]
        ).then(
            fn=get_patient_header,
            inputs=[selector],
            outputs=[selected_text]
        )

    for btn in patient_buttons:
        setup_patient_button(btn)

    def update_patient_buttons(sessions):
        names = list(sessions.keys())
        updates = []
        for i, btn in enumerate(patient_buttons):
            if i < len(names):
                updates.append(gr.update(value=names[i], visible=True))
            else:
                updates.append(gr.update(visible=False))
        return updates

    def toggle_chat_ui_on_add(selector_val, sessions_val):
        return gr.update(visible=True), gr.update(visible=False)

    def load_patient_info(patient_id, sessions):
        info = sessions.get(patient_id, {})
        return (
            info.get("gender", ""),
            info.get("birth", ""),
            info.get("symptom", "")
        )

    def save_patient_info(patient_id, gender, birth, symptom, sessions):
        if patient_id in sessions:
            sessions[patient_id]["gender"] = gender
            sessions[patient_id]["birth"] = birth
            sessions[patient_id]["symptom"] = symptom
            return "✅ 저장되었습니다.", sessions
        else:
            return "❌ 환자 정보 없음", sessions

    # msg.submit(fn=chatbot_response, inputs=[msg, selector, sessions], outputs=[msg, chatbot, sessions])

    confirm_btn.click(
        fn=confirm_add_patient,
        inputs=[new_name, new_gender, new_birth, new_symptom, sessions],
        outputs=[selector, sessions]
    ).then(
        fn=update_patient_buttons,
        inputs=[sessions],
        outputs=patient_buttons
    ).then(
        fn=get_patient_header,
        inputs=[selector],
        outputs=[selected_text]
    ).then(
        fn=toggle_chat_ui_on_add,
        inputs=[selector, sessions],
        outputs=[chatbot_container, empty_notice]
    ).then(
        fn=lambda: ("", None, "", ""),
        outputs=[new_name, new_gender, new_birth, new_symptom]
    )

    selector.change(
        fn=load_patient_info,
        inputs=[selector, sessions],
        outputs=[edit_gender, edit_birth, edit_symptom]
    )

    save_btn.click(
        fn=save_patient_info,
        inputs=[selector, edit_gender, edit_birth, edit_symptom, sessions],
        outputs=[save_result, sessions]
    )

    return {
        "sessions": sessions,
        "selector": selector,
        "chatbot": chatbot,
        "msg": msg,
        "chatbot_container": chatbot_container,
        "empty_notice": empty_notice
    }
