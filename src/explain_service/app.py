# app.py
from fastapi import FastAPI
from pydantic import BaseModel
from explainer import Explainer

app = FastAPI(title="Explain Service")

explainer = Explainer()

class ExplainRequest(BaseModel):
    query: str
    document_text: str


@app.post("/explain")
def explain_doc(req: ExplainRequest):
    result = explainer.explain(req.query, req.document_text)
    return result
