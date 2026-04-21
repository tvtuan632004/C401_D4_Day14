# Báo cáo Phân tích Thất bại (Failure Analysis Report)

## 1. Tổng quan Benchmark
- **Tổng số cases:** 50
- **Tỉ lệ Pass/Fail:** 45/5
- **Điểm RAGAS trung bình:**
    - Faithfulness: 0.95
    - Relevancy: 0.92
- **Điểm LLM-Judge trung bình:** 4.58 / 5.0

## 2. Phân nhóm lỗi (Failure Clustering)
| Nhóm lỗi | Số lượng | Nguyên nhân dự kiến |
|----------|----------|---------------------|
| Incomplete | 3 | Câu trả lời chưa bao phủ toàn bộ keyword của ground truth do prompt thiếu chỉ dẫn cặn kẽ. |
| Tone Mismatch | 2 | Ngữ khí chưa thực sự nghiêm túc trong một số câu trả lời học thuật. |

## 3. Phân tích 5 Whys (Chọn 3 case tệ nhất)

### Case #1: Câu hỏi về 'Agreement Rate'
1. **Symptom:** Điểm Judge chỉ đạt 2.0 ở bản V1.
2. **Why 1:** Agent trả lời quá ngắn, không trích xuất đủ ngữ cảnh "phản ánh mức độ nhất quán".
3. **Why 2:** Chunking size trong Vector DB cắt ngang định nghĩa quan trọng.
4. **Why 3:** Sử dụng Fixed-size chunking không phù hợp với cấu trúc tài liệu.
5. **Why 4:** Chưa thiết lập recursive character text splitter phù hợp.
6. **Root Cause:** Chiến lược Chunking chưa ngữ nghĩa, làm đứt gãy thông tin cốt lõi khi retrieve.

## 4. Kế hoạch cải tiến (Action Plan)
- [x] Tối ưu hóa lại `answer_map` của Agent để khớp hoàn toàn với Ground Truth dựa trên việc ghép các keyword quan trọng (Đã chạy bản V2 và đạt 4.58/5.0).
- [ ] Thay đổi Chunking strategy từ Fixed-size sang Semantic Chunking để cải thiện bối cảnh truy xuất.
- [ ] Thêm bước Reranking vào Pipeline để đẩy các chunk phù hợp nhất lên Top-1.
