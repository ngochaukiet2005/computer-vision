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
            
        self.spot_state = {}

    def _crop_center(self, roi_color, ratio=0.5):
        height, width = roi_color.shape[:2]
        if height < 8 or width < 8:
            return roi_color

        crop_h = max(4, int(height * ratio))
        crop_w = max(4, int(width * ratio))
        top = max(0, (height - crop_h) // 2)
        left = max(0, (width - crop_w) // 2)
        return roi_color[top:top + crop_h, left:left + crop_w]

    def _sample_regions(self, roi_color):
        height, width = roi_color.shape[:2]
        if height < 8 or width < 8:
            return [roi_color]

        regions = []
        centers = [
            (0.50, 0.50),
            (0.35, 0.50),
            (0.65, 0.50),
            (0.50, 0.35),
            (0.50, 0.65),
        ]

        crop_h = max(4, int(height * 0.45))
        crop_w = max(4, int(width * 0.45))

        for center_x, center_y in centers:
            left = int(width * center_x - crop_w / 2)
            top = int(height * center_y - crop_h / 2)
            left = max(0, min(left, width - crop_w))
            top = max(0, min(top, height - crop_h))
            regions.append(roi_color[top:top + crop_h, left:left + crop_w])

        return regions

    def analyze_spot(self, roi_color):
        """Sử dụng toàn bộ Pipeline (Tiền xử lý -> Phân đoạn -> HOG -> SVM) để dự đoán"""
        votes = []
        for region in self._sample_regions(roi_color):
            preprocessed_img = apply_preprocessing(region)

            is_empty_bg, variance = is_flat_background(preprocessed_img)
            if is_empty_bg and variance < 120:
                votes.append("empty")
                continue

            if self.svm is None:
                votes.append("empty")
                continue

            features = self.hog.compute(preprocessed_img)
            features = np.array([features], dtype=np.float32)
            _, result = self.svm.predict(features)
            votes.append("occupied" if int(result[0][0]) == 1 else "empty")

        occupied_votes = votes.count("occupied")
        empty_votes = votes.count("empty")
        return "occupied" if occupied_votes >= 3 else "empty"

    def _get_final_status(self, spot_id, current_pred):
        state = self.spot_state.setdefault(spot_id, {
            "status": "empty",
            "occupied_hits": 0,
            "empty_hits": 0,
        })

        if current_pred == "occupied":
            state["occupied_hits"] += 1
            state["empty_hits"] = 0
        else:
            state["empty_hits"] += 1
            state["occupied_hits"] = 0

        if state["status"] == "empty" and state["occupied_hits"] >= 2:
            state["status"] = "occupied"
        elif state["status"] == "occupied" and state["empty_hits"] >= 5:
            state["status"] = "empty"

        return state["status"]

    def process_frame(self, frame, parking_spots):
        """Hàm chính xử lý toàn bộ các ô đỗ trên frame"""
        results = []
        for spot in parking_spots:
            spot_id = spot['id']
            x, y, w, h = spot['box']
            roi_color = frame[y:y+h, x:x+w]
            current_pred = self.analyze_spot(roi_color)
            final_status = self._get_final_status(spot_id, current_pred)
            
            results.append({
                "id": spot_id,
                "status": final_status,
                "box": spot['box']
            })
            
        return results