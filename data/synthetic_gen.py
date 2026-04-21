import json
import asyncio
import os
from typing import List, Dict

TOPICS = [
    {
        "doc_id": "doc_ai_eval_intro",
        "text": "AI Evaluation là quy trình đo lường chất lượng của hệ thống AI bằng các chỉ số định lượng như accuracy, latency, cost và safety."
    },
    {
        "doc_id": "doc_hit_rate",
        "text": "Hit Rate dùng để đo xem tài liệu đúng có xuất hiện trong top-k kết quả retrieval hay không."
    },
    {
        "doc_id": "doc_mrr",
        "text": "MRR là Mean Reciprocal Rank. Nếu tài liệu đúng đứng ở vị trí đầu tiên thì điểm là 1.0, vị trí thứ hai là 0.5, vị trí thứ ba là 0.333."
    },
    {
        "doc_id": "doc_multi_judge",
        "text": "Multi-judge consensus là phương pháp dùng nhiều model giám khảo để chấm một câu trả lời nhằm tăng độ tin cậy."
    },
    {
        "doc_id": "doc_agreement_rate",
        "text": "Agreement Rate là tỉ lệ đồng thuận giữa các judge model. Nếu các model cho điểm gần nhau thì agreement rate cao."
    },
    {
        "doc_id": "doc_failure_analysis",
        "text": "Failure Analysis giúp phân nhóm lỗi như hallucination, incomplete answer và tone mismatch để tìm nguyên nhân gốc rễ."
    },
    {
        "doc_id": "doc_five_whys",
        "text": "Phương pháp 5 Whys đào sâu nguyên nhân lỗi bằng cách hỏi tại sao nhiều lần cho đến khi tìm ra root cause."
    },
    {
        "doc_id": "doc_regression",
        "text": "Regression testing trong AI dùng để so sánh phiên bản agent mới với phiên bản cũ dựa trên score, latency và cost."
    },
    {
        "doc_id": "doc_release_gate",
        "text": "Release gate là cơ chế tự động quyết định approve hoặc rollback dựa trên các ngưỡng chất lượng."
    },
    {
        "doc_id": "doc_async_runner",
        "text": "Async runner giúp chạy benchmark song song để giảm thời gian đánh giá cho nhiều test cases."
    },
]

QUESTION_TEMPLATES = [
    "AI Evaluation là gì?",
    "Hit Rate dùng để đo điều gì?",
    "MRR là gì?",
    "Multi-judge consensus là gì?",
    "Agreement Rate là gì?",
    "Failure Analysis có vai trò gì?",
    "5 Whys dùng để làm gì?",
    "Regression testing trong AI là gì?",
    "Release gate là gì?",
    "Async runner có tác dụng gì?"
]

def build_cases() -> List[Dict]:
    cases = []
    case_id = 0

    mapping = {
        "doc_ai_eval_intro": [
            ("AI Evaluation là gì?", "AI Evaluation là quy trình đo lường chất lượng hệ thống AI bằng các chỉ số như accuracy, latency, cost và safety."),
            ("AI Evaluation đo những gì?", "AI Evaluation đo chất lượng AI bằng các chỉ số định lượng như accuracy, latency, cost và safety."),
            ("Mục tiêu của AI Evaluation là gì?", "Mục tiêu của AI Evaluation là đánh giá và cải thiện chất lượng hệ thống AI bằng số liệu."),
            ("AI Evaluation có phải là đo chất lượng AI không?", "Có. AI Evaluation là quy trình đo lường chất lượng của hệ thống AI."),
            ("Hãy giải thích ngắn gọn AI Evaluation.", "AI Evaluation là quá trình đánh giá hệ thống AI bằng các metric cụ thể.")
        ],
        "doc_hit_rate": [
            ("Hit Rate là gì?", "Hit Rate đo xem tài liệu đúng có xuất hiện trong top-k kết quả retrieval hay không."),
            ("Hit Rate dùng để đo điều gì?", "Hit Rate đo khả năng retriever lấy được tài liệu đúng trong top-k."),
            ("Khi nào Hit Rate bằng 1?", "Hit Rate bằng 1 khi ít nhất một tài liệu đúng xuất hiện trong top-k."),
            ("Hit Rate có hạn chế gì so với MRR?", "Hit Rate không phản ánh vị trí của tài liệu đúng, trong khi MRR có."),
            ("Nếu Hit Rate cao nhưng user vẫn không hài lòng, vấn đề có thể là gì?", "Có thể tài liệu đúng không nằm ở vị trí cao hoặc câu trả lời chưa tốt.")
        ],
        "doc_mrr": [
            ("MRR là gì?", "MRR là Mean Reciprocal Rank, dùng để đo thứ hạng của tài liệu đúng."),
            ("Nếu tài liệu đúng đứng thứ 1 thì MRR bằng bao nhiêu?", "MRR bằng 1.0."),
            ("Nếu tài liệu đúng đứng thứ 2 thì MRR bằng bao nhiêu?", "MRR bằng 0.5."),
            ("MRR khác gì Hit Rate?", "MRR xét vị trí tài liệu đúng còn Hit Rate chỉ xét có hay không."),
            ("Vì sao MRR quan trọng hơn Hit Rate trong một số hệ thống?", "Vì nó phản ánh chất lượng ranking chứ không chỉ sự xuất hiện.")
        ],
        "doc_multi_judge": [
            ("Multi-judge consensus là gì?", "Multi-judge consensus là phương pháp dùng nhiều model judge để chấm cùng một câu trả lời."),
            ("Tại sao phải dùng nhiều judge model?", "Dùng nhiều judge model giúp tăng độ tin cậy và giảm thiên lệch khi chấm."),
            ("Một judge có đủ khách quan không?", "Không hoàn toàn. Multi-judge giúp khách quan hơn so với chỉ dùng một judge."),
            ("Multi-judge dùng để làm gì?", "Multi-judge dùng để tăng độ tin cậy của việc chấm câu trả lời AI."),
            ("Consensus engine là gì?", "Consensus engine là logic tổng hợp điểm từ nhiều judge model.")
        ],
        "doc_agreement_rate": [
            ("Agreement Rate là gì?", "Agreement Rate là tỉ lệ đồng thuận giữa các judge model."),
            ("Khi nào Agreement Rate cao?", "Agreement Rate cao khi các judge model cho điểm gần nhau hoặc giống nhau."),
            ("Agreement Rate phản ánh điều gì?", "Agreement Rate phản ánh mức độ nhất quán giữa các judge."),
            ("Agreement Rate có quan trọng không?", "Có, vì nó cho biết hệ thống chấm điểm có ổn định hay không."),
            ("Agreement Rate liên quan gì đến multi-judge?", "Agreement Rate là chỉ số quan trọng trong multi-judge consensus.")
        ],
        "doc_failure_analysis": [
            ("Failure Analysis là gì?", "Failure Analysis là quá trình phân tích lỗi của hệ thống AI."),
            ("Failure clustering dùng để làm gì?", "Dùng để nhóm các lỗi giống nhau."),
            ("Vì sao cần phân tích lỗi?", "Để biết hệ thống yếu ở đâu."),
            ("Failure Analysis giúp cải thiện agent như thế nào?", "Bằng cách xác định root cause và hướng tối ưu."),
            ("Nếu retrieval đúng nhưng answer sai, lỗi nằm ở đâu?", "Lỗi nằm ở generation hoặc prompt, không phải retrieval.")
        ],
        "doc_five_whys": [
            ("5 Whys là gì?", "5 Whys là phương pháp hỏi tại sao nhiều lần để tìm nguyên nhân gốc rễ."),
            ("Mục tiêu của 5 Whys là gì?", "Mục tiêu của 5 Whys là tìm ra root cause của lỗi."),
            ("5 Whys có dùng trong Failure Analysis không?", "Có, 5 Whys là kỹ thuật phổ biến trong Failure Analysis."),
            ("Root cause là gì?", "Root cause là nguyên nhân gốc rễ gây ra vấn đề."),
            ("Vì sao phải hỏi nhiều lần trong 5 Whys?", "Hỏi nhiều lần giúp đi từ triệu chứng bề mặt đến nguyên nhân sâu hơn.")
        ],
        "doc_regression": [
            ("Regression testing trong AI là gì?", "Regression testing là so sánh agent mới với agent cũ theo score, latency và cost."),
            ("Tại sao phải so sánh V1 và V2?", "Để kiểm tra phiên bản mới có thực sự tốt hơn phiên bản cũ hay không."),
            ("Regression testing đo những gì?", "Regression testing thường đo chất lượng, độ trễ và chi phí."),
            ("Nếu V2 kém hơn V1 thì sao?", "Nếu V2 kém hơn V1 thì có thể phải block release hoặc rollback."),
            ("Regression có vai trò gì trong benchmark?", "Regression giúp đảm bảo bản cập nhật không làm hệ thống tệ đi.")
        ],
        "doc_release_gate": [
            ("Release gate là gì?", "Release gate là cơ chế tự động quyết định approve hoặc rollback dựa trên ngưỡng metric."),
            ("Khi nào nên rollback?", "Nên rollback khi score giảm hoặc latency, cost tăng quá ngưỡng cho phép."),
            ("Approve bản mới khi nào?", "Approve khi phiên bản mới cải thiện hoặc đáp ứng ngưỡng chất lượng đề ra."),
            ("Release gate dựa trên gì?", "Release gate dựa trên các metric như score, latency, cost hoặc safety."),
            ("Auto-gate có lợi ích gì?", "Auto-gate giúp quyết định phát hành một cách tự động và nhất quán.")
        ],
        "doc_async_runner": [
            ("Async runner là gì?", "Async runner là cơ chế chạy nhiều bài test song song bằng asyncio."),
            ("Tại sao cần async trong benchmark?", "Async giúp giảm tổng thời gian chạy benchmark cho nhiều test cases."),
            ("Benchmark song song có lợi ích gì?", "Chạy song song giúp tiết kiệm thời gian và tăng hiệu năng."),
            ("Async runner có giúp tránh chậm không?", "Có, vì nó cho phép xử lý đồng thời nhiều case thay vì tuần tự."),
            ("Batch size trong async runner dùng để làm gì?", "Batch size giúp giới hạn số lượng task chạy đồng thời để tránh rate limit.")
        ],
    }

    # return cases
    for doc_id, qa_list in mapping.items():
        for idx, (question, expected_answer) in enumerate(qa_list):
            difficulty = "hard" if idx == 4 else ("medium" if idx in [2, 3] else "easy")
            case_type = "adversarial" if idx == 4 else "fact-check"
            cases.append({
                "id": f"case_{case_id}",
                "query": question,
                "ground_truth_answer": expected_answer,
                "ground_truth_doc_ids": [doc_id],
                "type": case_type,
                "metadata": {
                    "difficulty": difficulty
                }
            })

            case_id += 1

    return cases

async def main():
    os.makedirs("data", exist_ok=True)
    cases = build_cases()

    with open("data/golden_set.jsonl", "w", encoding="utf-8") as f:
        for case in cases:
            f.write(json.dumps(case, ensure_ascii=False) + "\n")

    print(f"Done! Saved {len(cases)} test cases to data/golden_set.jsonl")

if __name__ == "__main__":
    asyncio.run(main())