from fastapi import FastAPI
from pydantic import BaseModel
from .utils import preprocess_documents, load_original_text

app = FastAPI(title="Document Service")

# Memory store (acts like small DB)
DOCUMENT_STORE = {}         # filename → cleaned text
ORIGINAL_STORE = {}         # filename → original text
HASH_STORE = {}             # filename → hash
META_STORE = {}             # filename → metadata (length etc)


class FolderRequest(BaseModel):
    folder: str


@app.post("/load_docs")
def load_docs(req: FolderRequest):
    """
    Loads documents from folder, cleans text, computes hash, stores everything.
    """

    global DOCUMENT_STORE, ORIGINAL_STORE, HASH_STORE, META_STORE

    try:
        docs = preprocess_documents(req.folder)

        for d in docs:
            fname = d["filename"]
            DOCUMENT_STORE[fname] = d["clean_text"]
            ORIGINAL_STORE[fname] = load_original_text(req.folder, fname)
            HASH_STORE[fname] = d["hash"]
            META_STORE[fname] = {"length": d["length"]}

        return {
            "count": len(docs),
            "files": list(DOCUMENT_STORE.keys())
        }

    except Exception as e:
        return {"error": str(e)}


# ---------------------------------------------------------
# GET A SINGLE DOCUMENT
# Needed by API Gateway for explanations
# ---------------------------------------------------------
@app.get("/get_doc/{filename}")
def get_doc(filename: str):

    if filename not in ORIGINAL_STORE:
        return {"error": f"Document {filename} not found"}

    return {
        "filename": filename,
        "text": ORIGINAL_STORE[filename],
        "clean_text": DOCUMENT_STORE[filename],
        "hash": HASH_STORE[filename],
        "meta": META_STORE.get(filename, {})
    }


# ---------------------------------------------------------
# Provide all documents when needed (for debugging)
# ---------------------------------------------------------
@app.get("/all_docs")
def all_docs():
    return {
        "count": len(DOCUMENT_STORE),
        "documents": list(DOCUMENT_STORE.keys())
    }
