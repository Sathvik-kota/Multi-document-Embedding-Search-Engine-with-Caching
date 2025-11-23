import json
import requests

API = "http://localhost:8000"

def run_evaluation():
    # Load generated queries
    queries = json.load(open("generated_queries.json"))

    results = []

    for item in queries:
        q = item["query"]
        expected_doc = item["doc_id"] + ".txt"

        resp = requests.post(
            f"{API}/search",
            json={"query": q, "top_k": 5}
        ).json()

        returned_doc = resp["results"][0]["filename"] if resp["results"] else None

        results.append({
            "query": q,
            "expected": expected_doc,
            "returned": returned_doc,
            "correct": returned_doc == expected_doc
        })

    # Compute accuracy
    accuracy = sum(r["correct"] for r in results) / len(results)

    # Save results for inspection
    with open("evaluation_results.json", "w") as f:
        json.dump(results, f, indent=4)

    return accuracy, results
