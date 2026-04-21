from typing import Dict, Any

class LLMJudge:
    def __init__(self, model: str = "multi-judge"):
        self.model = model

    def _score_answer(self, answer: str, ground_truth: str) -> int:
        answer_lower = answer.lower().strip()
        gt_lower = ground_truth.lower().strip()

        if answer_lower == gt_lower:
            return 5

        gt_words = [w for w in gt_lower.split() if len(w) > 2]
        overlap = sum(1 for w in gt_words if w in answer_lower)
        ratio = overlap / max(len(gt_words), 1)

        if ratio >= 0.75:
            return 5
        if ratio >= 0.55:
            return 4
        if ratio >= 0.35:
            return 3
        if ratio >= 0.15:
            return 2
        return 1

    async def evaluate_multi_judge(self, question: str, answer: str, ground_truth: str) -> Dict[str, Any]:
        score_a = self._score_answer(answer, ground_truth)
        score_b = self._score_answer(answer, ground_truth)

        final_score = (score_a + score_b) / 2
        agreement = 1.0 if score_a == score_b else 0.8

        return {
            "final_score": final_score,
            "agreement_rate": agreement,
            "individual_scores": {
                "judge_model_a": score_a,
                "judge_model_b": score_b
            },
            "reasoning": "Điểm được tính dựa trên mức độ khớp giữa câu trả lời và ground truth."
        }

    async def check_position_bias(self, response_a: str, response_b: str):
        return {
            "bias_detected": False,
            "note": "Mock check"
        }