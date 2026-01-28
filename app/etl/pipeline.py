import os
import sys
from pathlib import Path
import pickle

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.etl.extractor import extract_text_from_pdf
from app.etl.transformer import chunk_text, extract_legal_entities
from app.vector_store.faiss_store import VectorStore

# Max PDFs to process
MAX_PDFS = 1000
# Metadata file to track processed PDFs (from your VectorStore)
METADATA_FILE = "data/metadata.pkl"


def run_etl_pipeline(pdf_dir: str):
    print(f"Starting ETL process for directory: {pdf_dir}")

    # Initialize VectorStore
    vs = VectorStore()

    # Load already processed PDF names from metadata to skip them
    processed_pdfs = set()
    if Path(METADATA_FILE).exists():
        try:
            with open(METADATA_FILE, "rb") as f:
                metadata = pickle.load(f)
                processed_pdfs = {m["source"] for m in metadata}
        except Exception as e:
            print(f"Warning: Could not load metadata file: {e}")

    pdf_path = Path(pdf_dir)
    if not pdf_path.exists():
        print(f"Error: Directory {pdf_dir} does not exist.")
        return

    pdf_files = [f for f in pdf_path.glob("*.pdf") if f.name not in processed_pdfs]
    if not pdf_files:
        print("No new PDFs to process. Exiting.")
        return

    # Limit number of PDFs
    pdf_files = pdf_files[:MAX_PDFS]
    print(f"Processing {len(pdf_files)} PDF files (limit {MAX_PDFS}).")

    for i, file_path in enumerate(pdf_files):
        print(f"[{i+1}/{len(pdf_files)}] Processing {file_path.name}...")

        try:
            # 1️⃣ Extract text
            text = extract_text_from_pdf(str(file_path))
            if not text.strip():
                print("   Skipping empty PDF.")
                continue

            # 2️⃣ Chunk text
            chunks = chunk_text(text)

            texts_to_add = []
            metadatas = []

            for chunk in chunks:
                entities = extract_legal_entities(chunk)

                texts_to_add.append(chunk)

                metadatas.append({
                    "source": file_path.name,      # PDF name
                    "text": chunk,                 # REQUIRED for RAG summary
                    "ipc_sections": entities.get("ipc_sections", []),
                    "articles": entities.get("articles", []),
                    "acts": entities.get("acts", [])
                })

            # 3️⃣ Load into FAISS
            if texts_to_add:
                vs.add_texts(texts_to_add, metadatas)
                print(f"   Added {len(texts_to_add)} chunks.")

        except Exception as e:
            print(f"   Error processing {file_path.name}: {e}")

    print("ETL process completed successfully.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run ETL Pipeline for Legal PDFs")
    parser.add_argument(
        "--dir",
        type=str,
        required=True,
        help="Directory containing PDF files"
    )

    args = parser.parse_args()
    run_etl_pipeline(args.dir)
