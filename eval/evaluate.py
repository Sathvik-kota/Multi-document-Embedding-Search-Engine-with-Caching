import json
import requests
import numpy as np
from sklearn.metrics import precision_score, recall_score

API_URL = "http://localhost:8000/search"


# -----------------------------
# Utility: Compute MRR
# -----------------------------
def compute_mrr(all_ranks):
    if not all_ranks:
        return 0.0
    rr = [1.0 / r for r in all_ranks]
    return float(np.mean(rr))


# -----------------------------
# Utility: Compute NDCG@K
# -----------------------------
def compute_ndcg(results, k):
    dcg = 0
    for rank, rel in enumerate(results[:k], start=1):
        if rel == 1:
            dcg += 1 / np.log2(rank + 1)
    ideal = 1  # only 1 relevant doc
    idcg = 1 / np.log2(1 + 1)
    return dcg / idcg if idcg != 0 else 0


# -----------------------------
# Main Evaluation
# -----------------------------
def run_evaluation(top_k=5, query_file="generated_queries.json"):

    with open(query_file) as f:
        queries = json.load(f)

    correct = []
    ranks = []
    ndcg_scores = []
    detailed = []

    for item in queries:
        q = item["query"]
        expected = item["doc_id"] + ".txt"  # expected filename

        resp = requests.post(API_URL, json={"query": q, "top_k": top_k})
        if resp.status_code != 200:
            continue

        data = resp.json().get("results", [])

        # extract returned filenames
        retrieved = [r["filename"] for r in data]

        # relevance array for NDCG
        relevance = [1 if filename == expected else 0 for filename in retrieved]

        # 1) ACCURACY @ top-k
        hit = expected in retrieved
        correct.append(1 if hit else 0)

        # 2) RANK for MRR
        if hit:
            rank_pos = retrieved.index(expected) + 1
            ranks.append(rank_pos)

        # 3) NDCG
        ndcg_scores.append(compute_ndcg(relevance, top_k))

        # 4) Record details
        detailed.append({
            "query": q,
            "expected": expected,
            "retrieved": retrieved,
            "is_correct": hit,
            "rank": retrieved.index(expected) + 1 if hit else None
        })

    # -----------------------------
    # METRICS
    # -----------------------------
    accuracy = np.mean(correct) * 100
    mrr = compute_mrr(ranks)
    mean_ndcg = float(np.mean(ndcg_scores))

    return {
        "accuracy": round(accuracy, 2),
        "mrr": round(mrr, 4),
        "ndcg": round(mean_ndcg, 4),
        "total_queries": len(queries),
        "correct_count": sum(correct),
        "incorrect_count": len(queries) - sum(correct),
        "details": detailed
    }
