import json
import requests
import numpy as np


API_URL = "http://localhost:8000/search"

# =====================================================
# Utility: MRR
# =====================================================
def compute_mrr(all_ranks):
    if not all_ranks:
        return 0.0
    rr = [1.0 / r for r in all_ranks]
    return float(np.mean(rr))


# =====================================================
# Utility: NDCG@K
# =====================================================
def compute_ndcg(results, k):
    """results = [1,0,0...] relevance for retrieved docs"""
    dcg = 0
    for rank, rel in enumerate(results[:k], start=1):
        if rel == 1:
            dcg += 1 / np.log2(rank + 1)

    idcg = 1 / np.log2(1 + 1)  # ideal rank = 1
    return dcg / idcg if idcg != 0 else 0


# =====================================================
# MAIN EVALUATION FUNCTION
# =====================================================
def run_evaluation(query_file="generated_queries.json", top_k=10):
    """
    top_k is FIXED = 10 for a realistic evaluation.
    """

    with open(query_file) as f:
        queries = json.load(f)

    correct = []
    ranks = []
    ndcg_scores = []
    detailed = []

    for item in queries:
        query = item["query"]
        expected = item["doc_id"] + ".txt"

        # ----------------------------
        # CALL API
        # ----------------------------
        resp = requests.post(API_URL, json={"query": query, "top_k": top_k})
        if resp.status_code != 200:
            continue

        results = resp.json().get("results", [])
        retrieved = [r["filename"] for r in results]

        # relevance array for NDCG
        relevance = [1 if fn == expected else 0 for fn in retrieved]

        # ----------------------------
        # ACCURACY
        # ----------------------------
        hit = expected in retrieved
        correct.append(1 if hit else 0)

        # ----------------------------
        # RANK for MRR
        # ----------------------------
        if hit:
            rank_position = retrieved.index(expected) + 1
            ranks.append(rank_position)
        else:
            rank_position = None

        # ----------------------------
        # NDCG
        # ----------------------------
        ndcg_scores.append(compute_ndcg(relevance, top_k))

        # ----------------------------
        # Save detail
        # ----------------------------
        detailed.append({
            "query": query,
            "expected": expected,
            "retrieved": retrieved,
            "rank": rank_position,
            "is_correct": hit
        })

    # =====================================================
    # FINAL METRICS
    # =====================================================
    accuracy = round(np.mean(correct) * 100, 2)
    mrr = round(compute_mrr(ranks), 4)
    mean_ndcg = round(float(np.mean(ndcg_scores)), 4)

    summary = {
        "accuracy": accuracy,
        "mrr": mrr,
        "ndcg": mean_ndcg,
        "total_queries": len(queries),
        "correct_count": sum(correct),
        "incorrect_count": len(queries) - sum(correct),
        "details": detailed
    }

    return summary
