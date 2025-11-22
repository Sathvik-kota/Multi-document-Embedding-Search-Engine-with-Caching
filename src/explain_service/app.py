# src/explain_service/app.py
from fastapi import FastAPI
from pydantic import BaseModel
from .explainer import Explainer

app = FastAPI(title="Explain Service")
explainer = Explainer()

class ExplainRequest(BaseModel):
    query: str
    document_text: str

@app.post("/explain")
def explain_doc(req: ExplainRequest):
    return explainer.explain(req.query, req.document_text)
