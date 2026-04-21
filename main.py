import asyncio
import json
import os
import time
from dotenv import load_dotenv

load_dotenv()

from engine.runner import BenchmarkRunner
from agent.main_agent import MainAgent
from engine.llm_judge import LLMJudge
from engine.retrieval_eval import RetrievalEvaluator


class ExpertEvaluator:
    def __init__(self, top_k: int = 3):
        self.retrieval_evaluator = RetrievalEvaluator()
        self.top_k = top_k

    def _extract_retrieved_ids(self, resp):
        if not isinstance(resp, dict):
            return []

        if "retrieved_ids" in resp and isinstance(resp["retrieved_ids"], list):
            return resp["retrieved_ids"]

        for key in ["documents", "context_docs", "contexts", "sources"]:
            if key in resp and isinstance(resp[key], list):
                extracted = []
                for item in resp[key]:
                    if isinstance(item, str):
                        extracted.append(item)
                    elif isinstance(item, dict):
                        doc_id = item.get("doc_id") or item.get("id") or item.get("source_id")
                        if doc_id:
                            extracted.append(doc_id)
                if extracted:
                    return extracted

        return []

    async def score(self, case, resp):
        expected_ids = case.get("ground_truth_doc_ids", [])
        retrieved_ids = self._extract_retrieved_ids(resp)

        retrieval_result = await self.retrieval_evaluator.evaluate_batch(
            [
                {
                    "id": case.get("id"),
                    "query": case.get("question", ""),
                    "ground_truth_doc_ids": expected_ids,
                    "retrieved_ids": retrieved_ids,
                }
            ],
            top_k=self.top_k
        )

        detail = retrieval_result["details"][0] if retrieval_result["details"] else {}

        retrieval_metrics = {
            "hit_rate": detail.get("hit", 0.0),
            "mrr": detail.get("mrr", 0.0),
            "rank": detail.get("rank", -1),
            "expected_ids": detail.get("expected_ids", expected_ids),
            "retrieved_ids": detail.get("retrieved_ids", retrieved_ids),
            "recall_at_k": detail.get("recall_at_k", 0.0),
            "is_multi_doc": detail.get("is_multi_doc", False),
        }

        return {
            "faithfulness": 0.9,
            "relevancy": 0.8,
            "retrieval": retrieval_metrics,
        }


async def run_benchmark_with_results(agent_version: str):
    print(f"🚀 Khởi động Benchmark cho {agent_version}...")

    if not os.path.exists("data/golden_set.jsonl"):
        print("❌ Thiếu data/golden_set.jsonl. Hãy chạy 'python data/synthetic_gen.py' trước.")
        return None, None

    with open("data/golden_set.jsonl", "r", encoding="utf-8") as f:
        dataset = [json.loads(line) for line in f if line.strip()]

    if not dataset:
        print("❌ File data/golden_set.jsonl rỗng. Hãy tạo ít nhất 1 test case.")
        return None, None

    agent_mode = "v2" if "V2" in agent_version else "v1"

    runner = BenchmarkRunner(
        MainAgent(version=agent_mode),
        ExpertEvaluator(top_k=3),
        LLMJudge()
    )

    results = await runner.run_all(dataset)
    total = len(results)

    if total == 0:
        print("❌ Không có kết quả benchmark.")
        return None, None

    avg_score = sum(r["judge"]["final_score"] for r in results) / total
    avg_hit_rate = sum(r["ragas"]["retrieval"].get("hit_rate", 0.0) for r in results) / total
    avg_mrr = sum(r["ragas"]["retrieval"].get("mrr", 0.0) for r in results) / total
    agreement_rate = sum(r["judge"]["agreement_rate"] for r in results) / total
    avg_latency = sum(r.get("latency", 0.0) for r in results) / total

    has_recall = any("recall_at_k" in r["ragas"]["retrieval"] for r in results)
    avg_recall_at_k = (
        sum(r["ragas"]["retrieval"].get("recall_at_k", 0.0) for r in results) / total
        if has_recall else None
    )

    pass_count = sum(1 for r in results if r.get("status") == "pass")
    fail_count = total - pass_count

    summary = {
        "metadata": {
            "version": agent_version,
            "agent_mode": agent_mode,
            "total": total,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        },
        "metrics": {
            "avg_score": avg_score,
            "hit_rate": avg_hit_rate,
            "mrr": avg_mrr,
            "agreement_rate": agreement_rate,
            "avg_latency_sec": avg_latency,
            "pass_count": pass_count,
            "fail_count": fail_count,
        }
    }

    if avg_recall_at_k is not None:
        summary["metrics"]["recall_at_k"] = avg_recall_at_k

    return results, summary


async def run_benchmark(version: str):
    _, summary = await run_benchmark_with_results(version)
    return summary


async def main():
    v1_results, v1_summary = await run_benchmark_with_results("Agent_V1_Base")
    v2_results, v2_summary = await run_benchmark_with_results("Agent_V2_Optimized")

    if not v1_summary or not v2_summary:
        print("❌ Không thể chạy Benchmark. Kiểm tra lại data/golden_set.jsonl.")
        return

    print("\n📊 --- KẾT QUẢ SO SÁNH (REGRESSION) ---")
    delta = v2_summary["metrics"]["avg_score"] - v1_summary["metrics"]["avg_score"]

    print(f"V1 Score: {v1_summary['metrics']['avg_score']:.2f}")
    print(f"V2 Score: {v2_summary['metrics']['avg_score']:.2f}")
    print(f"Delta: {'+' if delta >= 0 else ''}{delta:.2f}")

    print(f"V1 Hit Rate: {v1_summary['metrics']['hit_rate']:.2f}")
    print(f"V2 Hit Rate: {v2_summary['metrics']['hit_rate']:.2f}")

    print(f"V1 MRR: {v1_summary['metrics']['mrr']:.2f}")
    print(f"V2 MRR: {v2_summary['metrics']['mrr']:.2f}")

    if "recall_at_k" in v1_summary["metrics"] and "recall_at_k" in v2_summary["metrics"]:
        print(f"V1 Recall@K: {v1_summary['metrics']['recall_at_k']:.2f}")
        print(f"V2 Recall@K: {v2_summary['metrics']['recall_at_k']:.2f}")

    os.makedirs("reports", exist_ok=True)

    final_summary = {
        "metadata": {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "mode": "regression",
            "versions_compared": [
                v1_summary["metadata"]["version"],
                v2_summary["metadata"]["version"]
            ]
        },
        "metrics": {
            "avg_score": v2_summary["metrics"]["avg_score"],
            "hit_rate": v2_summary["metrics"]["hit_rate"],
            "mrr": v2_summary["metrics"]["mrr"],
            "agreement_rate": v2_summary["metrics"]["agreement_rate"],
            "avg_latency_sec": v2_summary["metrics"]["avg_latency_sec"],
            "baseline_score": v1_summary["metrics"]["avg_score"],
            "baseline_hit_rate": v1_summary["metrics"]["hit_rate"],
            "baseline_mrr": v1_summary["metrics"]["mrr"],
            "delta_vs_baseline": delta
        }
    }

    if "recall_at_k" in v2_summary["metrics"]:
        final_summary["metrics"]["recall_at_k"] = v2_summary["metrics"]["recall_at_k"]
    if "recall_at_k" in v1_summary["metrics"]:
        final_summary["metrics"]["baseline_recall_at_k"] = v1_summary["metrics"]["recall_at_k"]

    with open("reports/summary.json", "w", encoding="utf-8") as f:
        json.dump(final_summary, f, ensure_ascii=False, indent=2)

    with open("reports/benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "baseline": {
                    "summary": v1_summary,
                    "results": v1_results
                },
                "candidate": {
                    "summary": v2_summary,
                    "results": v2_results
                }
            },
            f,
            ensure_ascii=False,
            indent=2
        )

    if delta >= 0 and v2_summary["metrics"]["agreement_rate"] >= 0.6:
        print("✅ QUYẾT ĐỊNH: CHẤP NHẬN BẢN CẬP NHẬT (APPROVE)")
    else:
        print("❌ QUYẾT ĐỊNH: TỪ CHỐI (BLOCK RELEASE)")


if __name__ == "__main__":
    asyncio.run(main())