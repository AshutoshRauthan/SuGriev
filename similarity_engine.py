import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("paraphrase-MiniLM-L12-v2")


def cosine_sim(v1, v2):
    return np.dot(v1, v2)

def are_similar(c1, c2, threshold=0.60):
    # Step 1: Pincode check
    if c1["pincode"] != c2["pincode"]:
        return False

    # Step 2: Issue similarity
    issue_emb = model.encode(
        [c1["issue_text"], c2["issue_text"]],
        normalize_embeddings=True
    )
    issue_sim = cosine_sim(issue_emb[0], issue_emb[1])

    # Step 3: Address similarity
    addr_emb = model.encode(
        [c1["address"], c2["address"]],
        normalize_embeddings=True
    )
    addr_sim = cosine_sim(addr_emb[0], addr_emb[1])

    # Step 4: Weighted similarity
    final_sim = (0.7 * issue_sim) + (0.3 * addr_sim)

    print(f"Issue similarity: {issue_sim:.2f}")
    print(f"Address similarity: {addr_sim:.2f}")
    print(f"Final similarity: {final_sim:.2f}")

    return final_sim >= threshold

c1 = {
    "issue_text": "Garbage pile near govt school",
    "address": "Govt High School, JP Nagar",
    "pincode": "560078"
}

c2 = {
    "issue_text": "Waste dumping outside government school",
    "address": "Near Government High School, J.P. Nagar",
    "pincode": "560078"
}
# Expected: True
print(are_similar(c1, c2))
# another exampel for test 
'''
c1 = {
    "issue_text": "Illegal parking on roadside",
    "address": "Ring Road",
    "pincode": "302015"
}

c2 = {
    "issue_text": "Water leakage from overhead tank",
    "address": "Ring Road",
    "pincode": "302015"
}
# Expected: False
'''