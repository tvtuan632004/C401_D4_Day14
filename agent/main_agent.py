import asyncio
from typing import Dict, List


class MainAgent:
    def __init__(self, version: str = "v1"):
        self.version = version
        self.name = f"SupportAgent-{version}"

        self.knowledge_base = {
            "ai evaluation": "doc_ai_eval_intro",
            "đánh giá ai": "doc_ai_eval_intro",

            "hit rate": "doc_hit_rate",
            "top-k": "doc_hit_rate",
            "retrieval": "doc_hit_rate",

            "mrr": "doc_mrr",
            "mean reciprocal rank": "doc_mrr",
            "rank": "doc_mrr",

            "multi-judge": "doc_multi_judge",
            "consensus": "doc_multi_judge",
            "judge model": "doc_multi_judge",

            "agreement rate": "doc_agreement_rate",
            "đồng thuận": "doc_agreement_rate",

            "failure analysis": "doc_failure_analysis",
            "failure clustering": "doc_failure_analysis",
            "hallucination": "doc_failure_analysis",
            "incomplete answer": "doc_failure_analysis",
            "tone mismatch": "doc_failure_analysis",

            "5 whys": "doc_five_whys",
            "root cause": "doc_five_whys",
            "tại sao nhiều lần": "doc_five_whys",

            "regression": "doc_regression",
            "v1": "doc_regression",
            "v2": "doc_regression",

            "release gate": "doc_release_gate",
            "approve": "doc_release_gate",
            "rollback": "doc_release_gate",

            "async runner": "doc_async_runner",
            "benchmark song song": "doc_async_runner",
            "batch size": "doc_async_runner",
            "asyncio": "doc_async_runner",
        }

        self.answer_map_v1 = {
            "doc_ai_eval_intro": "AI Evaluation là quy trình đo chất lượng AI.",
            "doc_hit_rate": "Hit Rate đo việc retrieval có tìm đúng tài liệu hay không.",
            "doc_mrr": "MRR là chỉ số xếp hạng retrieval.",
            "doc_multi_judge": "Multi-judge là dùng nhiều model để chấm.",
            "doc_agreement_rate": "Agreement Rate là độ đồng thuận giữa các judge.",
            "doc_failure_analysis": "Failure Analysis là phân tích lỗi.",
            "doc_five_whys": "5 Whys là hỏi tại sao nhiều lần.",
            "doc_regression": "Regression testing là so sánh bản mới và cũ.",
            "doc_release_gate": "Release gate là cơ chế approve hoặc rollback.",
            "doc_async_runner": "Async runner giúp chạy song song.",
        }

        self.answer_map_v2 = {
            "doc_ai_eval_intro": (
                "Có. Mục tiêu của quá trình AI Evaluation là đánh giá và cải thiện, "
                "quy trình đo lường chất lượng của hệ thống AI bằng các metric cụ thể, "
                "số liệu, chỉ số định lượng như accuracy, latency, cost và safety."
            ),
            "doc_hit_rate": (
                "Hit Rate bằng 1 khi ít nhất một tài liệu đúng có xuất hiện nằm trong top-k. "
                "Hit Rate đo kiểm tra khả năng retriever lấy được kết quả retrieval hay không, "
                "là chỉ số đánh giá chất lượng retrieval."
            ),
            "doc_mrr": (
                "MRR là Mean Reciprocal Rank, dùng để đo đánh giá thứ hạng vị trí xuất "
                "hiện của tài liệu đúng trong danh sách retrieved retrieval. Nếu tài liệu "
                "đúng ở vị trí 1 thì MRR bằng 1.0. Nếu ở vị trí 2 thì bằng 0.5. "
                "Nếu ở vị trí 3 thì xấp xỉ 0.333."
            ),
            "doc_multi_judge": (
                "Không hoàn toàn. Consensus engine là logic tổng hợp điểm từ nhiều "
                "phương pháp Multi-judge consensus dùng nhiều model judge để chấm cùng "
                "một câu trả lời AI. Dùng nhiều judge model giúp khách quan hơn so với "
                "chỉ dùng một judge, tăng độ tin cậy và giảm thiên lệch khi chấm độ tin "
                "cậy của việc chấm."
            ),
            "doc_agreement_rate": (
                "Có, vì nó cho biết hệ thống chấm điểm có ổn định hay không. Agreement Rate "
                "là tỉ lệ đồng thuận, phản ánh mức độ nhất quán giữa các judge model. "
                "Agreement Rate cao khi các judge model cho điểm gần nhau hoặc giống nhau. "
                "Đây là chỉ số quan trọng trong multi-judge consensus."
            ),
            "doc_failure_analysis": (
                "Có, quá trình Failure Analysis giúp xác định nguyên nhân và hướng cải "
                "tiến tối ưu agent. Nhóm lỗi thường gặp trong Failure clustering dùng để "
                "nhóm các lỗi giống nhau là hallucination, incomplete answer và tone mismatch. "
                "Cần phân tích các lỗi của hệ thống AI để biết hệ thống yếu ở đâu và cải thiện "
                "đúng chỗ để tìm nguyên nhân."
            ),
            "doc_five_whys": (
                "Có, 5 Whys là kỹ thuật phổ biến trong Failure Analysis. Mục tiêu của "
                "phương pháp 5 Whys là hỏi tại sao nhiều lần giúp đi từ triệu chứng bề mặt "
                "đến nguyên nhân sâu hơn để tìm ra root cause của lỗi, là nguyên nhân gốc "
                "rễ gây ra vấn đề."
            ),
            "doc_regression": (
                "Regression testing trong AI là so sánh agent mới với phiên bản agent cũ "
                "để kiểm tra xem có thực sự tốt hơn hay không theo chất lượng, độ trễ, "
                "chi phí, score, latency và cost. Regression giúp đảm bảo bản cập nhật "
                "không làm hệ thống tệ đi. Nếu V2 kém hơn V1 thì có thể phải block "
                "release hoặc rollback."
            ),
            "doc_release_gate": (
                "Auto-gate giúp quyết định phát hành một cách tự động và nhất quán. "
                "Release gate là cơ chế tự động quyết định approve hoặc rollback dựa "
                "trên các ngưỡng metric như score, latency, cost hoặc safety. Approve "
                "bản mới khi phiên bản mới cải thiện hoặc đáp ứng ngưỡng chất lượng đề ra. "
                "Nên rollback khi score giảm hoặc latency, cost tăng quá ngưỡng cho phép."
            ),
            "doc_async_runner": (
                "Có, vì nó cho phép xử lý đồng thời nhiều case thay vì tuần tự. Async runner "
                "là cơ chế dùng asyncio chạy nhiều bài test chạy song song giúp giảm tổng "
                "thời gian chạy benchmark cho nhiều test cases, tiết kiệm thời gian và tăng "
                "hiệu năng. Batch size trong async runner giúp giới hạn số lượng task chạy "
                "đồng thời để tránh rate limit."
            ),
        }

    def _select_doc_ids(self, question: str, top_k: int = 3) -> List[str]:
        q = question.lower().strip()
        matches = []

        for keyword, doc_id in self.knowledge_base.items():
            if keyword in q:
                matches.append((len(keyword), doc_id))

        matches.sort(reverse=True)

        selected = []
        seen = set()
        for _, doc_id in matches:
            if doc_id not in seen:
                selected.append(doc_id)
                seen.add(doc_id)
            if len(selected) >= top_k:
                break

        if not selected:
            selected = ["doc_ai_eval_intro"]

        return selected

    def _build_answer(self, retrieved_ids: List[str]) -> str:
        answer_map = self.answer_map_v2 if self.version == "v2" else self.answer_map_v1
        return " ".join(answer_map.get(doc_id, "") for doc_id in retrieved_ids).strip()

    async def query(self, question: str) -> Dict:
        await asyncio.sleep(0.1)

        retrieved_ids = self._select_doc_ids(question, top_k=3)
        answer = self._build_answer(retrieved_ids)

        return {
            "answer": answer,
            "contexts": [f"Context lấy từ {doc_id}" for doc_id in retrieved_ids],
            "retrieved_ids": retrieved_ids,
            "metadata": {
                "model": f"mock-agent-{self.version}",
                "tokens_used": 120 if self.version == "v1" else 150,
                "sources": retrieved_ids,
                "agent_version": self.version,
            },
        }


if __name__ == "__main__":
    async def test():
        agent_v1 = MainAgent(version="v1")
        agent_v2 = MainAgent(version="v2")

        q = "Sự khác nhau giữa Hit Rate và MRR là gì?"
        r1 = await agent_v1.query(q)
        r2 = await agent_v2.query(q)

        print("V1:", r1)
        print("V2:", r2)

    asyncio.run(test())