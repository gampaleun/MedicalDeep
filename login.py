from dotenv import load_dotenv
import os
import mysql.connector
import gradio as gr

load_dotenv("key.env")

def show_login():
    return gr.update(visible=True), gr.update(visible=False)

def show_signup():
    return gr.update(visible=False), gr.update(visible=True)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", 3306))
    )

def signup(username, password, confirm):
    if password != confirm:
        return gr.update(value="❌ 비밀번호가 일치하지 않습니다.", visible=True)
    elif len(password) < 4:
        return gr.update(value="❌ 비밀번호는 최소 4자 이상이어야 합니다.", visible=True)

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        return gr.update(value="✅ 회원가입 성공! 로그인해주세요.", visible=True)
    except mysql.connector.IntegrityError:
        return gr.update(value="❌ 이미 존재하는 아이디입니다.", visible=True)
    finally:
        cursor.close()
        conn.close()

def login(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result and password == result[0]:
        return (
            gr.update(value="✅ 로그인 성공!", visible=True),
            gr.update(visible=False),
            gr.update(visible=True)
        )
    else:
        return (
            gr.update(value="❌ 로그인 실패", visible=True),
            gr.update(visible=True),
            gr.update(visible=False)
        )

with gr.Blocks() as demo:
    with gr.Tab("회원가입"):
        u1 = gr.Textbox(label="아이디")
        p1 = gr.Textbox(label="비밀번호", type="password")
        c1 = gr.Textbox(label="비밀번호 확인", type="password")
        out1 = gr.Textbox(label="결과 메시지")
        btn1 = gr.Button("회원가입")
        btn1.click(fn=signup, inputs=[u1, p1, c1], outputs=out1)

    with gr.Tab("로그인"):
        u2 = gr.Textbox(label="아이디")
        p2 = gr.Textbox(label="비밀번호", type="password")
        out2 = gr.Textbox(label="결과 메시지")
        btn2 = gr.Button("로그인")
        btn2.click(fn=login, inputs=[u2, p2], outputs=out2)
