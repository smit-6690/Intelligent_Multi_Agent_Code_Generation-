from __future__ import annotations

from pathlib import Path

class FaissRetriever:
    def __init__(self, directory: str | Path):
        import faiss
        import numpy as np
        from sentence_transformers import SentenceTransformer

        directory = Path(directory)
        self.index = faiss.read_index(str(directory / "index.faiss"))
        self.documents = np.load(directory / "documents.npy", allow_pickle=True).tolist()
        model_name = (directory / "embedding_model.txt").read_text(encoding="utf-8").strip()
        self.encoder = SentenceTransformer(model_name)

    def retrieve(self, query: str, top_k: int = 3) -> str:
        vector = self.encoder.encode([query], normalize_embeddings=True).astype("float32")
        _, indices = self.index.search(vector, top_k)
        return "\n\n".join(self.documents[index] for index in indices[0] if index >= 0)


class NullRetriever:
    def retrieve(self, query: str, top_k: int = 3) -> str:
        return ""
