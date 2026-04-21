from typing import List, Dict

class RetrievalEvaluator:
    def __init__(self):
        pass

    def calculate_hit_rate(self, expected_ids: List[str], retrieved_ids: List[str], top_k: int = 3) -> float:
        top_retrieved = retrieved_ids[:top_k]
        hit = any(doc_id in top_retrieved for doc_id in expected_ids)
        return 1.0 if hit else 0.0

    def calculate_mrr(self, expected_ids: List[str], retrieved_ids: List[str]) -> float:
        for i, doc_id in enumerate(retrieved_ids):
            if doc_id in expected_ids:
                return 1.0 / (i + 1)
        return 0.0

    def get_rank(self, expected_ids: List[str], retrieved_ids: List[str]) -> int:
        """Return vị trí (1-indexed) của doc đúng, -1 nếu không có"""
        for i, doc_id in enumerate(retrieved_ids):
            if doc_id in expected_ids:
                return i + 1
        return -1

    async def evaluate_batch(self, dataset: List[Dict]) -> Dict:
        results = []

        for sample in dataset:
            expected_ids = sample.get("ground_truth_doc_ids", [])
            retrieved_ids = sample.get("retrieved_ids", [])

            hit = self.calculate_hit_rate(expected_ids, retrieved_ids)
            mrr = self.calculate_mrr(expected_ids, retrieved_ids)
            rank = self.get_rank(expected_ids, retrieved_ids)

            results.append({
                "id": sample.get("id"),
                "query": sample.get("query"),
                "hit": hit,
                "mrr": mrr,
                "rank": rank,
                "expected_ids": expected_ids,
                "retrieved_ids": retrieved_ids
            })

        # aggregate metrics
        total = len(results)
        avg_hit_rate = sum(r["hit"] for r in results) / total if total > 0 else 0
        avg_mrr = sum(r["mrr"] for r in results) / total if total > 0 else 0

        hit_count = sum(r["hit"] for r in results)
        miss_count = total - hit_count

        return {
            "avg_hit_rate": avg_hit_rate,
            "avg_mrr": avg_mrr,
            "total_samples": total,
            "hit_count": hit_count,
            "miss_count": miss_count,
            "details": results  
        }