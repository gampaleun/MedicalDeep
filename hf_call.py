import requests
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="hf_api_token.env")
API_TOKEN = os.getenv("HF_TOKEN")

MODEL_ID = "tiiuae/falcon-7b-instruct"
API_URL = f"https://api-inference.huggingface.co/models/{MODEL_ID}"


headers = {
    "Authorization": f"Bearer {API_TOKEN}"
}

def call_huggingface(prompt):
    payload = {
        "inputs": prompt,
        "parameters": {
            "temperature": 0.7,
            "max_new_tokens": 100,
            "return_full_text": False
        }
    }
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            return response.json()[0]["generated_text"]
        else:
            print(f"[API ERROR] {response.status_code} - {response.text}")
            print("[DEBUG] API_URL:", API_URL)
            print("[DEBUG] prompt:", prompt)
            return "🤖: API 오류 발생"
    except Exception as e:
        print(f"[NETWORK ERROR] {e}")
        return "🤖: 네트워크 오류 발생"
