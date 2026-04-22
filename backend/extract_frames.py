import cv2
import os

os.makedirs('data/raw_frames', exist_ok=True)
video_path = '../data/raw_videos/time-lapse-of-parking-lot-of-shopping-center-filled-with-different-cars-video.mp4'
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print(f"❌ LỖI: Không thể mở được video tại đường dẫn: {video_path}")
    print("Vui lòng kiểm tra lại tên file video và xem bạn đã copy nó vào thư mục backend chưa nhé!")
    exit()

count = 0
frame_id = 0

print("Đang trích xuất ảnh...")
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