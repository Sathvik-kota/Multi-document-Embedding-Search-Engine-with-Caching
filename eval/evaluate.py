# eval/evaluate.py
import json
import requests

API_GATEWAY_URL = "http://localhost:8000"

def run_evaluation(top_k: int = 1):
    # 1) Load generated queries
    with open("generated_queries.json", "r") as f:
        items = json.load(f)

    total = len(items)
    correct = 0
    records = []  # store ALL results

    for item in items:
        doc_id = item["doc_id"]          # e.g. "doc_001"
        query = item["query"]
        expected_fname = f"{doc_id}.txt" # "doc_001.txt"

        try:
            resp = requests.post(
                f"{API_GATEWAY_URL}/search",
                json={"query": query, "top_k": top_k},
                timeout=20
            )
        except Exception as e:
            print(f"❌ Request failed for query: {query} | {e}")
            continue

        if resp.status_code != 200:
            print(f"❌ API error ({resp.status_code}): {resp.text}")
            continue

        data = resp.json()
        if "results" not in data or len(data["results"]) == 0:
            returned_fname = None
            score = None
        else:
            top_hit = data["results"][0]
            returned_fname = top_hit["filename"]
            score = top_hit.get("score", None)

        is_correct = (returned_fname == expected_fname)
        if is_correct:
            correct += 1

        records.append({
            "query": query,
            "expected": expected_fname,
            "returned": returned_fname,
            "score": score,
            "correct": is_correct
        })

    # ---- Metrics ----
    accuracy = correct / total if total > 0 else 0.0

    # With 1 prediction per query, precision@1 = recall@1 = accuracy
    precision_at_1 = accuracy
    recall_at_1 = accuracy
    f1_at_1 = (2 * precision_at_1 * recall_at_1 / (precision_at_1 + recall_at_1)
               if (precision_at_1 + recall_at_1) > 0 else 0.0)

    summary = {
        "total": total,
        "correct": correct,
        "accuracy": accuracy,
        "precision_at_1": precision_at_1,
        "recall_at_1": recall_at_1,
        "f1_at_1": f1_at_1,
        "records": records,
    }

    return summary
