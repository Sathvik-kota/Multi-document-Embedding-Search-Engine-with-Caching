# explainer.py
import re
import numpy as np
from sentence_transformers import SentenceTransformer

# Simple stopword list
STOPWORDS = set("""
a an the and or but if while with without for on in into by to from of is are was were be been being as it this that these those
""".split())

class Explainer:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    # ---------------------------
    # Clean + tokenize query/doc
    # ---------------------------
    def tokenize(self, text: str):
        text = text.lower()
        tokens = re.findall(r"[a-zA-Z]+", text)
        tokens = [t for t in tokens if t not in STOPWORDS]
        return tokens

    # ------------------------------------
    # Keyword Overlap Score (simple & fast)
    # ------------------------------------
    def keyword_overlap(self, query: str, doc: str):
        q_tokens = set(self.tokenize(query))
        d_tokens = set(self.tokenize(doc))

        overlap = q_tokens.intersection(d_tokens)
        overlap_ratio = len(overlap) / (len(q_tokens) + 1e-5)

        return list(overlap), float(overlap_ratio)

    # ------------------------------------
    # Sentence-level similarity explanation
    # ------------------------------------
    def best_sentences(self, query: str, doc: str, top_k=2):
        # Split into sentences
        sentences = re.split(r"[.!?]", doc)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 0]

        if len(sentences) == 0:
            return []

        q_emb = self.model.encode(query, convert_to_numpy=True)
        s_embs = self.model.encode(sentences, convert_to_numpy=True)

        # Normalize
        q_emb = q_emb / (np.linalg.norm(q_emb) + 1e-10)
        s_norm = s_embs / (np.linalg.norm(s_embs, axis=1, keepdims=True) + 1e-10)

        sims = (s_norm @ q_emb).tolist()

        # Top-k indices
        top_ids = np.argsort(sims)[::-1][:top_k]

        results = []
        for idx in top_ids:
            results.append({
                "sentence": sentences[idx],
                "score": float(sims[idx])
            })

        return results

    # ---------------------------
    # Final explanation function
    # ---------------------------
    def explain(self, query: str, doc_text: str):
        keywords, overlap_ratio = self.keyword_overlap(query, doc_text)
        top_sentences = self.best_sentences(query, doc_text)

        return {
            "keyword_overlap": keywords,
            "overlap_ratio": overlap_ratio,
            "top_sentences": top_sentences
        }
