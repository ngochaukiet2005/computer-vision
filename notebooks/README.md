# Notebooks Directory

Thư mục này chứa các Jupyter Notebook phục vụ cho việc nghiên cứu, thử nghiệm và trình diễn các thuật toán Computer Vision cho hệ thống Smart Parking.

## Cấu trúc thư mục

- **01_preprocessing_exploration.ipynb**: Thử nghiệm các kỹ thuật tiền xử lý (Gray, CLAHE, Gaussian Blur) để tối ưu hóa ảnh đầu vào.
- **02_svm_training_analysis.ipynb**: Huấn luyện mô hình SVM sử dụng đặc trưng HOG. Đánh giá độ chính xác và Confusion Matrix.
- **03_cv_pipeline_demo.ipynb**: Kết hợp toàn bộ Pipeline (Tiền xử lý -> Phân đoạn -> Phân loại) trên video thực tế.
- **04_background_analysis.ipynb**: Nghiên cứu kỹ thuật phân đoạn dựa trên phương sai (Variance) để tối ưu hóa tốc độ hệ thống (Early Exit).

## Lưu ý
- Dữ liệu thô nên được đặt trong `backend/data/raw`.
- Mô hình sau khi huấn luyện xong nên được lưu vào `backend/models/`.
- Hạn chế để code "rác" trong này; khi thuật toán đã ổn định, hãy chuyển nó vào `backend/core_cv/`.
