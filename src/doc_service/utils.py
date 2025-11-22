# src/doc_service/utils.py
import os
import hashlib
import re

def load_text_files(folder_path: str):
    docs = []
    for fname in sorted(os.listdir(folder_path)):
        if fname.endswith(".txt"):
            full_path = os.path.join(folder_path, fname)
            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
            docs.append({
                "filename": fname,
                "path": full_path,
                "text": text
            })
    return docs


def load_original_text(folder_path: str, filename: str):
    path = os.path.join(folder_path, filename)
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def compute_hash(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def preprocess_documents(folder_path: str):
    raw_docs = load_text_files(folder_path)
    result = []

    for doc in raw_docs:
        cleaned = clean_text(doc["text"])
        h = compute_hash(cleaned)
        result.append({
            "filename": doc["filename"],
            "clean_text": cleaned,
            "hash": h,
            "length": len(cleaned.split()),
            "original_text": doc["text"]
        })

    return result
