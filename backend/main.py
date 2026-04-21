from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import shutil
import os
import cv2
from core_cv.pipeline import ParkingCVPipeline

app = FastAPI(title="Smart Parking Simulation API (Multi-Camera)")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

os.makedirs("../data/raw_videos", exist_ok=True)
os.makedirs("models", exist_ok=True)

# Hệ thống quản lý Đa Camera
camera_system = {} 
# Cấu trúc: { "cam_id": { "video_cap": obj, "spots": [...], "pipeline": obj } }

@app.post("/upload-config-multi")
async def upload_config_multi(request: Request):
    global camera_system
    
    # Giải phóng camera cũ nếu có
    for cam_id, data in camera_system.items():
        if data["video_cap"] is not None:
            data["video_cap"].release()
            
    camera_system = {}
    
    form = await request.form()
    config_str = form.get("config")
    if not config_str:
        return {"status": "error", "message": "Thiếu dữ liệu cấu hình JSON (config)"}
        
    config = json.loads(config_str)
    
    # Duyệt qua từng camera
    for cam_id, spots in config.items():
        video_file = form.get(f"video_{cam_id}")
        if not video_file:
            continue
            
        video_path = f"../data/raw_videos/{video_file.filename}"
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(video_file.file, buffer)
            
        # Khởi tạo pipeline và OpenCV VideoCapture
        cap = cv2.VideoCapture(video_path)
        camera_system[cam_id] = {
            "video_path": video_path,
            "video_cap": cap,
            "spots": spots,
            "pipeline": ParkingCVPipeline()
        }
    
    # Lưu backup config
    with open("models/parking_spots_multi.json", "w") as f:
        json.dump(config, f, indent=4)
        
    return {"status": "success", "message": "Cấu hình hệ thống đa camera thành công!"}

@app.websocket("/ws/parking")
async def websocket_endpoint(websocket: WebSocket):
    global camera_system
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            event = json.loads(data)
            action = event.get("action")
            
            if action in ["car_enter", "sync_frame"]:
                if not camera_system:
                    await websocket.send_json({"status": "error", "message": "Hệ thống chưa được cấu hình!"})
                    continue
                
                parking_state = {}
                
                # Quét qua tất cả camera
                for cam_id, cam_data in camera_system.items():
                    cap = cam_data["video_cap"]
                    spots = cam_data["spots"]
                    pipeline = cam_data["pipeline"]
                    
                    # ĐỒNG BỘ HÓA TỐC ĐỘ (DESYNC FIX)
                    # Video chạy ở Frontend là 25 FPS (1 giây có 25 hình).
                    # Websocket gọi mỗi 200ms (5 lần/giây). 
                    # Do đó, mỗi lần gọi, Backend cần phải nhảy qua 5 frame để theo kịp tốc độ của Frontend!
                    for _ in range(4):
                        cap.read() # Đọc bỏ qua 4 frame
                        
                    ret, frame = cap.read() # Đọc frame thứ 5 để xử lý
                    
                    if not ret or frame is None:
                        # Hết video -> Mở lại từ đầu giống như thẻ <video loop>
                        cap.release()
                        cap = cv2.VideoCapture(cam_data["video_path"])
                        cam_data["video_cap"] = cap
                        ret, frame = cap.read()
                        
                        # Reset luôn bộ đệm lịch sử để tránh báo đỏ ảo do quá khứ
                        pipeline.spot_history.clear()
                        
                    # Phân tích frame qua thuật toán SVM
                    updated_spots = pipeline.process_frame(frame, spots)
                    cam_data["spots"] = updated_spots
                    parking_state[cam_id] = updated_spots
                    
                response = {
                    "status": "success",
                    "parking_state": parking_state
                }
                
                # Nếu là yêu cầu đỗ xe, tìm ô trống luân phiên theo thứ tự camera
                if action == "car_enter":
                    empty_spot = None
                    for cam_id, spots in parking_state.items():
                        for spot in spots:
                            if spot['status'] == 'empty':
                                empty_spot = spot['id']
                                break
                        if empty_spot:
                            break # Đã tìm thấy thì dừng vòng lặp ngoài
                            
                    response["closest_empty_spot"] = empty_spot if empty_spot else "BÃI ĐÃ ĐẦY!"
                    
                await websocket.send_json(response)
                
    except WebSocketDisconnect:
        pass

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)