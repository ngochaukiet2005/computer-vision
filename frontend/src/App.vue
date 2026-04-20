<template>
  <div class="container">
    <h1>Hệ Thống Đỗ Xe Thông Minh (Core CV) 🚗</h1>

    <div v-if="!isConfigured" class="setup-section">
      <div class="upload-box">
        <label>Chọn video bãi đỗ xe (Góc quay từ trên cao): </label>
        <input type="file" accept="video/mp4" @change="handleVideoUpload" />
      </div>

      <div class="video-container" v-show="videoUrl">
        <p class="instruction">
          👉 <strong>BƯỚC 1:</strong> Dùng chuột <strong>KÉO THẢ</strong> để vẽ khung chữ nhật bao quanh các ô đỗ xe.<br/>
          👉 <strong>BƯỚC 2:</strong> Nhấn "Lưu Cấu Hình" để bắt đầu hệ thống.
        </p>
        
        <div class="canvas-wrapper" @mousedown="startDrawing" @mousemove="draw" @mouseup="stopDrawing">
          <video ref="videoPlayer" :src="videoUrl" controls @loadedmetadata="setupCanvas"></video>
          <canvas ref="drawCanvas"></canvas>
        </div>
        
        <button v-if="spots.length > 0" @click="submitConfiguration" class="btn-primary" :disabled="isLoading">
          {{ isLoading ? '⏳ Đang khởi tạo...' : '💾 Lưu Cấu Hình & Bắt Đầu' }}
        </button>
      </div>
    </div>

    <div v-else class="run-section">
      <div class="control-panel">
        <button @click="simulateCarEnter" class="btn-simulate">
          🚗 CÓ XE VÀO BÃI (Cấp quyền đỗ)
        </button>
        <div class="instruction-text">
          👉 Vị trí ô trống được chỉ định: 
          <strong :class="{'blink-text': closestSpot !== 'Đang chờ...' && closestSpot !== 'BÃI ĐÃ ĐẦY!'}">
            {{ closestSpot }}
          </strong>
        </div>
      </div>

      <div class="live-dashboard">
        <div class="canvas-wrapper">
          <video :src="videoUrl" autoplay loop muted class="playing-vid" ref="runVideoPlayer"></video>
          
          <svg class="overlay-svg" :viewBox="`0 0 ${vidWidth} ${vidHeight}`">
            <g v-for="spot in parkingState" :key="spot.id">
              <rect 
                :x="spot.box[0]" 
                :y="spot.box[1]" 
                :width="spot.box[2]" 
                :height="spot.box[3]"
                :class="[
                  'live-spot', 
                  spot.status, 
                  { 'target-blink': spot.id === closestSpot }
                ]"
              />
              <text 
                :x="spot.box[0]" 
                :y="spot.box[1] - 10"
                class="spot-label-text"
                :font-size="vidWidth > 1200 ? '30px' : '18px'" 
              >
                {{ spot.id }} - {{ spot.status === 'empty' ? 'Trống' : 'Có Xe' }}
              </text>
            </g>
          </svg>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue';

const isConfigured = ref(false);
const isLoading = ref(false);
const videoFile = ref(null);
const videoUrl = ref('');
const videoPlayer = ref(null);
const drawCanvas = ref(null);

const spots = ref([]);
let isDrawing = false;
let startX = 0, startY = 0;
let spotCounter = 1;

// Lưu lại kích thước gốc của video để nhúng vào viewBox của SVG
const vidWidth = ref(1920);
const vidHeight = ref(1080);

const socket = ref(null);
const closestSpot = ref('Đang chờ...');
const parkingState = ref([]);

// --- GIAI ĐOẠN 1: VẼ CANVAS ---
const handleVideoUpload = (event) => {
  const file = event.target.files[0];
  if (file) {
    videoFile.value = file;
    videoUrl.value = URL.createObjectURL(file);
    spots.value = [];
    spotCounter = 1;
  }
};

const setupCanvas = () => {
  const video = videoPlayer.value;
  const canvas = drawCanvas.value;
  canvas.width = video.clientWidth;
  canvas.height = video.clientHeight;
  
  // Lấy độ phân giải gốc của video
  vidWidth.value = video.videoWidth;
  vidHeight.value = video.videoHeight;
};

const startDrawing = (e) => {
  isDrawing = true;
  const rect = drawCanvas.value.getBoundingClientRect();
  startX = e.clientX - rect.left;
  startY = e.clientY - rect.top;
};

const draw = (e) => {
  if (!isDrawing) return;
  const canvas = drawCanvas.value;
  const ctx = canvas.getContext('2d');
  const rect = canvas.getBoundingClientRect();
  const currentX = e.clientX - rect.left;
  const currentY = e.clientY - rect.top;

  ctx.clearRect(0, 0, canvas.width, canvas.height);
  redrawSavedSpots(ctx);

  ctx.strokeStyle = '#00FF00';
  ctx.lineWidth = 2;
  ctx.strokeRect(startX, startY, currentX - startX, currentY - startY);
};

const stopDrawing = (e) => {
  if (!isDrawing) return;
  isDrawing = false;
  
  const rect = drawCanvas.value.getBoundingClientRect();
  const endX = e.clientX - rect.left;
  const endY = e.clientY - rect.top;
  
  const width = endX - startX;
  const height = endY - startY;

  if (Math.abs(width) > 20 && Math.abs(height) > 20) {
    const scaleX_ratio = vidWidth.value / videoPlayer.value.clientWidth;
    const scaleY_ratio = vidHeight.value / videoPlayer.value.clientHeight;

    spots.value.push({
      id: `A-${String(spotCounter).padStart(2, '0')}`,
      status: "empty",
      box: [
        Math.round(Math.min(startX, endX) * scaleX_ratio), 
        Math.round(Math.min(startY, endY) * scaleY_ratio), 
        Math.round(Math.abs(width) * scaleX_ratio), 
        Math.round(Math.abs(height) * scaleY_ratio)
      ]
    });
    spotCounter++;
  }
  
  const ctx = drawCanvas.value.getContext('2d');
  ctx.clearRect(0, 0, drawCanvas.value.width, drawCanvas.value.height);
  redrawSavedSpots(ctx);
};

const redrawSavedSpots = (ctx) => {
  const scaleX_ratio = videoPlayer.value.clientWidth / vidWidth.value;
  const scaleY_ratio = videoPlayer.value.clientHeight / vidHeight.value;

  spots.value.forEach(spot => {
    const [x, y, w, h] = spot.box;
    ctx.strokeStyle = '#00FF00';
    ctx.lineWidth = 2;
    ctx.strokeRect(x * scaleX_ratio, y * scaleY_ratio, w * scaleX_ratio, h * scaleY_ratio);
    ctx.fillStyle = '#00FF00';
    ctx.font = '16px Arial';
    ctx.fillText(spot.id, x * scaleX_ratio, (y * scaleY_ratio) - 5);
  });
};

// --- GỬI DỮ LIỆU & BẮT ĐẦU ---
const submitConfiguration = async () => {
  isLoading.value = true;
  const formData = new FormData();
  formData.append('video', videoFile.value);
  formData.append('rois', JSON.stringify(spots.value));

  try {
    const response = await fetch('http://localhost:8000/upload-config', { method: 'POST', body: formData });
    if (response.ok) {
      isConfigured.value = true;
      parkingState.value = spots.value; // Gán tạm để giữ lại khung xanh trước khi websocket trả về
      connectWebSocket();
    }
  } catch (error) {
    alert("Lỗi Backend!");
  } finally {
    isLoading.value = false;
  }
};

// --- WEBSOCKET & XỬ LÝ NHẤP NHÁY ---
let syncInterval = null; // Biến lưu bộ đếm nhịp
const connectWebSocket = () => {
  socket.value = new WebSocket('ws://localhost:8000/ws/parking');
  
  socket.value.onopen = () => {
    closestSpot.value = 'Đang phân tích bãi đỗ...';
    
    // BẬT TÍNH NĂNG THỜI GIAN THỰC (REAL-TIME)
    // Cứ 150ms (khoảng 6-7 FPS) sẽ tự động gửi yêu cầu quét ảnh 1 lần
    syncInterval = setInterval(() => {
      if (socket.value && socket.value.readyState === WebSocket.OPEN) {
        socket.value.send(JSON.stringify({ action: 'sync_frame' }));
      }
    }, 150);
  };
  
  socket.value.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.status === 'success') {
      // Chỉ cập nhật trạng thái Đỏ/Xanh của các ô
      parkingState.value = data.parking_state; 
      if (data.closest_empty_spot) {
        closestSpot.value = data.closest_empty_spot;
      }
    }
  };

  socket.value.onclose = () => {
    clearInterval(syncInterval); // Tắt bộ đếm khi mất kết nối
  };
};

const simulateCarEnter = () => {
  if (socket.value && socket.value.readyState === WebSocket.OPEN) {
    // Khi bấm nút "CÓ XE VÀO BÃI", ta gửi lệnh riêng để tìm ô trống
    socket.value.send(JSON.stringify({ action: 'car_enter' }));
  }
};
</script>

<style scoped>
.container { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; text-align: center; }
.upload-box { margin: 20px 0; padding: 20px; background: #e9ecef; border-radius: 8px; font-weight: bold;}
.instruction { color: #d32f2f; font-size: 16px; margin-bottom: 15px; }

/* FIX LỖI Ở ĐÂY: Dùng inline-flex để xóa khoảng trắng thừa bên dưới video */
.canvas-wrapper { position: relative; display: inline-flex; margin-bottom: 20px; width: 100%; justify-content: center; }
video { max-width: 100%; max-height: 700px; border-radius: 8px; outline: 3px solid #ccc; display: block;}
canvas { position: absolute; top: 0; left: 50%; transform: translateX(-50%); cursor: crosshair; }

.btn-primary { padding: 12px 24px; background: #28a745; color: white; border: none; font-size: 16px; cursor: pointer; border-radius: 5px; font-weight: bold;}
.btn-simulate { padding: 15px 30px; background: #007bff; color: white; border: none; font-size: 18px; cursor: pointer; border-radius: 5px; font-weight: bold; width: 100%;}
.btn-simulate:hover { background: #0056b3; }

.control-panel { margin: 20px 0; padding: 20px; background-color: #f8f9fa; border-radius: 8px; border: 2px solid #007bff;}
.instruction-text { margin-top: 15px; font-size: 20px; color: #28a745; }

.overlay-svg { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; }
.live-spot { fill: transparent; stroke-width: 3px; transition: all 0.3s ease; }

/* Trạng thái bình thường */
.empty { stroke: #28a745; } /* Xanh bình thường */
.occupied { stroke: #FF0000; fill: rgba(255, 0, 0, 0.3); stroke-width: 5px; } /* Đỏ cho ô có xe */

/* HIỆU ỨNG NHẤP NHÁY CHO Ô ĐƯỢC CHỈ ĐỊNH */
.target-blink {
  stroke: #00FF00 !important;
  stroke-width: 8px !important;
  animation: glowingBlink 0.6s infinite alternate; 
}

@keyframes glowingBlink {
  0% {
    fill: rgba(0, 255, 0, 0.1);
    box-shadow: 0 0 5px #00FF00;
  }
  100% {
    fill: rgba(0, 255, 0, 0.5);
    filter: drop-shadow(0 0 10px #00FF00); /* Glow effect */
  }
}

.blink-text {
  color: #00FF00;
  animation: textBlink 0.6s infinite alternate;
}

@keyframes textBlink {
  0% { opacity: 1; }
  100% { opacity: 0.5; }
}

.spot-label-text { font-family: Arial; font-weight: bold; fill: #fff; text-shadow: 2px 2px 4px #000; }
</style>