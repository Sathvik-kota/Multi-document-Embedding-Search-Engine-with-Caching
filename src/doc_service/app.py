# src/doc_service/app.py
from fastapi import FastAPI
from pydantic import BaseModel
from src.doc_service.utils import preprocess_documents, load_original_text

app = FastAPI(title="Document Service")

class FolderRequest(BaseModel):
    folder: str

# In-memory stores (simple)
_DOCUMENTS = {}  # filename -> dict with clean_text, hash, length, original_text

@app.post("/load_docs")
def load_docs(req: FolderRequest):
    try:
        docs = preprocess_documents(req.folder)
        for d in docs:
            _DOCUMENTS[d["filename"]] = {
                "filename": d["filename"],
                "clean_text": d["clean_text"],
                "hash": d["hash"],
                "length": d["length"],
                "original_text": d["original_text"]
            }
        return {"count": len(docs), "documents": list(_DOCUMENTS.values())}
    except Exception as e:
        return {"error": str(e)}

@app.get("/get_doc/{filename}")
def get_doc(filename: str):
    if filename not in _DOCUMENTS:
        return {"error": "not_found", "message": f"{filename} not found"}
    return _DOCUMENTS[filename]

@app.get("/all_docs")
def all_docs():
    return {"count": len(_DOCUMENTS), "documents": list(_DOCUMENTS.values())}
