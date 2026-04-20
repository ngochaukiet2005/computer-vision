import cv2
import numpy as np
import os
import glob
from preprocessing import apply_preprocessing
from feature_extraction import get_hog_descriptor

def extract_features(image_paths, label, hog):
    features = []
    labels = []
    for path in image_paths:
        # Xử lý trường hợp đường dẫn có tiếng Việt
        img_array = np.fromfile(path, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        if img is not None:
            # 1. Tiền xử lý: Resize, Grayscale, CLAHE, Gaussian Blur
            preprocessed_img = apply_preprocessing(img)
            
            # 2. Trích xuất HOG từ ảnh đã tiền xử lý
            hist = hog.compute(preprocessed_img)
            features.append(hist)
            labels.append(label)
        else:
            print(f"⚠️ Cảnh báo: Không thể đọc được ảnh {path}")
    return features, labels

def train_and_save_svm():
    hog = get_hog_descriptor()
    
    # 1. Tự động lấy vị trí chính xác
    current_dir = os.path.dirname(os.path.abspath(__file__)) 
    backend_dir = os.path.dirname(current_dir) 
    
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
    print("⏳ Đang tiền xử lý và trích xuất đặc trưng HOG từ ảnh...")
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
    
    # Lưu ý: C và Gamma có thể tinh chỉnh sau, Gamma không có tác dụng với LINEAR kernel
    svm.setC(2.67) 
    
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