import cv2
import numpy as np
import os
from core_cv.preprocessing import apply_preprocessing
from core_cv.feature_extraction import get_hog_descriptor
from core_cv.segmentation import is_flat_background

class ParkingCVPipeline:
    def __init__(self):
        # 1. Khởi tạo thuật toán trích xuất đặc trưng HOG (Chương 3)
        self.hog = get_hog_descriptor()

        # 2. Tự động tải mô hình SVM đã huấn luyện (Chương 5)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(os.path.dirname(current_dir), 'models', 'svm_parking_model.xml')
        
        self.svm = None
        if os.path.exists(model_path):
            self.svm = cv2.ml.SVM_load(model_path)
            print("✅ Đã nạp thành công bộ não AI (SVM Model) vào Pipeline!")
        else:
            print("⚠️ CẢNH BÁO: Chưa tìm thấy file svm_parking_model.xml!")

    def analyze_spot(self, roi_color):
        """Sử dụng toàn bộ Pipeline (Tiền xử lý -> Phân đoạn -> HOG -> SVM) để dự đoán"""
        
        # BƯỚC 1: Phân đoạn ảnh / Early Exit (Chương 4)
        # Tính phương sai trên ảnh gốc Xám (trước khi cân bằng sáng) để độ chính xác cao hơn
        gray_for_var = cv2.cvtColor(cv2.resize(roi_color, (64, 128)), cv2.COLOR_BGR2GRAY)
        is_empty, variance = is_flat_background(gray_for_var, variance_threshold=50) # Giảm ngưỡng xuống 50
        if is_empty:
            return "empty"

        # BƯỚC 2: Tiền xử lý (Chương 2) - Grayscale, CLAHE, Gaussian Blur
        preprocessed_img = apply_preprocessing(roi_color)

        # BƯỚC 3 & 4: HOG + SVM (Chương 3 & 5)
        if self.svm is None:
            return "empty" # Nếu chưa có model thì mặc định trả về Trống

        # Trích xuất vector HOG từ ảnh đã tiền xử lý
        features = self.hog.compute(preprocessed_img)
        features = np.array([features], dtype=np.float32)

        # AI Phân loại
        _, result = self.svm.predict(features)
        
        if int(result[0][0]) == 1:
            return "occupied"
        else:
            return "empty"

    def process_frame(self, frame, parking_spots):
        """Hàm chính xử lý toàn bộ các ô đỗ trên frame dựa vào tọa độ từ Vue.js"""
        results = []
        for spot in parking_spots:
            x, y, w, h = spot['box']
            
            # Cắt lấy vùng ảnh MÀU chứa ô đỗ xe
            roi_color = frame[y:y+h, x:x+w]

            # Phân tích trạng thái
            status = self.analyze_spot(roi_color)
            
            results.append({
                "id": spot['id'],
                "status": status,
                "box": spot['box']
            })
            
        return results