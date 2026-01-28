from sentence_transformers import SentenceTransformer
import sys

print("Loading model...")
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
