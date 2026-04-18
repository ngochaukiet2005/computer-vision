from fastapi import FastAPI, WebSocket, WebSocketDisconnect, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import shutil
import os
import cv2
from core_cv.pipeline import ParkingCVPipeline

app = FastAPI(title="Smart Parking Simulation API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

os.makedirs("../data/raw_videos", exist_ok=True)
os.makedirs("models", exist_ok=True)

# Biến toàn cục để lưu trạng thái Video và Thuật toán
cv_pipeline = ParkingCVPipeline()
video_cap = None
current_spots = []

@app.post("/upload-config")
async def upload_config(video: UploadFile = File(...), rois: str = Form(...)):
    global video_cap, current_spots, cv_pipeline
    
    # 1. Lưu video
    video_path = f"../data/raw_videos/{video.filename}"
    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(video.file, buffer)
    
    # 2. Lưu tọa độ vẽ tay
    current_spots = json.loads(rois)
    with open("models/parking_spots.json", "w") as f:
        json.dump(current_spots, f, indent=4)
        
    # 3. Khởi tạo lại luồng Camera và reset thuật toán CV
    if video_cap is not None:
        video_cap.release()
    video_cap = cv2.VideoCapture(video_path)
    cv_pipeline = ParkingCVPipeline() 
    
    return {"status": "success", "message": "Đã lưu cấu hình bãi đỗ!"}

@app.websocket("/ws/parking")
async def websocket_endpoint(websocket: WebSocket):
    global video_cap, current_spots, cv_pipeline
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            event = json.loads(data)
            
            if event.get("action") == "car_enter":
                if video_cap is None or not video_cap.isOpened():
                    await websocket.send_json({"status": "error", "message": "Chưa có video camera!"})
                    continue
                    
                # Tiến tới khung hình (frame) tiếp theo của video để giả lập thời gian thực
                ret, frame = video_cap.read()
                if not ret:
                    video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0) # Nếu hết video thì lặp lại
                    ret, frame = video_cap.read()

                # ĐƯA FRAME VÀO PIPELINE XỬ LÝ ẢNH
                updated_spots = cv_pipeline.process_frame(frame, current_spots)
                
                # Logic: Tìm ô trống gần nhất (Ở đây lấy ô trống đầu tiên trong danh sách)
                empty_spot = "BÃI ĐÃ ĐẦY!"
                for spot in updated_spots:
                    if spot['status'] == 'empty':
                        empty_spot = spot['id']
                        break

                await websocket.send_json({
                    "status": "success",
                    "closest_empty_spot": empty_spot,
                    "parking_state": updated_spots
                })
                
    except WebSocketDisconnect:
        pass

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)