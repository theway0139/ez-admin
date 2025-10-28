<template>
  <div class="rtsp-player-container">
    <div class="header">
      <h1>RTSP 视频流播放器</h1>
      <p>实时视频流展示</p>
    </div>
    
    <div class="video-container">
      <div class="video-wrapper">
        <video
          ref="videoPlayer"
          class="video-player"
          controls
          autoplay
          muted
          playsinline
        >
          您的浏览器不支持视频播放。
        </video>
        
        <div class="video-info">
          <div class="info-item">
            <span class="label">RTSP地址:</span>
            <span class="value">{{ rtspUrl }}</span>
          </div>
          <div class="info-item">
            <span class="label">连接状态:</span>
            <span class="value" :class="connectionStatus">{{ statusText }}</span>
          </div>
        </div>
      </div>
      
      <div class="controls">
        <el-button type="primary" @click="startPlay" :disabled="isPlaying">
          <el-icon><VideoPlay /></el-icon>
          开始播放
        </el-button>
        <el-button type="danger" @click="stopPlay" :disabled="!isPlaying">
          <el-icon><VideoPause /></el-icon>
          停止播放
        </el-button>
        <el-button @click="refreshStream">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { VideoPlay, VideoPause, Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// 响应式数据
const videoPlayer = ref(null)
const isPlaying = ref(false)
const connectionStatus = ref('disconnected')
const rtspUrl = 'rtsp://admin:okwy1234@192.168.1.64:554/Streaming/Channels/101/H264'

// 计算属性
const statusText = computed(() => {
  switch (connectionStatus.value) {
    case 'connecting':
      return '连接中...'
    case 'connected':
      return '已连接'
    case 'disconnected':
      return '未连接'
    case 'error':
      return '连接错误'
    default:
      return '未知状态'
  }
})

// 方法
const startPlay = async () => {
  try {
    connectionStatus.value = 'connecting'
    
    if (videoPlayer.value) {
      // 由于浏览器安全限制，直接播放RTSP流需要通过WebRTC或HLS转换
      // 这里提供一个简单的实现方案
      
      // 使用HLS.js播放转换后的HLS流
      const hlsUrl = '/streams/cam1/index.m3u8'
      
      const HlsGlobal = window.Hls
      if (HlsGlobal && HlsGlobal.isSupported()) {
        const hls = new HlsGlobal({
          maxBufferLength: 5,
          liveSyncDurationCount: 2,
        })
        hls.loadSource(hlsUrl)
        hls.attachMedia(videoPlayer.value)
        hls.on(HlsGlobal.Events.MANIFEST_PARSED, async () => {
          try {
            await videoPlayer.value.play()
            isPlaying.value = true
            connectionStatus.value = 'connected'
          } catch (e) {
            console.error(e)
          }
        })
        hls.on(HlsGlobal.Events.ERROR, (event, data) => {
          console.error('HLS error', data)
          connectionStatus.value = 'error'
          ElMessage.error('HLS播放错误，请确认转码服务是否运行')
        })
      } else if (videoPlayer.value.canPlayType('application/vnd.apple.mpegURL')) {
        // Safari原生支持HLS
        videoPlayer.value.src = hlsUrl
        await videoPlayer.value.play()
        isPlaying.value = true
        connectionStatus.value = 'connected'
      } else {
        connectionStatus.value = 'error'
        ElMessage.error('当前浏览器不支持HLS，请使用Chrome或Safari')
      }
    }
  } catch (error) {
    console.error('播放失败:', error)
    connectionStatus.value = 'error'
    ElMessage.error('视频播放失败，请检查网络连接')
  }
}

const stopPlay = () => {
  if (videoPlayer.value) {
    videoPlayer.value.pause()
    videoPlayer.value.currentTime = 0
    isPlaying.value = false
    connectionStatus.value = 'disconnected'
  }
}

const refreshStream = () => {
  stopPlay()
  setTimeout(() => {
    startPlay()
  }, 1000)
}

// 生命周期
onMounted(() => {
  // 监听视频事件
  if (videoPlayer.value) {
    videoPlayer.value.addEventListener('loadstart', () => {
      connectionStatus.value = 'connecting'
    })
    
    videoPlayer.value.addEventListener('canplay', () => {
      connectionStatus.value = 'connected'
    })
    
    videoPlayer.value.addEventListener('error', () => {
      connectionStatus.value = 'error'
      isPlaying.value = false
    })
    
    videoPlayer.value.addEventListener('ended', () => {
      isPlaying.value = false
      connectionStatus.value = 'disconnected'
    })
  }
})

onUnmounted(() => {
  stopPlay()
})
</script>

<style scoped>
.rtsp-player-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  text-align: center;
  margin-bottom: 30px;
}

.header h1 {
  color: #303133;
  margin-bottom: 10px;
}

.header p {
  color: #909399;
  font-size: 14px;
}

.video-container {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.video-wrapper {
  position: relative;
  background: #000;
}

.video-player {
  width: 100%;
  height: 500px;
  object-fit: contain;
  background: #000;
}

.video-info {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 10px;
  border-radius: 4px;
  font-size: 12px;
}

.info-item {
  margin-bottom: 5px;
}

.info-item:last-child {
  margin-bottom: 0;
}

.label {
  font-weight: bold;
  margin-right: 5px;
}

.value {
  color: #fff;
}

.value.connecting {
  color: #E6A23C;
}

.value.connected {
  color: #67C23A;
}

.value.disconnected {
  color: #909399;
}

.value.error {
  color: #F56C6C;
}

.controls {
  padding: 20px;
  text-align: center;
  background: #f5f7fa;
}

.controls .el-button {
  margin: 0 10px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .rtsp-player-container {
    padding: 10px;
  }
  
  .video-player {
    height: 300px;
  }
  
  .controls .el-button {
    margin: 5px;
    display: block;
    width: 100%;
    max-width: 200px;
  }
}
</style>