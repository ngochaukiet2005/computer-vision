import cv2
import os

os.makedirs('data/raw_frames', exist_ok=True)
video_dir = '../data/raw_videos/'

# Lấy danh sách các file mp4 trong thư mục
video_files = [f for f in os.listdir(video_dir) if f.endswith('.mp4')]

if not video_files:
    print(f"❌ LỖI: Không tìm thấy video nào trong thư mục: {video_dir}")
    print("Vui lòng kiểm tra lại xem bạn đã copy nó vào thư mục backend chưa nhé!")
    exit()

count = 0
frame_id = 0

print("Đang trích xuất ảnh...")

for video_file in video_files:
    video_path = os.path.join(video_dir, video_file)
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"❌ LỖI: Không thể mở được video tại đường dẫn: {video_path}")
        # Bỏ qua video bị lỗi và tiếp tục với video tiếp theo thay vì thoát hẳn chương trình
        continue

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        if count % 30 == 0:
            cv2.imwrite(f'../data/raw_frames/frame_{frame_id}.jpg', frame)
            frame_id += 1
        count += 1

    cap.release()

print(f"✅ Đã trích xuất xong {frame_id} ảnh vào thư mục data/raw_frames!")