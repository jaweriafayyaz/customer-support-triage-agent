import csv
import time
from run_test_set import TEST_TICKETS
from pipeline import run_pipeline

EXPECTED = {
    "T-1": "Billing", "T-2": "Technical", "T-3": "Refund", "T-4": "Shipping",
    "T-5": "General", "T-6": "Refund", "T-7": "Refund", "T-8": "Unroutable",
    "T-9": "Shipping", "T-10": "Unroutable",
}


def run_eval(results_csv_path="results_after_day4.csv"):
    import os
    if os.path.exists(results_csv_path):
        os.remove(results_csv_path)

    rows = []
    total_latency = 0.0

    for ticket in TEST_TICKETS:
        start = time.perf_counter()
        result = run_pipeline(**ticket)
        elapsed = time.perf_counter() - start
        total_latency += elapsed

        expected = EXPECTED[ticket["ticket_id"]]
        correct = result.category == expected
        rows.append({
            "ticket_id": result.ticket_id, "expected": expected, "actual": result.category,
            "correct": correct, "confidence": result.confidence, "action": result.action,
            "latency_sec": round(elapsed, 4),
        })

    with open(results_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    accuracy = sum(r["correct"] for r in rows) / len(rows)
    manual_touch_rate = sum(1 for r in rows if r["action"] == "needs_human_review") / len(rows)
    avg_latency = total_latency / len(rows)

    print(f"{'Ticket':<8}{'Expected':<12}{'Actual':<12}{'Correct':<9}{'Action'}")
    for r in rows:
        print(f"{r['ticket_id']:<8}{r['expected']:<12}{r['actual']:<12}{str(r['correct']):<9}{r['action']}")

    print(f"\nAccuracy: {accuracy:.0%} ({sum(r['correct'] for r in rows)}/{len(rows)})")
    print(f"Manual-touch rate: {manual_touch_rate:.0%}")
    print(f"Avg latency per ticket: {avg_latency*1000:.2f} ms")

    return rows, accuracy, manual_touch_rate, avg_latency


if __name__ == "__main__":
    run_eval()