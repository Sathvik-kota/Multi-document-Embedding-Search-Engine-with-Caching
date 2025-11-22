# utils.py
import os
import hashlib
import re

def load_text_files(folder_path: str):
    docs = []
    for fname in os.listdir(folder_path):
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


def clean_text(text: str) -> str:
    # lowercase
    text = text.lower()
    # remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    # remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def compute_hash(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def preprocess_documents(folder_path: str):
    """
    Returns list of:
    {
        filename,
        text,
        clean_text,
        hash,
        length
    }
    """
    raw_docs = load_text_files(folder_path)
    result = []

    for doc in raw_docs:
        cleaned = clean_text(doc["text"])
        h = compute_hash(cleaned)
        result.append({
            "filename": doc["filename"],
            "clean_text": cleaned,
            "hash": h,
            "length": len(cleaned.split())
        })

    return result
