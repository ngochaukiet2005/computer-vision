import cv2
import numpy as np
import os
from core_cv.preprocessing import apply_preprocessing
from core_cv.feature_extraction import get_hog_descriptor
from core_cv.segmentation import is_flat_background

class ParkingCVPipeline:
    def __init__(self):
        self.hog = get_hog_descriptor()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(os.path.dirname(current_dir), 'models', 'svm_parking_model.xml')
        
        self.svm = None
        if os.path.exists(model_path):
            self.svm = cv2.ml.SVM_load(model_path)
            print("✅ Đã nạp thành công bộ não AI (SVM Model) vào Pipeline!")
        else:
            print("⚠️ CẢNH BÁO: Chưa tìm thấy file svm_parking_model.xml!")
            
        self.spot_history = {}
        self.history_size = 5

    def analyze_spot(self, roi_color):
        """Sử dụng toàn bộ Pipeline (Tiền xử lý -> Phân đoạn -> HOG -> SVM) để dự đoán"""
        preprocessed_img = apply_preprocessing(roi_color)
        if self.svm is None:
            return "empty"
        features = self.hog.compute(preprocessed_img)
        features = np.array([features], dtype=np.float32)
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
            roi_color = frame[y:y+h, x:x+w]
            current_pred = self.analyze_spot(roi_color)
            
            if spot_id not in self.spot_history:
                self.spot_history[spot_id] = [current_pred] * self.history_size
                
            self.spot_history[spot_id].pop(0)
            self.spot_history[spot_id].append(current_pred)
            
            occ_count = self.spot_history[spot_id].count("occupied")
            emp_count = self.spot_history[spot_id].count("empty")
            final_status = "occupied" if occ_count >= 2 else "empty"
            
            results.append({
                "id": spot_id,
                "status": final_status,
                "box": spot['box']
            })
            
        return results