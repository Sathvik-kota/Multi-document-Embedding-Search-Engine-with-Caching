# app.py
from fastapi import FastAPI
from pydantic import BaseModel
from .utils import preprocess_documents

app = FastAPI(title="Document Service")

class FolderRequest(BaseModel):
    folder: str

@app.post("/load_docs")
def load_docs(req: FolderRequest):
    try:
        docs = preprocess_documents(req.folder)
        return {
            "count": len(docs),
            "documents": docs
        }
    except Exception as e:
        return {"error": str(e)}
