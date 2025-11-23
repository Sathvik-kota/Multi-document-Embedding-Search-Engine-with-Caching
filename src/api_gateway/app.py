# src/api_gateway/app.py
from fastapi import FastAPI
from pydantic import BaseModel
import requests
import time
app = FastAPI(title="API Gateway")

DOC_URL = "http://localhost:9001"
EMBED_URL = "http://localhost:9002"
SEARCH_URL = "http://localhost:9003"
EXPLAIN_URL = "http://localhost:9004"
DATA_FOLDER = "data/docs"

class SearchQuery(BaseModel):
    query: str
    top_k: int = 5

@app.post("/initialize")
def initialize():
    # 1) load docs
    d = requests.post(f"{DOC_URL}/load_docs", json={"folder": DATA_FOLDER}, timeout=20)
    if d.status_code != 200:
        return {"error": "doc_load_failed", "detail": d.text}
    docs = d.json().get("documents", [])

    # 2) prepare docs for embed_batch: ensure keys filename,text,hash
    batch_docs = [{"filename": x["filename"], "text": x.get("clean_text", x.get("text","")), "hash": x["hash"]} for x in docs]

    # 3) embed batch
    e = requests.post(f"{EMBED_URL}/embed_batch", json={"docs": batch_docs}, timeout=60)
    if e.status_code != 200:
        return {"error": "embed_failed", "detail": e.text}
    embed_out = e.json()
    embeddings = [r["embedding"] for r in embed_out["results"]]
    meta = {i: r["filename"] for i, r in enumerate(embed_out["results"])}

    # 4) build index
    b = requests.post(f"{SEARCH_URL}/build_index", json={"embeddings": embeddings, "meta": meta}, timeout=60)
    if b.status_code != 200:
        return {"error": "build_index_failed", "detail": b.text}

    return {"docs_loaded": len(docs), "embeddings": len(embeddings), "build": b.json()}

@app.post("/search")
def search(req: SearchQuery):
    # embed query
    unique_id = str(time.time())
    q = requests.post(f"{EMBED_URL}/embed_document", json={"filename": f"query_{unique_id}", "text": req.query, "hash": unique_id},   timeout=10)
    if q.status_code != 200:
        return {"error": "embed_query_failed", "detail": q.text}
    q_emb = q.json()["embedding"]

    # search vectors
    s = requests.post(f"{SEARCH_URL}/search_vectors", json={"query_embedding": q_emb, "top_k": req.top_k}, timeout=10)
    if s.status_code != 200:
        return {"error": "search_failed", "detail": s.text}
    sdata = s.json()
    if "error" in sdata:
        return {"error": "search_index_error", "detail": sdata}

    scores = sdata["scores"]
    ids = sdata["ids"]
    meta = sdata["meta"]  # { "0": filename, ... }

    # for each id load doc from doc service and call explain
    results = []
    for score, idx in zip(scores, ids):
        filename = meta.get(str(idx))
        if filename is None:
            continue
        doc_resp = requests.get(f"{DOC_URL}/get_doc/{filename}", timeout=10)
        if doc_resp.status_code != 200:
            continue
        doc = doc_resp.json()  # has clean_text, original_text, ...
        # explain
        exp = requests.post(f"{EXPLAIN_URL}/explain", json={"query": req.query, "document_text": doc.get("clean_text","")}, timeout=10)
        explanation = exp.json() if exp.status_code == 200 else {}
        results.append({
            "filename": filename,
            "score": float(score),
            "preview": doc.get("clean_text","")[:350],
            "full_text": doc.get("original_text",""),
            "explanation": explanation
        })
    return {"results": results}
