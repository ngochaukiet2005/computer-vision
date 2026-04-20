import numpy as np

def is_flat_background(gray_image, variance_threshold=150):
    """
    Kỹ thuật Chương 4: Phân đoạn ảnh / Phân tích nền
    Nhựa đường trống thường có phương sai cường độ pixel rất thấp do màu sắc đồng nhất.
    Sử dụng hàm này như một bộ lọc sớm (Early Exit) để loại bỏ các ô chắc chắn là Trống, 
    tiết kiệm thời gian tính toán cho SVM.
    
    Args:
        gray_image: Ảnh đã qua tiền xử lý (ảnh xám, lọc nhiễu)
        variance_threshold: Ngưỡng phương sai tối đa để coi là bãi trống
        
    Returns:
        is_empty (bool): True nếu mặt đường phẳng và trống
        variance (float): Giá trị phương sai tính được
    """
    # Tính phương sai cường độ pixel
    variance = np.var(gray_image)
    
    # Nếu phương sai quá thấp, nghĩa là mặt đường phẳng -> Trống
    if variance < variance_threshold:
        return True, variance
    return False, variance
