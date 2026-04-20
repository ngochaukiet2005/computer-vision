import cv2

def apply_preprocessing(image):
    """
    Kỹ thuật Chương 2: Tiền xử lý ảnh
    1. Chuyển sang ảnh xám (Grayscale)
    2. Cân bằng sáng (CLAHE)
    3. Lọc nhiễu (Gaussian Blur)
    """
    # Đảm bảo resize về chuẩn chung để thuật toán ổn định
    resized = cv2.resize(image, (64, 128))
    
    # 1. Chuyển sang ảnh xám
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    
    # 2. Cân bằng sáng (CLAHE - Contrast Limited Adaptive Histogram Equalization)
    # Giúp giải quyết vấn đề ánh sáng yếu, bóng râm trong bãi đỗ xe
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    equalized = clahe.apply(gray)
    
    # 3. Lọc nhiễu (Gaussian Blur)
    # Khử nhiễu hột từ camera để tránh ảnh hưởng đến việc tính toán gradient sau này
    blurred = cv2.GaussianBlur(equalized, (3, 3), 0)
    
    return blurred
