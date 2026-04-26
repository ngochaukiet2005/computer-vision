# Bảng Phân Chia Công Việc - Dự án Smart Parking (Nhóm 6 Thành viên)

Dưới đây là bảng phân công nhiệm vụ chi tiết cho 6 thành viên, đảm bảo mỗi người phụ trách một phần chuyên biệt trong pipeline xử lý ảnh và hệ thống ứng dụng theo yêu cầu của Bài tập lớn.

| Thành viên | Vai trò chính | Công việc cụ thể | Kỹ thuật CV tương ứng |
| :--- | :--- | :--- | :--- |
| **Thành viên 1** (Trưởng nhóm) | **Kiến trúc hệ thống & Tài liệu** | - Thiết kế kiến trúc tổng thể của pipeline và ứng dụng.<br>- Kết nối các module CV vào hệ thống chính.<br>- Viết báo cáo kỹ thuật và tài liệu hướng dẫn. | **System Architecture** |
| **Thành viên 2** | **Tiền xử lý & Phân đoạn** | - Triển khai các kỹ thuật tiền xử lý (Grayscale, CLAHE, Gaussian Blur).<br>- Xây dựng thuật toán phân đoạn dựa trên phương sai (Variance). | **Chương 2 & 4** |
| **Thành viên 3** | **Đặc trưng & Nhận dạng** | - Triển khai trích xuất đặc trưng HOG.<br>- Huấn luyện và tối ưu hóa mô hình phân loại SVM. | **Chương 3 & 5** |
| **Thành viên 4** | **Kỹ sư Dữ liệu & Đánh giá** | - Thu thập video, trích xuất khung hình và gán nhãn dữ liệu.<br>- Thực hiện Data Augmentation.<br>- Đo lường độ chính xác (Accuracy, Precision, Recall). | **Data Engineering** |
| **Thành viên 5** | **Phát triển Backend** | - Xây dựng API Server với FastAPI.<br>- Xử lý WebSocket cho luồng video thời gian thực.<br>- Viết logic quản lý trạng thái bãi đỗ xe. | **Backend Development** |
| **Thành viên 6** | **Phát triển Frontend** | - Xây dựng giao diện Web (Vue 3).<br>- Triển khai công cụ vẽ vùng đỗ xe (Bounding Box).<br>- Hiển thị kết quả nhận diện và chỉ đường. | **Frontend Development** |

---

## Mô tả chi tiết công việc

### 1. Thành viên 1: Trưởng nhóm & Kiến trúc sư
- **Pipeline Integration:** Chịu trách nhiệm kết nối các phần code của Thành viên 2 và 3 thành một luồng xử lý đồng bộ trong `pipeline.py`.
- **System Documentation:** Chịu trách nhiệm chính cho file Báo cáo (25% số điểm), đảm bảo đủ 8 mục yêu cầu và đúng định dạng IEEE/APA cho tài liệu tham khảo.

### 2. Thành viên 2: Kỹ sư Tiền xử lý (Chương 2 & 4)
- **Image Enhancement:** Sử dụng CLAHE để chuẩn hóa độ sáng cho các vùng ảnh bị bóng râm che khuất, giúp các bước sau đạt độ chính xác cao hơn.
- **Background Analysis:** Sử dụng phương sai (Variance) để lọc nhanh các ô đỗ xe trống, giúp giảm tải tính toán cho CPU bằng cách bỏ qua các bước HOG/SVM đối với nền phẳng.

### 3. Thành viên 3: Chuyên gia Nhận dạng (Chương 3 & 5)
- **HOG Implementation:** Thiết lập các tham số cho HOG Descriptor để trích xuất được "bản sắc" hình học của các loại xe khác nhau.
- **SVM Classification:** Sử dụng thư viện `cv2.ml` để huấn luyện bộ phân loại. Tinh chỉnh các tham số hạt nhân (kernel) để tách biệt tốt nhất giữa hai lớp: `occupied` và `empty`.

### 4. Thành viên 4: Kỹ sư Dữ liệu & Kiểm thử
- **Data Collection:** Thu thập video thực tế từ các bãi đỗ xe (đáp ứng yêu cầu "Dữ liệu thực tế" trong PDF).
- **Metric Evaluation:** Sau khi Thành viên 3 có model, Thành viên 4 sẽ chạy kiểm thử trên tập dữ liệu độc lập để tính toán các chỉ số định lượng (Accuracy, F1-score) cho báo cáo.

### 5. Thành viên 5: Lập trình viên Backend
- **Real-time Processing:** Xử lý việc nhận khung hình từ camera và trả kết quả về frontend qua WebSocket mỗi 200ms.
- **Smart Routing:** Triển khai thuật toán tìm kiếm vị trí trống gần nhất dựa trên tọa độ tâm của các bounding box.

### 6. Thành viên 6: Lập trình viên Frontend
- **Interactive UI:** Tạo giao diện Dashboard hiển thị sơ đồ bãi đỗ xe sống động.
- **Configurable Tool:** Phát triển tính năng cho phép người dùng cấu hình hệ thống bằng cách vẽ trực tiếp các ô đỗ xe lên màn hình video, giúp hệ thống có tính tùy biến cao.
