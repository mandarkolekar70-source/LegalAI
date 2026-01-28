import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import pickle
import os


class VectorStore:
    def __init__(
        self,
        index_path: str = "data/faiss_index.bin",
        metadata_path: str = "data/metadata.pkl"
    ):
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
        self.dimension = 384
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.metadata: List[Dict[str, Any]] = []

        if os.path.exists(index_path) and os.path.exists(metadata_path):
            self.index = faiss.read_index(index_path)
            with open(metadata_path, "rb") as f:
                self.metadata = pickle.load(f)
        else:
            self.index = faiss.IndexFlatL2(self.dimension)

    # ---------------- ADD TEXTS ----------------
    def add_texts(
        self,
        texts: List[str],
        metadatas: List[Dict[str, Any]]
    ):
        """
        Required metadata structure:
        {
            "source": "pdf_name.pdf",
            "text": "chunk text",
            "ipc_sections": [],
            "articles": [],
            "acts": []
        }
        """

        if not texts:
            return

        embeddings = self.encoder.encode(
            texts, show_progress_bar=True
        )

        self.index.add(np.array(embeddings).astype("float32"))

        for m, t in zip(metadatas, texts):
            self.metadata.append({
                "source": m.get("source", "Unknown PDF"),
                "text": t,
                "ipc_sections": m.get("ipc_sections", []),
                "articles": m.get("articles", []),
                "acts": m.get("acts", [])
            })

        self.save()

    # ---------------- SEARCH ----------------
    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        embedding = self.encoder.encode([query])
        distances, indices = self.index.search(
            np.array(embedding).astype("float32"), k
        )

        results = []
        for i, idx in enumerate(indices[0]):
            if idx == -1 or idx >= len(self.metadata):
                continue

            meta = self.metadata[idx].copy()
            distance = float(distances[0][i])

            relevance = max(55, int(100 - (distance * 10)))

            results.append({
                "source": meta.get("source"),
                "text": meta.get("text", ""),
                "ipc_sections": meta.get("ipc_sections", []),
                "articles": meta.get("articles", []),
                "acts": meta.get("acts", []),
                "score": distance,
                "relevance": f"{relevance}% match"
            })

        return results

    # ---------------- SAVE ----------------
    def save(self):
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)

        with open(self.metadata_path, "wb") as f:
            pickle.dump(self.metadata, f)
