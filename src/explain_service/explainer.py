# src/explain_service/explainer.py
import re
import numpy as np
from sentence_transformers import SentenceTransformer
from google import genai

STOPWORDS = set("""
a an the and or but if while with without for on in into by to from of is are was were be been being as it this that these those
""".split())

class Explainer:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def tokenize(self, text: str):
        text = text.lower()
        tokens = re.findall(r"[a-zA-Z]+", text)
        tokens = [t for t in tokens if t not in STOPWORDS]
        return tokens

    def keyword_overlap(self, query: str, doc: str):
        q_tokens = set(self.tokenize(query))
        d_tokens = set(self.tokenize(doc))
        overlap = q_tokens.intersection(d_tokens)
        overlap_ratio = len(overlap) / (len(q_tokens) + 1e-8)
        return list(overlap), float(overlap_ratio)

    def best_sentences(self, query: str, doc: str, top_k=2):
        sentences = re.split(r"[.!?]", doc)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 0]
        if len(sentences) == 0:
            return []
        q_emb = self.model.encode(query, convert_to_numpy=True)
        s_embs = self.model.encode(sentences, convert_to_numpy=True)
        q_emb = q_emb / (np.linalg.norm(q_emb) + 1e-10)
        s_norm = s_embs / (np.linalg.norm(s_embs, axis=1, keepdims=True) + 1e-10)
        sims = (s_norm @ q_emb).tolist()
        top_ids = np.argsort(sims)[::-1][:top_k]
        results = []
        for idx in top_ids:
            results.append({"sentence": sentences[idx], "score": float(sims[idx])})
        return results

    def explain(self, query: str, doc_text: str):
        keywords, overlap_ratio = self.keyword_overlap(query, doc_text)
        top_sentences = self.best_sentences(query, doc_text)
        return {"keyword_overlap": keywords, "overlap_ratio": overlap_ratio, "top_sentences": top_sentences}

class Explainer:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.client = genai.Client(api_key="YOUR_KEY")   # <--- NEW

    def llm_explain(self, query, doc_text, top_sentences):
        prompt = f"""
You are an AI assistant that explains *why* a document matches a user query.

QUERY:
{query}

DOCUMENT (excerpt):
{doc_text[:500]}

MOST RELEVANT SENTENCES:
{top_sentences}

Explain in 2–3 natural sentences *why this document matches the query*.
Avoid repeating the sentences exactly; explain the reasoning.
"""

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={"temperature": 0.4}
        )

        return response.text.strip()
