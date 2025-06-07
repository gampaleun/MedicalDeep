from unsloth import FastLanguageModel
import torch
from trl import SFTTrainer
from unsloth import is_bfloat16_supported
from huggingface_hub import login
from transformers import TrainingArguments
from datasets import load_dataset
import wandb
import os
import pandas as pd
import re
import torch
from sentence_transformers import SentenceTransformer, util
from transformers import TextStreamer
from unsloth import FastLanguageModel

os.environ["CUDA_VISIBLE_DEVICES"] = "5"

term_df = pd.read_excel("terms.xlsx")

def make_term_variants(term):
    english_terms = re.findall(r"\((.*?)\)", term)
    base_term = re.sub(r"\(.*?\)", "", term).strip()
    return [base_term] + english_terms

term_entries = []
exact_term_lookup = {}
for _, row in term_df.iterrows():
    variants = make_term_variants(row["용어"])
    for v in variants:
        key = v.lower().strip()
        term_entries.append((key, f"{row['용어']}: {row['정의']}"))
        exact_term_lookup[key] = f"{row['용어']}: {row['정의']}"

term_texts = [entry[1] for entry in term_entries]

embed_model = SentenceTransformer("snunlp/KR-SBERT-V40K-klueNLI-augSTS")

embedding_file = "term_embeddings.pt"
if os.path.exists(embedding_file):
    print("✅ [로딩중] term_embeddings.pt 파일에서 임베딩 불러오는 중...")
    term_embeddings = torch.load(embedding_file)
else:
    print("✅ [임베딩중] term_texts 임베딩 생성 중... (시간 걸릴 수 있음)")
    term_embeddings = embed_model.encode(
        term_texts,
        batch_size=8,
        convert_to_tensor=True,
        show_progress_bar=True
    )
    torch.save(term_embeddings, embedding_file)
    print("✅ [완료] term_embeddings.pt 파일로 저장 완료!")

def extract_exact_matches(question):
    matches = []
    question_lower = question.lower()
    for key in exact_term_lookup:
        if key in question_lower:
            matches.append(f"- {exact_term_lookup[key]}")
    return matches

def embed_rag_context(question, top_k=1, max_context_terms=5):
    exact_matches = extract_exact_matches(question)
    q_embedding = embed_model.encode(question, convert_to_tensor=True)
    hits = util.semantic_search(q_embedding, term_embeddings, top_k=top_k)[0]
    retrieved = [f"- {term_texts[hit['corpus_id']]}" for hit in hits]

    context_set = list(dict.fromkeys(exact_matches + retrieved))
    limited_context = context_set[:max_context_terms]

    return "\n".join(limited_context)

