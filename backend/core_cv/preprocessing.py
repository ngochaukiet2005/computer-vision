import cv2

def apply_preprocessing(image):
    """
    Kỹ thuật Chương 2: Tiền xử lý ảnh
    - Chuyển sang ảnh xám (Grayscale)
    - Cân bằng sáng (CLAHE - Contrast Limited Adaptive Histogram Equalization)
    - Lọc nhiễu (Gaussian Blur)
    """
    resized = cv2.resize(image, (64, 128))
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    equalized = clahe.apply(gray)
    blurred = cv2.GaussianBlur(equalized, (3, 3), 0)
    
    return blurred
