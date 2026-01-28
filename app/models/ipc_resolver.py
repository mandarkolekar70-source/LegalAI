import pandas as pd
import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer


class IPCMatcher:
    def __init__(self):
        # Load IPC dataset
        self.df = pd.read_csv("data/ipc_sections.csv")

        # Combine section text
        self.texts = (
            self.df["section"].astype(str) + " " +
            self.df["title"] + " " +
            self.df["description"]
        ).tolist()

        # Load Legal-BERT
        self.model = SentenceTransformer("nlpaueb/legal-bert-base-uncased")

        # Create embeddings
        embeddings = self.model.encode(self.texts, normalize_embeddings=True)
        embeddings = np.array(embeddings)

        # Create FAISS index
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(embeddings)

    def find_ipc(self, case_text, top_k=3):
        query_emb = self.model.encode([case_text], normalize_embeddings=True)
        query_emb = np.array(query_emb)

        D, I = self.index.search(query_emb, top_k)

        results = []
        for idx, score in zip(I[0], D[0]):
            row = self.df.iloc[idx]
            results.append({
                "section": f"IPC {row['section']}",
                "title": row["title"],
                "confidence": round(float(score), 2)
            })

        return results
