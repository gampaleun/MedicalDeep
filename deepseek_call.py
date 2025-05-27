# deepseek_call.py
import requests

API_KEY = "your_deepseek_api_key"  # 본인의 DeepSeek API 키 입력
ENDPOINT = "https://api.deepseek.com/v1/chat/completions"  # DeepSeek 엔드포인트 확인 필요

def call_deepseek(messages):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",  # 사용 가능한 모델명 확인 필요
        "messages": messages,
        "temperature": 0.7
    }
    response = requests.post(ENDPOINT, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"❌ 오류 발생: {response.status_code} - {response.text}"
