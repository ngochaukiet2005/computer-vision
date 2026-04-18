import cv2
import numpy as np

class ParkingCVPipeline:
    def __init__(self):
        # Kỹ thuật 3 (Chương 4): Khởi tạo thuật toán Trừ nền (Background Subtraction MOG2)
        # Giúp nhận diện các vật thể (xe) di chuyển vào bãi đỗ.
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=50, detectShadows=False)

    def preprocess(self, frame):
        """Kỹ thuật 1 (Chương 2): Tiền xử lý ảnh"""
        # Chuyển sang ảnh xám để giảm khối lượng tính toán
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Lọc nhiễu Gaussian để làm mịn ảnh, loại bỏ nhiễu hạt từ camera
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        return blurred

    def get_edges(self, blurred_frame):
        """Kỹ thuật 2 (Chương 3): Phát hiện đặc trưng"""
        # Dùng thuật toán Canny để tìm viền của các xe đang đỗ
        edges = cv2.Canny(blurred_frame, 50, 150)
        return edges

    def analyze_spot(self, roi_edges, roi_mask):
        """
        Phân tích trạng thái Trống/Có xe của 1 ô đỗ cụ thể.
        Dựa vào mật độ đường viền (edges) và chuyển động (mask).
        """
        total_pixels = roi_edges.shape[0] * roi_edges.shape[1]
        if total_pixels == 0: return "empty"

        # Đếm số lượng điểm ảnh trắng (là viền xe hoặc đối tượng nổi bật)
        edge_pixels = cv2.countNonZero(roi_edges)
        edge_density = edge_pixels / total_pixels
        
        # NGƯỠNG QUYẾT ĐỊNH (Threshold)
        # Ô đỗ trống (chỉ có nền đường nhựa) sẽ có rất ít viền.
        # Nếu mật độ viền > 8% (0.08), ta kết luận là Có Xe.
        # (Số 0.08 này có thể tinh chỉnh nếu video của bạn sáng/tối hơn).
        if edge_density > 0.08:
            return "occupied"
        else:
            return "empty"

    def process_frame(self, frame, parking_spots):
        """Hàm chính chạy qua 3 kỹ thuật cho frame hiện tại"""
        blurred = self.preprocess(frame)
        edges = self.get_edges(blurred)
        
        # Cập nhật background model (Giúp hệ thống học được nền đường)
        fg_mask = self.bg_subtractor.apply(blurred)

        results = []
        for spot in parking_spots:
            x, y, w, h = spot['box']
            # Cắt ảnh (ROI) đúng vào vị trí người dùng đã vẽ trên web
            roi_edges = edges[y:y+h, x:x+w]
            roi_mask = fg_mask[y:y+h, x:x+w]

            status = self.analyze_spot(roi_edges, roi_mask)
            results.append({
                "id": spot['id'],
                "status": status,
                "box": spot['box']
            })
            
        return results