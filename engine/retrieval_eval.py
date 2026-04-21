from typing import List, Dict


class RetrievalEvaluator:
    def __init__(self):
        pass

    def calculate_hit_rate(
        self,
        expected_ids: List[str],
        retrieved_ids: List[str],
        top_k: int = 3
    ) -> float:
        top_retrieved = retrieved_ids[:top_k]
        hit = any(doc_id in top_retrieved for doc_id in expected_ids)
        return 1.0 if hit else 0.0

    def calculate_recall_at_k(
        self,
        expected_ids: List[str],
        retrieved_ids: List[str],
        top_k: int = 3
    ) -> float:
        """
        Recall@K = số doc đúng xuất hiện trong top-k / tổng số doc đúng kỳ vọng.
        Hữu ích đặc biệt cho multi-doc questions.
        """
        if not expected_ids:
            return 1.0 if not retrieved_ids[:top_k] else 0.0

        top_retrieved = retrieved_ids[:top_k]
        matched = len(set(expected_ids) & set(top_retrieved))
        return matched / len(set(expected_ids))

    def calculate_mrr(self, expected_ids: List[str], retrieved_ids: List[str]) -> float:
        for i, doc_id in enumerate(retrieved_ids):
            if doc_id in expected_ids:
                return 1.0 / (i + 1)
        return 0.0

    def get_rank(self, expected_ids: List[str], retrieved_ids: List[str]) -> int:
        """Return vị trí (1-indexed) của doc đúng đầu tiên, -1 nếu không có"""
        for i, doc_id in enumerate(retrieved_ids):
            if doc_id in expected_ids:
                return i + 1
        return -1

    async def evaluate_batch(self, dataset: List[Dict], top_k: int = 3) -> Dict:
        results = []

        for sample in dataset:
            expected_ids = sample.get("ground_truth_doc_ids", [])
            retrieved_ids = sample.get("retrieved_ids", [])

            hit = self.calculate_hit_rate(expected_ids, retrieved_ids, top_k=top_k)
            recall_at_k = self.calculate_recall_at_k(expected_ids, retrieved_ids, top_k=top_k)
            mrr = self.calculate_mrr(expected_ids, retrieved_ids)
            rank = self.get_rank(expected_ids, retrieved_ids)
            is_multi_doc = len(expected_ids) > 1

            results.append({
                "id": sample.get("id"),
                "query": sample.get("query"),
                "hit": hit,
                "recall_at_k": recall_at_k,
                "mrr": mrr,
                "rank": rank,
                "expected_ids": expected_ids,
                "retrieved_ids": retrieved_ids,
                "is_multi_doc": is_multi_doc,
            })

        total = len(results)
        avg_hit_rate = sum(r["hit"] for r in results) / total if total > 0 else 0.0
        avg_recall_at_k = sum(r["recall_at_k"] for r in results) / total if total > 0 else 0.0
        avg_mrr = sum(r["mrr"] for r in results) / total if total > 0 else 0.0

        hit_count = sum(r["hit"] for r in results)
        miss_count = total - hit_count

        multi_doc_results = [r for r in results if r["is_multi_doc"]]
        single_doc_results = [r for r in results if not r["is_multi_doc"]]

        def safe_avg(items, key):
            return sum(x[key] for x in items) / len(items) if items else 0.0

        breakdown = {
            "single_doc": {
                "count": len(single_doc_results),
                "avg_hit_rate": safe_avg(single_doc_results, "hit"),
                "avg_recall_at_k": safe_avg(single_doc_results, "recall_at_k"),
                "avg_mrr": safe_avg(single_doc_results, "mrr"),
            },
            "multi_doc": {
                "count": len(multi_doc_results),
                "avg_hit_rate": safe_avg(multi_doc_results, "hit"),
                "avg_recall_at_k": safe_avg(multi_doc_results, "recall_at_k"),
                "avg_mrr": safe_avg(multi_doc_results, "mrr"),
            }
        }

        return {
            "avg_hit_rate": avg_hit_rate,
            "avg_recall_at_k": avg_recall_at_k,
            "avg_mrr": avg_mrr,
            "total_samples": total,
            "hit_count": hit_count,
            "miss_count": miss_count,
            "breakdown": breakdown,
            "details": results
        }