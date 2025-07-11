# 🩺 MedicalDeep
Medical Deep은 환자 정보를 기반으로 맞춤형 상담이 가능한 의료 특화 챗봇 플랫폼입니다.

## 모델
**deepseek_r1_medicalQA_chatbot_최종.ipynb**: 딥시크를 준비한 의료 질문-추론-응답 데이터 4000개로 파인튜닝 후 허깅페이스에 업로드. 코사인 유사도와 BERT Score F1으로 검증 완료 (0.7)

**combined_translated_0000_3999.json**: 한글로 번역한 의료 질문-추론-응답 데이터.(4000개) 위 모델의 학습용 데이터.

**validation_translated_4001_4100.json, validation_translated_4101_4200.json** : 모델 성능 검증용 데이터

## 웹 애플리케이션
**login.py**: 사용자 로그인 기능, MySQL 서버 자동 실행

**main.py**: Gradio 기반 챗봇 웹 인터페이스 실행

**chat.py**: 의료 상담 챗봇 기능 구현, 환자 프로필 관리

## RAG
**rag.py**: 환자 질문에 포함되어있는 단어 중 병원_의학용어_정의_통합본_2.xlsx 데이터와 연관이 있어보이는 단어를 임베딩한 후 유사도 검색하여 프롬프트에 추가. 딥시크가 더 정확하고 자세한 설명을 하도록 유도.

**병원_의학용어_정의_통합본_2.xlsx** : rag에 활용하는 의료 데이터베이스 (의학 용어와 설명 사전)

## 기술 스택
Python
Gradio
MySQL
