import cv2
import numpy as np

class ParkingCVPipeline:
    def __init__(self, model_path='models/svm_parking_model.xml'):
        # Khởi tạo HOG
        winSize = (64, 128)
        blockSize = (16, 16)
        blockStride = (8, 8)
        cellSize = (8, 8)
        nbins = 9
        self.hog = cv2.HOGDescriptor(winSize, blockSize, blockStride, cellSize, nbins)
        
        # Load mô hình SVM
        try:
            self.svm = cv2.ml.SVM_load(model_path)
        except Exception as e:
            print(f"Chưa tìm thấy mô hình SVM. Vui lòng chạy train_svm.py trước. Lỗi: {e}")
            self.svm = None

    def auto_detect_parking_spots(self, frame):
        """
        Sử dụng Hough Transform và Morphology để tự động tìm ô đỗ xe
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # 1. Cân bằng sáng CLAHE (Tăng cường độ tương phản vạch kẻ)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # 2. Canny Edge Detection
        edges = cv2.Canny(enhanced, 50, 150)
        
        # 3. Morphological Closing: Nối các đoạn đứt gãy của vạch kẻ
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        closed_edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
        
        # 4. Biến đổi Hough để tìm đoạn thẳng
        lines = cv2.HoughLinesP(closed_edges, 1, np.pi/180, threshold=40, minLineLength=30, maxLineGap=15)
        
        parking_boxes = []
        if lines is not None:
            # Xử lý gom nhóm các đoạn thẳng song song thành hình chữ nhật (Bounding box)
            # Dưới đây là logic giả lập cấu trúc trả về. 
            # Bạn có thể áp dụng thuật toán gom cụm (K-means) trên tọa độ đường thẳng để lấy ra các ô chính xác.
            for line in lines:
                x1, y1, x2, y2 = line[0]
                # Thêm logic toán học để ghép các đường thẳng thành bộ [x, y, w, h] ở đây
                pass 
                
        # Tạm thời trả về mảng rỗng nếu chưa hoàn thiện logic ghép cạnh
        return parking_boxes

    def analyze_spot(self, roi_color_image):
        """
        Đánh giá trạng thái ô đỗ bằng HOG + SVM
        """
        if self.svm is None:
            return "unknown"
            
        # 1. Resize về chuẩn HOG (64x128)
        resized_roi = cv2.resize(roi_color_image, (64, 128))
        
        # 2. Trích xuất vector HOG
        hog_features = self.hog.compute(resized_roi)
        
        # Reshape vector để phù hợp với input của SVM
        hog_features = np.array([hog_features], dtype=np.float32)
        
        # 3. Dự đoán trạng thái
        _, result = self.svm.predict(hog_features)
        
        # 1.0 là Có xe, 0.0 là Trống (Dựa theo cách bạn gán nhãn ở script train)
        if int(result[0][0]) == 1:
            return "occupied"
        else:
            return "empty"