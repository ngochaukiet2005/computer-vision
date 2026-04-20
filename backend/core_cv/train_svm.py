import cv2
import numpy as np
import os
import glob

def get_hog_descriptor():
    winSize = (64, 128)
    blockSize = (16, 16)
    blockStride = (8, 8)
    cellSize = (8, 8)
    nbins = 9
    return cv2.HOGDescriptor(winSize, blockSize, blockStride, cellSize, nbins)

def extract_features(image_paths, label, hog):
    features = []
    labels = []
    for path in image_paths:
        # Xử lý trường hợp đường dẫn có tiếng Việt
        img_array = np.fromfile(path, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        if img is not None:
            # Tiền xử lý: Resize về đúng kích thước winSize
            img = cv2.resize(img, (64, 128))
            hist = hog.compute(img)
            features.append(hist)
            labels.append(label)
        else:
            print(f"⚠️ Cảnh báo: Không thể đọc được ảnh {path}")
    return features, labels

def train_and_save_svm():
    hog = get_hog_descriptor()
    
    # 1. Tự động lấy vị trí chính xác
    current_dir = os.path.dirname(os.path.abspath(__file__)) # Vị trí file train_svm.py (thư mục core_cv)
    backend_dir = os.path.dirname(current_dir) # Lùi ra 1 cấp để vào thư mục backend
    
    # 2. Xây dựng đường dẫn tuyệt đối đến thư mục data
    occ_pattern = os.path.join(backend_dir, 'data', 'train', 'occupied', '*.jpg')
    emp_pattern = os.path.join(backend_dir, 'data', 'train', 'empty', '*.jpg')
    
    occupied_paths = glob.glob(occ_pattern)
    empty_paths = glob.glob(emp_pattern)
    
    print("="*50)
    print(f"🔍 Đang tìm ảnh CÓ XE tại: {occ_pattern}")
    print(f"✅ TÌM THẤY: {len(occupied_paths)} ảnh CÓ XE")
    print(f"🔍 Đang tìm ảnh TRỐNG tại: {emp_pattern}")
    print(f"✅ TÌM THẤY: {len(empty_paths)} ảnh TRỐNG")
    print("="*50)
    
    if len(occupied_paths) == 0 and len(empty_paths) == 0:
        print("❌ LỖI: Chưa có ảnh dữ liệu huấn luyện!")
        print("-> Bạn hãy chạy tool cắt ảnh và đảm bảo ảnh lưu đuôi .jpg nhé.")
        return

    # Trích xuất đặc trưng
    print("⏳ Đang trích xuất đặc trưng HOG từ ảnh...")
    features_occ, labels_occ = extract_features(occupied_paths, 1, hog)
    features_emp, labels_emp = extract_features(empty_paths, 0, hog)
    
    # Gom dữ liệu
    X = np.array(features_occ + features_emp, dtype=np.float32)
    y = np.array(labels_occ + labels_emp, dtype=np.int32)
    
    if len(X) == 0:
        print("❌ LỖI: Đọc ảnh thất bại!")
        return

    # Cấu hình và huấn luyện SVM
    svm = cv2.ml.SVM_create()
    svm.setKernel(cv2.ml.SVM_LINEAR)
    svm.setType(cv2.ml.SVM_C_SVC)
    svm.setC(2.67)
    svm.setGamma(5.383)
    
    print("🧠 Đang huấn luyện mô hình SVM...")
    svm.train(X, cv2.ml.ROW_SAMPLE, y)
    
    # Lưu mô hình
    models_dir = os.path.join(backend_dir, 'models')
    os.makedirs(models_dir, exist_ok=True)
    model_save_path = os.path.join(models_dir, 'svm_parking_model.xml')
    
    svm.save(model_save_path)
    print(f"🎉 HOÀN TẤT! Đã lưu mô hình tại:\n{model_save_path}")

if __name__ == '__main__':
    train_and_save_svm()