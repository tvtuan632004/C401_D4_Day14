# Individual Reflection Report - Hồ Bảo Thư

## 1. Engineering Contribution (15 điểm)
- **Module phụ trách:** Mở rộng bộ test cases có độ khó cao cho hệ thống AI Evaluation, bổ sung chỉ số đánh giá Retrieval theo hướng multi-document, và chỉnh sửa pipeline chạy đánh giá đầu-cuối.
- **Chi tiết công việc:**
  - **Thiết kế bộ test khó (`synthetic_gen.py`):** Xây dựng và mở rộng bộ synthetic cases từ các câu hỏi fact-check cơ bản sang nhiều nhóm khó hơn như **multi-doc reasoning**, **prompt injection**, **goal hijacking**, **out-of-context**, **ambiguous questions**, **simulated conflict**, **multi-turn carry-over**, **correction**, **cost-efficiency**, và **latency-stress**. Đồng thời chuẩn hóa metadata để phân loại rõ mức độ khó và loại test case, giúp pipeline đánh giá phản ánh đúng các failure modes thực tế hơn.  
  - **Mở rộng Retrieval Metrics (`retrieval_metrics.py` / tên đề xuất):** Bổ sung thêm **Recall@K** bên cạnh các metric cơ bản như Hit Rate và MRR. Recall@K được thêm vào để đánh giá đúng hơn các câu hỏi có **nhiều tài liệu ground truth**, thay vì chỉ kiểm tra kiểu nhị phân “có tìm thấy hay không”.
  - **Chỉnh sửa Evaluation Flow (`eval_runner.py`, `main_eval.py` / tên đề xuất):** Sửa phần eval và hàm main để pipeline có thể đọc bộ test mới, xử lý được nhiều loại case hơn, chạy qua toàn bộ tập test mở rộng, và tổng hợp kết quả theo từng nhóm difficulty/type. Việc này giúp hệ thống không chỉ báo điểm chung mà còn cho thấy agent yếu ở loại lỗi nào.
- **Kết quả đạt được:** Xây dựng được một bộ test có độ khó cao hơn đáng kể so với bộ baseline ban đầu, đồng thời nâng cấp pipeline retrieval evaluation để phù hợp với bài toán **multi-document retrieval** và đánh giá theo nhiều tình huống khó thực tế hơn. Bộ test mới không chỉ đo độ đúng của retrieval mà còn đo được tính ổn định của agent trước các câu hỏi gây nhiễu và các tình huống biên.

## 2. Technical Depth (15 điểm)
- **Kiến thức đạt được:**
  - **Thiết kế hard cases cho AI Evaluation:** Hiểu rằng một bộ test tốt không thể chỉ gồm các câu hỏi fact-check trực tiếp, mà cần bao phủ nhiều failure modes khác nhau như adversarial prompts, ambiguity, out-of-context, và multi-turn dependency. Việc phân tách rõ từng loại case giúp đánh giá agent sát thực tế hơn và tránh việc benchmark quá “dễ”.
  - **Recall@K cho multi-doc retrieval:** Hiểu rõ sự khác biệt giữa **Hit Rate** và **Recall@K**. Hit Rate chỉ cho biết hệ thống có lấy được ít nhất một tài liệu đúng hay không, trong khi Recall@K phản ánh mức độ coverage khi một câu hỏi cần nhiều tài liệu đúng cùng lúc. Điều này đặc biệt quan trọng với các câu hỏi tổng hợp hoặc so sánh.
  - **MRR và ranking quality:** Củng cố hiểu biết rằng MRR phù hợp để đánh giá chất lượng sắp xếp tài liệu, còn Recall@K bổ sung góc nhìn về coverage. Việc kết hợp cả hai giúp đánh giá retrieval cân bằng hơn.
  - **Đánh giá theo taxonomy của test cases:** Nắm được cách tổ chức bộ benchmark theo các nhóm như `fact-check`, `reasoning`, `multi-doc`, `prompt-injection`, `goal-hijacking`, `ambiguous`, `out-of-context`, `simulated-conflict`, `multi-turn`, và `latency-stress`, từ đó giúp phân tích kết quả chi tiết hơn thay vì chỉ nhìn một điểm số trung bình.
  - **Thiết kế pipeline đánh giá mở rộng:** Hiểu cách chỉnh sửa luồng eval/main để hỗ trợ format test case giàu metadata hơn, đồng thời tổng hợp metric theo từng nhóm difficulty và từng loại lỗi nhằm phục vụ failure analysis tốt hơn.

## 3. Problem Solving (10 điểm)
- **Vấn đề gặp phải:**
  - Bộ test ban đầu chủ yếu là **single-doc fact-check**, nên chưa đủ khó để phản ánh đúng chất lượng của agent trong các tình huống thực tế.
  - Khi bắt đầu thêm các câu hỏi cần nhiều tài liệu đúng, các metric cũ như Hit Rate không còn đủ để đánh giá chính xác mức độ retrieval coverage.
  - Pipeline eval ban đầu chưa được tổ chức để xử lý và báo cáo kết quả theo các nhóm test khó khác nhau.
- **Cách khắc phục:**
  - Mở rộng bộ synthetic data bằng cách thêm các nhóm case khó có chủ đích, đặc biệt là **multi-doc** và các nhóm phía sau như adversarial, ambiguous, out-of-context, correction, và stress cases. Việc này làm benchmark đa dạng hơn và kiểm tra được nhiều failure modes hơn.
  - Bổ sung **Recall@K** để xử lý các trường hợp có nhiều tài liệu ground truth, giúp phân biệt rõ hệ thống retrieval lấy được một phần hay toàn bộ các tài liệu cần thiết.
  - Chỉnh sửa lại phần **eval** và **main** để chạy được trên bộ test mở rộng, đồng thời tổng hợp kết quả theo từng nhóm test. Nhờ đó, thay vì chỉ biết agent “điểm cao hay thấp”, có thể xác định agent yếu ở phần nào: retrieval coverage, reasoning multi-doc, khả năng chống prompt injection, hay xử lý ambiguity.
- **Kết quả:** Pipeline đánh giá trở nên thực tế hơn, có khả năng phản ánh cả chất lượng retrieval lẫn độ bền của agent trước các tình huống khó. Điều này giúp nhóm có cơ sở tốt hơn để phân tích lỗi và cải tiến hệ thống theo đúng từng vấn đề cụ thể.
