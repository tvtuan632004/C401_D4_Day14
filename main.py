import asyncio
import json
import os
import time
from dotenv import load_dotenv

load_dotenv()

from engine.runner import BenchmarkRunner
from agent.main_agent import MainAgent
from engine.llm_judge import LLMJudge


class ExpertEvaluator:
    async def score(self, case, resp):
        # Mock retrieval metrics
        return {
            "faithfulness": 0.9,
            "relevancy": 0.8,
            "retrieval": {
                "hit_rate": 1.0,
                "mrr": 0.5
            }
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
        ExpertEvaluator(),
        LLMJudge()
    )

    results = await runner.run_all(dataset)
    total = len(results)

    avg_score = sum(r["judge"]["final_score"] for r in results) / total
    hit_rate = sum(r["ragas"]["retrieval"]["hit_rate"] for r in results) / total
    agreement_rate = sum(r["judge"]["agreement_rate"] for r in results) / total

    summary = {
        "metadata": {
            "version": agent_version,
            "agent_mode": agent_mode,
            "total": total,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        },
        "metrics": {
            "avg_score": avg_score,
            "hit_rate": hit_rate,
            "agreement_rate": agreement_rate
        }
    }

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
            "agreement_rate": v2_summary["metrics"]["agreement_rate"],
            "baseline_score": v1_summary["metrics"]["avg_score"],
            "delta_vs_baseline": delta
        }
    }

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