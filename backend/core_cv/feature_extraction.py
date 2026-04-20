import cv2

def get_hog_descriptor():
    """
    Kỹ thuật Chương 3: Trích xuất đặc trưng hình học
    Sử dụng HOG (Histogram of Oriented Gradients) để mô tả hình dáng và cạnh của xe ô tô.
    """
    winSize = (64, 128)
    blockSize = (16, 16)
    blockStride = (8, 8)
    cellSize = (8, 8)
    nbins = 9
    return cv2.HOGDescriptor(winSize, blockSize, blockStride, cellSize, nbins)
