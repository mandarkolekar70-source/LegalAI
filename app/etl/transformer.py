import re
from typing import List, Dict

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Splits text into chunks with overlap.
    """
    if not text:
        return []
    
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def extract_legal_entities(text: str) -> Dict[str, List[str]]:
    """
    Extracts IPC sections, Articles, and Acts using Regex.
    """
    entities = {
        "ipc_sections": [],
        "articles": [],
        "acts": []
    }
    
    # IPC Sections patterns
    ipc_pattern = r"(Section\s+\d+\s+of\s+(?:the\s+)?IPC|IPC\s+Section\s+\d+|Section\s+\d+\s+Indian\s+Penal\s+Code)"
    entities["ipc_sections"] = list(set(re.findall(ipc_pattern, text, re.IGNORECASE)))
    
    # Constitution Articles
    article_pattern = r"(Article\s+\d+\s+of\s+(?:the\s+)?Constitution)"
    entities["articles"] = list(set(re.findall(article_pattern, text, re.IGNORECASE)))
    
    # Acts (Basic pattern: Name Act, Year)
    act_pattern = r"([A-Z][a-zA-Z\s]+Act,\s+\d{4})"
    entities["acts"] = list(set(re.findall(act_pattern, text)))

    return entities
