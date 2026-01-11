import numpy as np
from sentence_transformers import SentenceTransformer

# Load model once (important for performance)
model = SentenceTransformer("paraphrase-MiniLM-L12-v2")



# Cosine Similarity

def cosine_sim(v1, v2) -> float:
    """
    Computes cosine similarity between two normalized vectors
    """
    return float(np.dot(v1, v2))



# Embedding Generator

def generate_embeddings(issue_text: str, address_text: str):
    """
    Generates normalized embeddings for:
    1. Complaint issue/description
    2. Complaint address
    """
    issue_emb, address_emb = model.encode(
        [issue_text, address_text],
        normalize_embeddings=True
    )
    return issue_emb, address_emb



# Similarity Checker

def is_similar(
    new_issue_emb,
    new_address_emb,
    old_issue_emb,
    old_address_emb,
    threshold: float = 0.60,
    issue_weight: float = 0.7,
    address_weight: float = 0.3
) -> bool:
    """
    Checks whether two complaints are similar using
    weighted similarity of issue + address embeddings
    """

    issue_similarity = cosine_sim(new_issue_emb, old_issue_emb)
    address_similarity = cosine_sim(new_address_emb, old_address_emb)

    final_similarity = (
        issue_weight * issue_similarity
        + address_weight * address_similarity
    )

    return final_similarity >= threshold
