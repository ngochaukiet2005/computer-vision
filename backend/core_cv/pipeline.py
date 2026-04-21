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
            
        # Biến lưu trữ lịch sử trạng thái (Dùng để chống nhiễu / chớp nháy do camera rung lắc)
        self.spot_history = {}
        self.history_size = 5  # Giảm xuống 5 frame (~1 giây) để hệ thống phản hồi cực nhanh thời gian thực

    def analyze_spot(self, roi_color):
        """Sử dụng toàn bộ Pipeline (Tiền xử lý -> Phân đoạn -> HOG -> SVM) để dự đoán"""
        
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
        """Hàm chính xử lý toàn bộ các ô đỗ trên frame"""
        results = []
        for spot in parking_spots:
            spot_id = spot['id']
            x, y, w, h = spot['box']
            
            # Cắt ảnh chính xác theo khung hình người dùng vẽ trên giao diện
            # Điều này giúp linh hoạt cho mọi video, người dùng vẽ ô to thì cắt to, vẽ nhỏ cắt nhỏ
            roi_color = frame[y:y+h, x:x+w]

            # Phân tích trạng thái bằng AI (SVM)
            current_pred = self.analyze_spot(roi_color)
            
            # Smoothing (Chống chớp nháy): Lấy biểu quyết từ N frame gần nhất
            if spot_id not in self.spot_history:
                self.spot_history[spot_id] = [current_pred] * self.history_size
                
            self.spot_history[spot_id].pop(0)
            self.spot_history[spot_id].append(current_pred)
            
            occ_count = self.spot_history[spot_id].count("occupied")
            emp_count = self.spot_history[spot_id].count("empty")
            
            # Phản hồi CỰC NHANH (Asymmetric Smoothing)
            # Thay vì chờ quá bán (3/5), chỉ cần 2 khung hình phát hiện có xe là lập tức bật ĐỎ
            # Giúp hệ thống đổi màu ngay khi xe vừa tiến vào được một nửa
            final_status = "occupied" if occ_count >= 2 else "empty"
            
            results.append({
                "id": spot_id,
                "status": final_status,
                "box": spot['box']
            })
            
        return results