<template>
  <div class="app-container">
    <!-- Toast Notification UI -->
    <transition name="toast-fade">
      <div v-if="toastMsg" class="toast-notification" :class="toastType">
        <span class="toast-icon">{{ toastType === 'error' ? '⚠️' : '✅' }}</span>
        <span>{{ toastMsg }}</span>
      </div>
    </transition>

    <!-- Header -->
    <header class="app-header glass-panel">
      <div class="header-content">
        <h1>Quản Lý Đỗ Xe Thông Minh</h1>
        <p class="subtitle">Đa Phân Khu - Tự động Luân chuyển</p>
      </div>
      <div class="header-badges">
        <span class="badge" :class="sysState">{{ sysState === 'SETUP' ? 'CHẾ ĐỘ CẤU HÌNH' : '🟢 GIÁM SÁT TRỰC TIẾP' }}</span>
      </div>
    </header>

    <!-- TRẠNG THÁI CẤU HÌNH -->
    <main v-if="sysState === 'SETUP'" class="setup-layout">
      <!-- Cột trái: Quản lý danh sách Camera -->
      <aside class="sidebar glass-panel">
        <div class="sidebar-header">
          <h2>Khu Vực Quản Lý</h2>
        </div>
        <div class="camera-list">
          <div 
            v-for="cam in cameras" :key="cam.id" 
            class="camera-item" 
            :class="{ active: activeCam && activeCam.id === cam.id }"
            @click="selectCamera(cam.id)"
          >
            <div class="cam-info">
              <strong>{{ cam.name }}</strong>
              <small :class="cam.videoUrl ? 'text-success' : 'text-danger'">
                {{ cam.videoUrl ? `${cam.spots.length} ô đỗ` : 'Chưa có Video' }}
              </small>
            </div>
            <button class="btn-icon btn-danger" @click.stop="removeCamera(cam.id)" title="Xóa Khu Vực">🗑️</button>
          </div>
        </div>
        
        <div class="action-bottom">
          <button class="btn-primary full-width" @click="addCamera">+ Thêm Khu Vực Mới</button>
          
          <button v-if="cameras.length > 0 && isAllCamerasReady" @click="startSimulation" class="btn-success full-width pulse-anim">
            BẮT ĐẦU GIÁM SÁT
          </button>
          <p v-else class="text-muted text-center text-sm">Cần thêm ít nhất 1 khu vực và tải video lên tất cả khu vực để bắt đầu.</p>
        </div>
      </aside>

      <!-- Cột phải: Editor -->
      <section class="main-editor glass-panel" v-if="activeCam">
        <div class="editor-header">
          <input v-model="activeCam.name" class="cam-name-input" placeholder="Tên khu vực..." />
          
          <div class="editor-tools" v-if="activeCam.videoUrl">
            <button class="btn-secondary" @click="undoSpot" :disabled="activeCam.spots.length === 0">Hoàn Tác Ô Cuối</button>
            <button class="btn-danger" @click="clearSpots" :disabled="activeCam.spots.length === 0">Xóa Tất Cả Ô</button>
            <label class="btn-primary upload-btn">
              Tải Video Khác
              <input type="file" accept="video/mp4" @change="handleVideoUpload" hidden />
            </label>
          </div>
        </div>

        <div v-if="!activeCam.videoUrl" class="upload-placeholder">
          <div 
            class="upload-box"
            :class="{ 'drag-over': isDragging }"
            @dragover.prevent="isDragging = true"
            @dragleave.prevent="isDragging = false"
            @drop.prevent="handleVideoDrop"
          >
            <div class="icon-big">📥</div>
            <h3>Kéo thả video vào đây hoặc tải lên cho {{ activeCam.name }}</h3>
            <p>Khuyên dùng góc quay từ trên cao, định dạng MP4</p>
            <input type="file" accept="video/mp4" @change="handleVideoUpload" class="file-input" />
          </div>
        </div>

        <div v-else class="canvas-container">
          <p class="instruction text-center mb-2">Kéo thả chuột để vẽ ô đỗ xe. Nhấn "Hoàn Tác" để xóa ô vẽ sai.</p>
          <div class="canvas-wrapper" @mousedown="startDrawing" @mousemove="draw" @mouseup="stopDrawing" ref="wrapperRef">
            <video :src="activeCam.videoUrl" controls @loadedmetadata="setupCanvas" ref="videoPlayer"></video>
            <canvas ref="drawCanvas"></canvas>
          </div>
        </div>
      </section>

      <section class="main-editor glass-panel flex-center" v-else>
        <div class="empty-state">
          <div class="icon-big">📹</div>
          <h2>Chưa chọn Khu Vực</h2>
          <p>Hãy chọn một khu vực bên trái hoặc bấm "+ Thêm Khu Vực Mới" để bắt đầu.</p>
        </div>
      </section>
    </main>

    <!-- TRẠNG THÁI LIVE DASHBOARD -->
    <main v-else class="live-layout">
      <!-- Bảng điều khiển và Log -->
      <aside class="dashboard-sidebar glass-panel">
        <button class="btn-simulate pulse-anim full-width" @click="simulateCarEnter" :disabled="isFull">
          {{ isFull ? 'BÃI ĐÃ ĐẦY' : 'CÓ XE VÀO BÃI' }}
        </button>

        <div class="stats-box mt-4">
          <div class="stat-item">
            <span class="stat-label">Tổng số chỗ:</span>
            <span class="stat-value">{{ totalSpots }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label text-success">Đang trống:</span>
            <span class="stat-value text-success">{{ totalEmpty }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label text-danger">Đã có xe:</span>
            <span class="stat-value text-danger">{{ totalSpots - totalEmpty }}</span>
          </div>
        </div>

        <div class="logs-container mt-4">
          <h3>Nhật ký Hoạt động</h3>
          <ul class="logs-list">
            <li v-for="(log, idx) in reversedLogs" :key="idx" :class="log.type">
              <span class="time">[{{ log.time }}]</span> {{ log.msg }}
            </li>
          </ul>
        </div>
        
        <button class="btn-secondary full-width mt-auto" @click="stopSimulation">Quay lại Cấu Hình</button>
      </aside>

      <!-- Lưới Video Grid -->
      <section class="video-grid" :class="'grid-cols-' + Math.min(cameras.length, 2)">
        <div v-for="cam in cameras" :key="cam.id" class="grid-item glass-panel">
          <div class="grid-header">
            <h3 class="grid-title">{{ cam.name }}</h3>
            <span class="stats-badge" :class="getEmptyCount(cam) === 0 ? 'bg-danger' : 'bg-success'">
              {{ getEmptyCount(cam) }}/{{ cam.spots.length }} Trống
            </span>
          </div>
          <div class="live-canvas-wrapper">
            <video :src="cam.videoUrl" autoplay loop muted class="live-video"></video>
            <svg class="overlay-svg" :viewBox="`0 0 ${cam.vidWidth} ${cam.vidHeight}`">
              <g v-for="spot in cam.spots" :key="spot.id">
                <rect 
                  :x="spot.box[0]" 
                  :y="spot.box[1]" 
                  :width="spot.box[2]" 
                  :height="spot.box[3]"
                  :class="[ 'live-spot', spot.status, { 'target-blink': spot.id === targetSpotId } ]"
                />
                <!-- Nền đen mờ dưới text để dễ đọc -->
                <rect
                  :x="spot.box[0] + 5"
                  :y="spot.box[1] + 5"
                  width="70"
                  height="30"
                  fill="rgba(0,0,0,0.6)"
                  rx="4"
                />
                <text 
                  :x="spot.box[0] + 10" 
                  :y="spot.box[1] + 25"
                  class="spot-label-text"
                  :fill="spot.status === 'empty' ? '#00FF00' : '#FF4444'"
                >
                  {{ spot.id }}
                </text>
              </g>
            </svg>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted, nextTick } from 'vue';

// --- STATE ---
const sysState = ref('SETUP'); // 'SETUP' or 'LIVE'
const cameras = ref([]);
const activeCamId = ref(null);
const globalSpotCounter = ref(1);

// Lấy camera đang được chọn
const activeCam = computed(() => cameras.value.find(c => c.id === activeCamId.value));

// Điều kiện bắt đầu: phải có camera, và mọi camera đều có videoUrl
const isAllCamerasReady = computed(() => {
  return cameras.value.length > 0 && cameras.value.every(c => c.videoUrl);
});

// Thống kê tổng
const totalSpots = computed(() => cameras.value.reduce((sum, cam) => sum + cam.spots.length, 0));
const totalEmpty = computed(() => cameras.value.reduce((sum, cam) => sum + getEmptyCount(cam), 0));
const isFull = computed(() => totalSpots.value > 0 && totalEmpty.value === 0);

// Log & Mock Logic
const logs = ref([]);
const reversedLogs = computed(() => [...logs.value].reverse());
const targetSpotId = ref(null);
let mockInterval = null;
let autoFillTimeout = null;

// Toast logic
const toastMsg = ref('');
const toastType = ref('error');
let toastTimer = null;

const showToast = (msg, type = 'error') => {
  toastMsg.value = msg;
  toastType.value = type;
  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toastMsg.value = '';
  }, 3500);
};

// Thêm log helper
const addLog = (msg, type = 'info') => {
  const now = new Date();
  const time = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`;
  logs.value.push({ time, msg, type });
  if (logs.value.length > 50) logs.value.shift();
};

const getEmptyCount = (cam) => cam.spots.filter(s => s.status === 'empty').length;

// --- QUẢN LÝ CAMERA ---
const generateId = () => Math.random().toString(36).substr(2, 9);

const addCamera = () => {
  const count = cameras.value.length + 1;
  const newCam = {
    id: generateId(),
    name: `Khu vực ${count} (Tầng ${count})`,
    videoFile: null,
    videoUrl: null,
    vidWidth: 1920,
    vidHeight: 1080,
    spots: []
  };
  cameras.value.push(newCam);
  activeCamId.value = newCam.id;
};

const removeCamera = (id) => {
  cameras.value = cameras.value.filter(c => c.id !== id);
  if (activeCamId.value === id) {
    activeCamId.value = cameras.value.length > 0 ? cameras.value[0].id : null;
  }
};

const selectCamera = (id) => {
  activeCamId.value = id;
  // Khi đổi tab, canvas cần được redraw
  nextTick(() => {
    if (activeCam.value && activeCam.value.videoUrl && drawCanvas.value) {
      setupCanvas();
    }
  });
};

// --- LOGIC VẼ CANVAS (Dành cho Active Camera) ---
const videoPlayer = ref(null);
const drawCanvas = ref(null);
let isDrawing = false;
let startX = 0, startY = 0;

const handleVideoUpload = (event) => {
  const file = event.target.files[0];
  if (file && activeCam.value) {
    activeCam.value.videoFile = file;
    activeCam.value.videoUrl = URL.createObjectURL(file);
    activeCam.value.spots = [];
  }
};

const isDragging = ref(false);
const handleVideoDrop = (event) => {
  isDragging.value = false;
  const files = event.dataTransfer.files;
  if (files.length > 0 && activeCam.value) {
    const file = files[0];
    if (file.type.startsWith('video/') || file.name.endsWith('.mp4')) {
      activeCam.value.videoFile = file;
      activeCam.value.videoUrl = URL.createObjectURL(file);
      activeCam.value.spots = [];
    } else {
      showToast("Vui lòng tải lên đúng định dạng Video MP4!", "error");
    }
  }
};



const setupCanvas = () => {
  if (!videoPlayer.value || !drawCanvas.value || !activeCam.value) return;
  const video = videoPlayer.value;
  const canvas = drawCanvas.value;
  
  canvas.width = video.clientWidth;
  canvas.height = video.clientHeight;
  
  activeCam.value.vidWidth = video.videoWidth || 1920;
  activeCam.value.vidHeight = video.videoHeight || 1080;
  
  redrawSavedSpots();
};

const startDrawing = (e) => {
  if (!activeCam.value) return;
  isDrawing = true;
  const rect = drawCanvas.value.getBoundingClientRect();
  startX = e.clientX - rect.left;
  startY = e.clientY - rect.top;
};

const draw = (e) => {
  if (!isDrawing || !activeCam.value) return;
  const canvas = drawCanvas.value;
  const ctx = canvas.getContext('2d');
  const rect = canvas.getBoundingClientRect();
  const currentX = e.clientX - rect.left;
  const currentY = e.clientY - rect.top;

  ctx.clearRect(0, 0, canvas.width, canvas.height);
  redrawSavedSpots();

  ctx.strokeStyle = '#00FF00';
  ctx.lineWidth = 2;
  ctx.strokeRect(startX, startY, currentX - startX, currentY - startY);
};

const stopDrawing = (e) => {
  if (!isDrawing || !activeCam.value) return;
  isDrawing = false;
  
  const rect = drawCanvas.value.getBoundingClientRect();
  const endX = e.clientX - rect.left;
  const endY = e.clientY - rect.top;
  
  const width = endX - startX;
  const height = endY - startY;

  // Nếu khung đủ to, lưu lại
  if (Math.abs(width) > 20 && Math.abs(height) > 20) {
    const scaleX_ratio = activeCam.value.vidWidth / videoPlayer.value.clientWidth;
    const scaleY_ratio = activeCam.value.vidHeight / videoPlayer.value.clientHeight;

    activeCam.value.spots.push({
      id: `K${String(globalSpotCounter.value).padStart(2, '0')}`,
      status: "empty", // Mặc định trống
      box: [
        Math.round(Math.min(startX, endX) * scaleX_ratio), 
        Math.round(Math.min(startY, endY) * scaleY_ratio), 
        Math.round(Math.abs(width) * scaleX_ratio), 
        Math.round(Math.abs(height) * scaleY_ratio)
      ]
    });
    globalSpotCounter.value++;
  }
  
  redrawSavedSpots();
};

const redrawSavedSpots = () => {
  if (!drawCanvas.value || !activeCam.value) return;
  const canvas = drawCanvas.value;
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const scaleX_ratio = videoPlayer.value.clientWidth / activeCam.value.vidWidth;
  const scaleY_ratio = videoPlayer.value.clientHeight / activeCam.value.vidHeight;

  activeCam.value.spots.forEach(spot => {
    const [x, y, w, h] = spot.box;
    ctx.strokeStyle = '#00FF00';
    ctx.lineWidth = 2;
    ctx.strokeRect(x * scaleX_ratio, y * scaleY_ratio, w * scaleX_ratio, h * scaleY_ratio);
    
    // Vẽ viền chữ
    ctx.fillStyle = 'rgba(0,0,0,0.6)';
    ctx.fillRect((x * scaleX_ratio) + 5, (y * scaleY_ratio) + 5, 50, 25);

    ctx.fillStyle = '#00FF00';
    ctx.font = '14px Arial';
    ctx.fillText(spot.id, (x * scaleX_ratio) + 10, (y * scaleY_ratio) + 22);
  });
};

const undoSpot = () => {
  if (activeCam.value && activeCam.value.spots.length > 0) {
    activeCam.value.spots.pop();
    globalSpotCounter.value--;
    redrawSavedSpots();
  }
};

const clearSpots = () => {
  if (activeCam.value) {
    globalSpotCounter.value -= activeCam.value.spots.length;
    activeCam.value.spots = [];
    redrawSavedSpots();
  }
};

const socket = ref(null);
const isConnecting = ref(false);

const startSimulation = async () => {
  if (totalSpots.value === 0) {
    showToast("LỖI: Vui lòng cấu hình ít nhất 1 ô đỗ xe trước khi bắt đầu!", "error");
    return;
  }
  
  isConnecting.value = true;
  
  const formData = new FormData();
  const configMap = {};
  
  cameras.value.forEach(cam => {
    formData.append(`video_${cam.id}`, cam.videoFile);
    configMap[cam.id] = cam.spots.map(s => ({...s, status: 'empty'}));
  });
  
  formData.append('config', JSON.stringify(configMap));

  try {
    const res = await fetch("http://localhost:8000/upload-config-multi", {
      method: "POST",
      body: formData
    });
    
    if (res.ok) {
      sysState.value = 'LIVE';
      logs.value = [];
      targetSpotId.value = null;
      addLog("Đã nạp dữ liệu AI. Khởi động luồng xử lý Đa Phân Khu...", "success");
      
      connectWebSocket();
    } else {
      addLog("LỖI: Không thể tải cấu hình lên Backend!", "error");
    }
  } catch (e) {
    showToast("LỖI KẾT NỐI: Không tìm thấy Backend (main.py). Vui lòng khởi động lại Backend!", "error");
  } finally {
    isConnecting.value = false;
  }
};

const connectWebSocket = () => {
  socket.value = new WebSocket('ws://localhost:8000/ws/parking');
  
  socket.value.onopen = () => {
    mockInterval = setInterval(() => {
      if (socket.value && socket.value.readyState === WebSocket.OPEN) {
        socket.value.send(JSON.stringify({ action: 'sync_frame' }));
      }
    }, 200); 
  };
  
  socket.value.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.status === 'success') {
      
      for (const camId in data.parking_state) {
        const camData = cameras.value.find(c => c.id === camId);
        if (camData) {
          camData.spots = data.parking_state[camId];
        }
      }
      
      if (data.closest_empty_spot) {
        targetSpotId.value = data.closest_empty_spot;
        
        // Tắt nhấp nháy sau 5 giây để trả lại trạng thái thường
        clearTimeout(autoFillTimeout);
        autoFillTimeout = setTimeout(() => {
          targetSpotId.value = null;
        }, 5000);
      }
    }
  };

  socket.value.onclose = () => {
    clearInterval(mockInterval);
  };
};

const stopSimulation = () => {
  sysState.value = 'SETUP';
  clearInterval(mockInterval);
  clearTimeout(autoFillTimeout);
  if (socket.value) {
    socket.value.close();
  }
};

const simulateCarEnter = () => {
  addLog("🚗 Yêu cầu đỗ xe gửi lên mô hình AI...", "info");
  if (socket.value && socket.value.readyState === WebSocket.OPEN) {
    socket.value.send(JSON.stringify({ action: 'car_enter' }));
  }
};

onUnmounted(() => {
  clearInterval(mockInterval);
  clearTimeout(autoFillTimeout);
  if (socket.value) socket.value.close();
});

// Init 1 camera mặc định
addCamera();
</script>

<style scoped>
:global(body) { margin: 0; padding: 0; width: 100vw; overflow-x: hidden; }
:global(#app) { width: 100%; height: 100%; }

/* --- DARK THEME & GLOBALS --- */
.app-container {
  font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #0f172a; /* Slate 900 */
  color: #e2e8f0;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

/* --- TOAST NOTIFICATION --- */
.toast-notification {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
  z-index: 9999;
  box-shadow: 0 10px 25px rgba(0,0,0,0.5);
  font-size: 15px;
}
.toast-notification.error { background: rgba(239, 68, 68, 0.95); color: white; border: 1px solid #dc2626; backdrop-filter: blur(5px);}
.toast-notification.success { background: rgba(16, 185, 129, 0.95); color: white; border: 1px solid #059669; backdrop-filter: blur(5px);}
.toast-fade-enter-active, .toast-fade-leave-active { transition: all 0.3s ease; }
.toast-fade-enter-from, .toast-fade-leave-to { opacity: 0; transform: translate(-50%, -20px); }

/* --- HEADER --- */
.glass-panel {
  background: rgba(30, 41, 59, 0.7); /* Slate 800 */
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
}

/* --- HEADER --- */
.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 30px;
  margin: 15px;
}
.header-content h1 {
  margin: 0;
  font-size: 24px;
  color: #38bdf8; /* Light blue neon */
  text-shadow: 0 0 10px rgba(56, 189, 248, 0.4);
}
.subtitle {
  margin: 5px 0 0 0;
  color: #94a3b8;
  font-size: 14px;
}
.badge {
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: bold;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 1px;
}
.badge.SETUP { background: #334155; color: #cbd5e1; border: 1px solid #475569; }
.badge.LIVE { background: rgba(34, 197, 94, 0.2); color: #4ade80; border: 1px solid #4ade80; box-shadow: 0 0 15px rgba(34,197,94,0.3); }

/* --- BUTTONS --- */
button {
  cursor: pointer;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.2s ease;
  padding: 10px 16px;
}
button:disabled { opacity: 0.5; cursor: not-allowed; }
.full-width { width: 100%; }
.mt-2 { margin-top: 10px; }
.mt-3 { margin-top: 15px; }
.mt-4 { margin-top: 20px; }
.mt-auto { margin-top: auto; }
.mb-2 { margin-bottom: 10px; }
.text-center { text-align: center; }

.btn-primary { background: #3b82f6; color: white; }
.btn-primary:hover:not(:disabled) { background: #2563eb; }
.btn-secondary { background: #475569; color: white; }
.btn-secondary:hover:not(:disabled) { background: #334155; }
.btn-danger { background: #ef4444; color: white; }
.btn-danger:hover:not(:disabled) { background: #dc2626; }
.btn-success { background: #10b981; color: white; font-size: 16px; }
.btn-success:hover:not(:disabled) { background: #059669; }

.btn-icon { padding: 6px; border-radius: 6px; font-size: 14px; }
.upload-btn { display: inline-block; cursor: pointer; padding: 10px 16px; border-radius: 8px; font-size: 14px; font-weight: 600;}

/* --- LAYOUTS --- */
.setup-layout, .live-layout {
  display: flex;
  flex: 1;
  padding: 0 15px 15px 15px;
  gap: 15px;
  overflow: hidden;
}

.sidebar {
  width: 320px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.sidebar-header h2 { margin-top: 0; color: #f8fafc; font-size: 18px; border-bottom: 1px solid #334155; padding-bottom: 10px;}

/* --- CAMERA LIST --- */
.camera-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 15px;
  padding-right: 5px;
}
.camera-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(15, 23, 42, 0.6);
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #334155;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}
.camera-item:hover { background: rgba(30, 41, 59, 0.9); }
.camera-item.active { border-color: #38bdf8; background: rgba(56, 189, 248, 0.1); }
.cam-info strong { display: block; color: #f1f5f9; }
.text-success { color: #4ade80; }
.text-danger { color: #f87171; }
.text-muted { color: #94a3b8; }
.text-sm { font-size: 13px; }

.action-bottom {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-top: auto;
}

/* --- EDITOR --- */
.main-editor {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 20px;
  overflow: hidden;
}
.flex-center { justify-content: center; align-items: center; }

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.cam-name-input {
  background: transparent;
  border: none;
  border-bottom: 2px solid #334155;
  color: #fff;
  font-size: 24px;
  font-weight: bold;
  padding: 5px;
  outline: none;
  width: 300px;
}
.cam-name-input:focus { border-color: #38bdf8; }

.editor-tools {
  display: flex;
  gap: 15px;
  align-items: center;
}
.editor-tools button, .editor-tools label {
  flex: 1 1 0;
  box-sizing: border-box;
  text-align: center;
  margin: 0;
  white-space: nowrap;
}

.empty-state { text-align: center; color: #94a3b8; }
.icon-big { font-size: 60px; margin-bottom: 15px; opacity: 0.5; }
.upload-placeholder { display: flex; justify-content: center; align-items: center; flex: 1; }
.upload-box { text-align: center; border: 2px dashed #475569; padding: 40px; border-radius: 12px; background: rgba(15,23,42,0.4); transition: all 0.3s ease; }
.upload-box.drag-over { border-color: #38bdf8; background: rgba(56, 189, 248, 0.1); }

/* --- CANVAS & VIDEO SETUP --- */
.canvas-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  overflow: hidden;
}
.instruction { color: #38bdf8; font-weight: 500; }
.canvas-wrapper { position: relative; display: inline-flex; max-width: 100%; max-height: calc(100vh - 250px); }
.canvas-wrapper video { max-width: 100%; max-height: 100%; border-radius: 8px; outline: 2px solid #334155; }
.canvas-wrapper canvas { position: absolute; top: 0; left: 0; cursor: crosshair; }

/* --- LIVE DASHBOARD STYLES --- */
.dashboard-sidebar { width: 350px; padding: 20px; display: flex; flex-direction: column;}

.btn-simulate { 
  background: linear-gradient(135deg, #0ea5e9, #2563eb); 
  color: white; 
  font-size: 18px; 
  padding: 16px; 
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(14, 165, 233, 0.4);
}

.stats-box { background: rgba(15, 23, 42, 0.6); padding: 15px; border-radius: 10px;}
.stat-item { display: flex; justify-content: space-between; margin-bottom: 8px; font-weight: 600; font-size: 15px;}
.stat-item:last-child { margin-bottom: 0; }
.stat-value { font-size: 18px; }

.logs-container { flex: 1; background: rgba(0,0,0,0.3); border-radius: 10px; padding: 15px; overflow-y: auto; border: 1px solid #334155;}
.logs-container h3 { margin-top: 0; font-size: 16px; color: #cbd5e1; border-bottom: 1px solid #334155; padding-bottom: 10px;}
.logs-list { list-style: none; padding: 0; margin: 0; font-size: 14px;}
.logs-list li { margin-bottom: 8px; padding-bottom: 8px; border-bottom: 1px dashed #334155; line-height: 1.4;}
.logs-list li.info { color: #e2e8f0; }
.logs-list li.success { color: #4ade80; }
.logs-list li.error { color: #f87171; }
.logs-list .time { color: #94a3b8; font-family: monospace; }

/* GRID HIỂN THỊ CAMERA */
.video-grid {
  flex: 1;
  display: grid;
  gap: 15px;
  overflow-y: auto;
}
.grid-cols-1 { grid-template-columns: 1fr; }
.grid-cols-2 { grid-template-columns: 1fr 1fr; }

.grid-item { display: flex; flex-direction: column; padding: 15px; }
.grid-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;}
.grid-title { margin: 0; font-size: 18px; color: #fff;}
.stats-badge { padding: 4px 10px; border-radius: 12px; font-size: 13px; font-weight: bold;}
.bg-success { background: rgba(34, 197, 94, 0.2); color: #4ade80; }
.bg-danger { background: rgba(239, 68, 68, 0.2); color: #f87171; }

.live-canvas-wrapper { position: relative; width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; background: #000; border-radius: 8px; overflow: hidden;}
.live-video { max-width: 100%; max-height: 100%; object-fit: contain;}
.overlay-svg { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; }

/* SVG SPOTS STYLES */
.live-spot { fill: transparent; stroke-width: 4px; transition: all 0.3s ease; }
.empty { stroke: #00FF00; }
.occupied { stroke: #FF3333; fill: rgba(255, 0, 0, 0.3); stroke-width: 6px; }

/* HIỆU ỨNG NHẤP NHÁY CHỈ ĐỊNH */
.target-blink {
  stroke: #00FFFF !important;
  stroke-width: 8px !important;
  animation: glowingBlink 0.8s infinite alternate; 
}
@keyframes glowingBlink {
  0% { fill: rgba(0, 255, 255, 0.1); box-shadow: 0 0 5px #00FFFF; }
  100% { fill: rgba(0, 255, 255, 0.6); filter: drop-shadow(0 0 15px #00FFFF); }
}
.spot-label-text { font-family: 'Inter', sans-serif; font-weight: 800; }

.pulse-anim { animation: pulseBtn 2s infinite; }
@keyframes pulseBtn {
  0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(14, 165, 233, 0.7); }
  70% { transform: scale(1.02); box-shadow: 0 0 0 10px rgba(14, 165, 233, 0); }
  100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(14, 165, 233, 0); }
}
</style>