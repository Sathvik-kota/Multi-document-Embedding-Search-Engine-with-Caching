# embedder.py
from sentence_transformers import SentenceTransformer
import numpy as np

class Embedder:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)

    def embed_text(self, text: str):
        """Embed a single document or query."""
        emb = self.model.encode(text, convert_to_numpy=True)
        return emb.astype("float32")

    def embed_batch(self, texts: list):
        """Embed a batch of texts."""
        embs = self.model.encode(texts, convert_to_numpy=True)
        return embs.astype("float32")

    def dim(self):
        """Embedding vector size."""
        return self.model.get_sentence_embedding_dimension()
