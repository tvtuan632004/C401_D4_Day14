from typing import Dict, Any
import os
import asyncio

from openai import AsyncOpenAI
import google.generativeai as genai


class LLMJudge:
    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.gemini_model = genai.GenerativeModel("gemini-1.5-flash")

    def _build_prompt(self, question: str, answer: str, ground_truth: str) -> str:
        return f"""
You are an AI evaluator.

Question: {question}
Ground Truth: {ground_truth}
Answer: {answer}

Score the answer from 0 to 1 based on correctness.

Return JSON:
{{
  "score": float,
  "reason": "short explanation"
}}
"""

    async def _judge_gpt(self, question: str, answer: str, ground_truth: str):
        prompt = self._build_prompt(question, answer, ground_truth)

        response = await self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        content = response.choices[0].message.content

        try:
            import json
            parsed = json.loads(content)
            return parsed["score"], parsed.get("reason", "")
        except:
            return 0.5, "Failed to parse GPT response"

    async def _judge_gemini(self, question: str, answer: str, ground_truth: str):
        prompt = self._build_prompt(question, answer, ground_truth)

        response = self.gemini_model.generate_content(prompt)

        content = response.text

        try:
            import json
            parsed = json.loads(content)
            return parsed["score"], parsed.get("reason", "")
        except:
            return 0.5, "Failed to parse Gemini response"

    async def evaluate_multi_judge(self, question: str, answer: str, ground_truth: str) -> Dict[str, Any]:

        gpt_task = self._judge_gpt(question, answer, ground_truth)
        gemini_task = self._judge_gemini(question, answer, ground_truth)

        score_a, score_b = await asyncio.gather(gpt_task, gemini_task)

        score_gpt, reason_gpt = score_a
        score_gemini, reason_gemini = score_b

        final_score = (score_gpt + score_gemini) / 2

        agreement = 1 - abs(score_gpt - score_gemini)

        if abs(score_gpt - score_gemini) > 0.3:
            final_score = min(score_gpt, score_gemini)

        return {
            "final_score": final_score,
            "agreement_rate": agreement,
            "individual_scores": {
                "gpt_4o": score_gpt,
                "gemini": score_gemini
            },
            "reasons": {
                "gpt": reason_gpt,
                "gemini": reason_gemini
            }
        }

    async def check_position_bias(self, response_a: str, response_b: str):
        return {
            "bias_detected": False,
            "note": "Not implemented"
        }