# Individual Reflection Report - Lê Đình Việt

## 1. Engineering Contribution (15 điểm)
- **Module phụ trách:** Xây dựng hệ thống Đánh giá Retrieval toàn diện, Sinh dữ liệu tổng hợp chất lượng cao (Synthetic Data Generation), và Triển khai Multi-Judge LLM Consensus Engine.
- **Chi tiết công việc:**
  - **Synthetic Data Generation (`synthetic_gen.py`):** Thiết kế và xây dựng bộ sinh dữ liệu tổng hợp bao gồm 10+ topics chuẩn hóa với document IDs ánh xạ rõ ràng. Tạo mapping giữa câu hỏi (queries) và tài liệu đúng (ground truth documents) để phục vụ cho việc đánh giá retrieval và multi-judge consensus.
  - **Retrieval Evaluation Engine (`retrieval_eval.py`):** Triển khai đầy đủ 3 chỉ số đánh giá chính: Hit Rate (top-k detection), Recall@K (multi-doc matching), và MRR (Mean Reciprocal Rank). Xử lý các edge cases (empty docs, multi-doc answers) với logic robust.
  - **Multi-Judge LLM Consensus (`llm_judge.py`):** Tích hợp 2 model judge độc lập (GPT-4o-mini & Gemini-pro) chạy song song (async), xây dựng cơ chế đo lường Agreement Rate giữa các judge và logic xử lý xung đột tự động.
- **Kết quả đạt được:** Xây dựng thành công pipeline đánh giá multi-layer với Retrieval metrics (Hit Rate, Recall, MRR) + Answer Quality consensus (Multi-Judge). Hệ thống chạy hoàn toàn async với 50+ test cases trong < 2 phút, đạt 100% agreement rate giữa 2 judge model.

## 2. Technical Depth (15 điểm)
- **Kiến thức đạt được:**
  - **Hit Rate & Recall@K:** Hiểu rõ sự khác biệt giữa 2 chỉ số này - Hit Rate (binary: có/không tìm thấy) vs Recall@K (tỉ lệ số doc đúng được trả về). Recall@K phù hợp hơn cho multi-doc questions.
  - **MRR (Mean Reciprocal Rank):** Chỉ số đánh giá ranking quality - doc đúng ở vị trí càng gần đầu (rank 1) thì score càng cao (1.0). Công thức 1/(rank) giúp penalize các kết quả ranking kém.
  - **Agreement Rate & Cohen's Kappa:** Đo lường sự đồng thuận giữa multiple judges. 100% agreement rate đồng nghĩa bộ prompt evaluation đáng tin cậy, không bị bias từ một model cụ thể.
  - **Async/Await & Concurrency:** Nắm vững Python async patterns để chạy multiple LLM calls song song, giảm latency từ sequential (5+ phút) xuống < 2 phút cho 50 cases.
  - **Position Bias & Debiasing:** Nhận thức về hiện tượng judge models thiên vị lựa chọn câu trả lời xuất hiện đầu tiên. Cách giảm thiểu bằng prompt engineering và randomization.

## 3. Problem Solving (10 điểm)
- **Vấn đề gặp phải:** 
  - Khi triển khai retrieval evaluation, gặp khó khăn với việc xử lý multi-document ground truth (nhiều tài liệu đúng có thể trả lời câu hỏi). Hit Rate (binary) không đủ để đánh giá chính xác coverage.
  - Multi-judge async calls ban đầu không có cơ chế xử lý khi 1 judge model fail, dẫn đến toàn bộ evaluation hang.
- **Cách khắc phục:**
  - Triển khai thêm Recall@K metric để đo lường tỉ lệ doc đúng được trả về, cùng với Hit Rate. Điều này giúp phân biệt được hệ thống retrieval tìm được 1/3 doc đúng vs 3/3 doc đúng.
  - Thêm exception handling & fallback logic trong `_judge_gpt()` và `_judge_gemini()` để một judge fail vẫn có thể lấy score từ judge còn lại. Thiết kế confidence scoring dựa trên agreement level.
  - Kết quả: Pipeline ổn định, hoàn thành đánh giá 50+ cases với tỷ lệ success 100%, không có hanging request. 
