<template>
  <div class="alarm-events-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">报警事件管理</h1>
        <p class="page-description">实时监控和报警事件处理</p>
      </div>
      <div class="header-right">
        <el-tag :type="analysisStatus === 'running' ? 'success' : 'info'" size="large" style="margin-right: 10px">
          视频分析服务: {{ analysisStatus === 'running' ? '运行中' : '已停止' }}
        </el-tag>
        <el-button @click="loadAlarmEvents">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-section">
      <div class="stats-grid">
        <div class="stat-card total">
          <div class="stat-icon">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ stats.total_events }}</div>
            <div class="stat-label">总报警事件</div>
          </div>
        </div>
        
        <div class="stat-card pending">
          <div class="stat-icon">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ stats.pending_events }}</div>
            <div class="stat-label">待处理</div>
          </div>
        </div>
        
        <div class="stat-card critical">
          <div class="stat-icon">
            <el-icon><WarningFilled /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ stats.critical_events }}</div>
            <div class="stat-label">严重事件</div>
          </div>
        </div>
        
        <div class="stat-card resolved">
          <div class="stat-icon">
            <el-icon><Check /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ stats.resolved_events }}</div>
            <div class="stat-label">已解决</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 筛选器 -->
    <div class="filter-section">
      <el-card>
        <div class="filter-row">
          <div class="filter-item">
            <label>事件类型：</label>
            <el-select v-model="filters.event_type" placeholder="选择事件类型" clearable>
              <el-option label="全部" value="" />
              <el-option label="吸烟检测" value="smoking" />
              <el-option label="电话检测" value="phone" />
              <el-option label="火灾检测" value="fire" />
              <el-option label="陌生人检测" value="stranger" />
              <el-option label="打架斗殴" value="fighting" />
              <el-option label="垃圾检测" value="rubbish" />
              <el-option label="翻越检测" value="crossover" />
            </el-select>
          </div>
          
          <div class="filter-item">
            <label>严重程度：</label>
            <el-select v-model="filters.severity" placeholder="选择严重程度" clearable>
              <el-option label="全部" value="" />
              <el-option label="低" value="low" />
              <el-option label="中" value="medium" />
              <el-option label="高" value="high" />
              <el-option label="严重" value="critical" />
            </el-select>
          </div>
          
          <div class="filter-item">
            <label>处理状态：</label>
            <el-select v-model="filters.status" placeholder="选择处理状态" clearable>
              <el-option label="全部" value="" />
              <el-option label="待处理" value="pending" />
              <el-option label="处理中" value="processing" />
              <el-option label="已解决" value="resolved" />
              <el-option label="已忽略" value="ignored" />
            </el-select>
          </div>
          
          <div class="filter-item">
            <el-button type="primary" @click="applyFilters">
              <el-icon><Search /></el-icon>
              筛选
            </el-button>
            <el-button @click="resetFilters">
              <el-icon><Refresh /></el-icon>
              重置
            </el-button>
          </div>
        </div>
      </el-card>
    </div>


    <!-- 事件列表 -->
    <div class="events-section">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>报警事件列表</span>
            <div class="header-actions">
              <el-button size="small" @click="loadAlarmEvents">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </div>
        </template>

        <el-table 
          :data="alarmEvents" 
          v-loading="loading"
          stripe
          style="width: 100%"
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="55" />
          
          <el-table-column prop="id" label="ID" width="80" />
          
          <el-table-column label="事件类型" width="120">
            <template #default="{ row }">
              <el-tag :type="getEventTypeTagType(row.event_type)">
                {{ getEventTypeLabel(row.event_type) }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column label="严重程度" width="100">
            <template #default="{ row }">
              <el-tag :type="getSeverityTagType(row.severity)">
                {{ getSeverityLabel(row.severity) }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column prop="title" label="事件标题" min-width="200" />
          
          <el-table-column label="置信度" width="100">
            <template #default="{ row }">
              <el-progress 
                :percentage="Math.round(row.confidence * 100)" 
                :color="getConfidenceColor(row.confidence)"
                :show-text="false"
                :stroke-width="8"
              />
              <span class="confidence-text">{{ Math.round(row.confidence * 100) }}%</span>
            </template>
          </el-table-column>
          
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusTagType(row.status)">
                {{ getStatusLabel(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column prop="detected_at" label="检测时间" width="180">
            <template #default="{ row }">
              {{ formatDateTime(row.detected_at) }}
            </template>
          </el-table-column>
          
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button size="small" @click="viewEventDetail(row)">
                <el-icon><View /></el-icon>
                查看
              </el-button>
              <el-button 
                size="small" 
                type="primary" 
                @click="updateEventStatus(row, 'processing')"
                v-if="row.status === 'pending'"
              >
                <el-icon><Edit /></el-icon>
                处理
              </el-button>
              <el-button 
                size="small" 
                type="success" 
                @click="updateEventStatus(row, 'resolved')"
                v-if="row.status === 'processing'"
              >
                <el-icon><Check /></el-icon>
                解决
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination-container">
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.page_size"
            :page-sizes="[10, 20, 50, 100]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </el-card>
    </div>

    <!-- 事件详情对话框 -->
    <el-dialog 
      v-model="detailDialogVisible" 
      title="事件详情" 
      width="800px"
      :close-on-click-modal="false"
    >
      <div v-if="selectedEvent" class="event-detail">
        <div class="detail-section">
          <h3>基本信息</h3>
          <div class="detail-grid">
            <div class="detail-item">
              <label>事件ID：</label>
              <span>{{ selectedEvent.id }}</span>
            </div>
            <div class="detail-item">
              <label>事件类型：</label>
              <el-tag :type="getEventTypeTagType(selectedEvent.event_type)">
                {{ getEventTypeLabel(selectedEvent.event_type) }}
              </el-tag>
            </div>
            <div class="detail-item">
              <label>严重程度：</label>
              <el-tag :type="getSeverityTagType(selectedEvent.severity)">
                {{ getSeverityLabel(selectedEvent.severity) }}
              </el-tag>
            </div>
            <div class="detail-item">
              <label>处理状态：</label>
              <el-tag :type="getStatusTagType(selectedEvent.status)">
                {{ getStatusLabel(selectedEvent.status) }}
              </el-tag>
            </div>
            <div class="detail-item">
              <label>置信度：</label>
              <span>{{ Math.round(selectedEvent.confidence * 100) }}%</span>
            </div>
            <div class="detail-item">
              <label>检测时间：</label>
              <span>{{ formatDateTime(selectedEvent.detected_at) }}</span>
            </div>
          </div>
        </div>

        <div class="detail-section">
          <h3>事件描述</h3>
          <p>{{ selectedEvent.description }}</p>
        </div>

        <div class="detail-section" v-if="selectedEvent.image_path">
          <h3>检测截图</h3>
          <div class="image-container">
            <img 
              :src="getImageUrl(selectedEvent.image_path)" 
              alt="检测截图"
              class="detection-image"
              @error="handleImageError"
            />
          </div>
        </div>

        <div class="detail-section" v-if="selectedEvent.video_path">
          <h3>检测视频</h3>
          <div class="video-container">
            <video 
              :src="getVideoUrl(selectedEvent.video_path)" 
              controls
              class="detection-video"
            >
              您的浏览器不支持视频播放
            </video>
          </div>
        </div>

        <div class="detail-section" v-if="selectedEvent.resolution_notes">
          <h3>处理备注</h3>
          <p>{{ selectedEvent.resolution_notes }}</p>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="detailDialogVisible = false">关闭</el-button>
          <el-button 
            type="primary" 
            @click="updateEventStatus(selectedEvent, 'processing')"
            v-if="selectedEvent && selectedEvent.status === 'pending'"
          >
            开始处理
          </el-button>
          <el-button 
            type="success" 
            @click="updateEventStatus(selectedEvent, 'resolved')"
            v-if="selectedEvent && selectedEvent.status === 'processing'"
          >
            标记解决
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 状态更新对话框 -->
    <el-dialog 
      v-model="statusDialogVisible" 
      title="更新事件状态" 
      width="500px"
    >
      <el-form :model="statusForm" label-width="100px">
        <el-form-item label="新状态：">
          <el-select v-model="statusForm.status" placeholder="选择状态">
            <el-option label="处理中" value="processing" />
            <el-option label="已解决" value="resolved" />
            <el-option label="已忽略" value="ignored" />
          </el-select>
        </el-form-item>
        <el-form-item label="处理备注：">
          <el-input 
            v-model="statusForm.resolution_notes" 
            type="textarea" 
            :rows="3"
            placeholder="请输入处理备注"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="statusDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmStatusUpdate">确认更新</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  VideoPlay,
  VideoPause,
  Refresh,
  Warning,
  Clock,
  WarningFilled,
  Check,
  Search,
  View,
  Edit
} from '@element-plus/icons-vue'
import axios from 'axios'

// API基础URL
const API_BASE = 'http://172.16.160.100:8003/api2'

// 响应式数据
const loading = ref(false)
const streamLoading = ref(false)
const alarmEvents = ref([])
const selectedEvent = ref(null)
const detailDialogVisible = ref(false)
const statusDialogVisible = ref(false)
const selectedEvents = ref([])

// 视频流相关数据
// 视频分析服务状态
const analysisStatus = ref('stopped')

// 统计数据
const stats = ref({
  total_events: 0,
  pending_events: 0,
  critical_events: 0,
  resolved_events: 0
})

// 筛选器
const filters = reactive({
  event_type: '',
  severity: '',
  status: ''
})

// 分页
const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

// 状态更新表单
const statusForm = reactive({
  status: '',
  resolution_notes: ''
})

// 计算属性
const getEventTypeLabel = (type) => {
  const labels = {
    'smoking': '吸烟检测',
    'phone': '电话检测',
    'fire': '火灾检测',
    'stranger': '陌生人检测',
    'fighting': '打架斗殴',
    'rubbish': '垃圾检测',
    'crossover': '翻越检测'
  }
  return labels[type] || type
}

const getSeverityLabel = (severity) => {
  const labels = {
    'low': '低',
    'medium': '中',
    'high': '高',
    'critical': '严重'
  }
  return labels[severity] || severity
}

const getStatusLabel = (status) => {
  const labels = {
    'pending': '待处理',
    'processing': '处理中',
    'resolved': '已解决',
    'ignored': '已忽略'
  }
  return labels[status] || status
}

const getEventTypeTagType = (type) => {
  const types = {
    'smoking': 'warning',
    'phone': 'info',
    'fire': 'danger',
    'stranger': 'warning',
    'fighting': 'danger',
    'rubbish': 'warning',
    'crossover': 'danger'
  }
  return types[type] || 'info'
}

const getSeverityTagType = (severity) => {
  const types = {
    'low': 'success',
    'medium': 'warning',
    'high': 'danger',
    'critical': 'danger'
  }
  return types[severity] || 'info'
}

const getStatusTagType = (status) => {
  const types = {
    'pending': 'warning',
    'processing': 'primary',
    'resolved': 'success',
    'ignored': 'info'
  }
  return types[status] || 'info'
}

const getConfidenceColor = (confidence) => {
  if (confidence >= 0.8) return '#f56c6c'
  if (confidence >= 0.6) return '#e6a23c'
  return '#67c23a'
}

// 方法
let previousEventCount = 0
const loadAlarmEvents = async (showLoading = false) => {
  try {
    if (showLoading) {
      loading.value = true
    }
    
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      ...filters,
      _t: Date.now() // 防止缓存
    }
    
    console.log('正在获取报警事件...', params)
    const response = await axios.get(`${API_BASE}/alarm-events`, { params })
    console.log('报警事件响应:', response.data)
    
    if (response.data.error) {
      ElMessage.error(response.data.error)
      return
    }
    
    const newTotal = response.data.total
    console.log(`当前总数: ${newTotal}, 之前总数: ${previousEventCount}`)
    
    // 检测是否有新的报警事件
    if (previousEventCount > 0 && newTotal > previousEventCount) {
      const newCount = newTotal - previousEventCount
      console.log(`✅ 检测到 ${newCount} 条新报警事件！`)
      ElMessage({
        message: `🚨 检测到 ${newCount} 条新报警事件！`,
        type: 'warning',
        duration: 5000,
        showClose: true
      })
      
      // 如果在第一页，自动滚动到顶部
      if (pagination.page === 1) {
        setTimeout(() => {
          const eventsSection = document.querySelector('.events-section')
          if (eventsSection) {
            eventsSection.scrollIntoView({ behavior: 'smooth', block: 'start' })
          }
        }, 500)
      }
    }
    
    previousEventCount = newTotal
    alarmEvents.value = response.data.data
    pagination.total = newTotal
    
    // 更新统计数据
    updateStats()
    
  } catch (error) {
    console.error('加载报警事件失败:', error)
    // 只在第一次加载时显示错误，避免频繁提示
    if (previousEventCount === 0) {
      ElMessage.error('加载报警事件失败')
    }
  } finally {
    if (showLoading) {
      loading.value = false
    }
  }
}

const updateStats = () => {
  stats.value.total_events = pagination.total
  stats.value.pending_events = alarmEvents.value.filter(e => e.status === 'pending').length
  stats.value.critical_events = alarmEvents.value.filter(e => e.severity === 'critical').length
  stats.value.resolved_events = alarmEvents.value.filter(e => e.status === 'resolved').length
}

const applyFilters = () => {
  pagination.page = 1
  loadAlarmEvents(true)
}

const resetFilters = () => {
  Object.keys(filters).forEach(key => {
    filters[key] = ''
  })
  applyFilters()
}

const handleSizeChange = (size) => {
  pagination.page_size = size
  pagination.page = 1
  loadAlarmEvents(true)
}

const handleCurrentChange = (page) => {
  pagination.page = page
  loadAlarmEvents(true)
}

const handleSelectionChange = (selection) => {
  selectedEvents.value = selection
}

const viewEventDetail = (event) => {
  selectedEvent.value = event
  detailDialogVisible.value = true
}

const updateEventStatus = (event, status) => {
  selectedEvent.value = event
  statusForm.status = status
  statusForm.resolution_notes = ''
  statusDialogVisible.value = true
}

const confirmStatusUpdate = async () => {
  try {
    const response = await axios.put(
      `${API_BASE}/alarm-events/${selectedEvent.value.id}/status`,
      {
        status: statusForm.status,
        resolution_notes: statusForm.resolution_notes
      }
    )
    
    if (response.data.error) {
      ElMessage.error(response.data.error)
      return
    }
    
    ElMessage.success('事件状态更新成功')
    statusDialogVisible.value = false
    loadAlarmEvents(true)
    
  } catch (error) {
    console.error('更新事件状态失败:', error)
    ElMessage.error('更新事件状态失败')
  }
}

const startVideoStream = async () => {
  try {
    streamLoading.value = true
    const response = await axios.post(`${API_BASE}/video-stream/start`)
    
    if (response.data.error) {
      ElMessage.error(response.data.error)
      return
    }
    
    ElMessage.success('视频流处理已启动')
    
  } catch (error) {
    console.error('启动视频流失败:', error)
    ElMessage.error('启动视频流失败')
  } finally {
    streamLoading.value = false
  }
}

const stopVideoStream = async () => {
  try {
    streamLoading.value = true
    const response = await axios.post(`${API_BASE}/video-stream/stop`)
    
    if (response.data.error) {
      ElMessage.error(response.data.error)
      return
    }
    
    ElMessage.success('视频流处理已停止')
    
  } catch (error) {
    console.error('停止视频流失败:', error)
    ElMessage.error('停止视频流失败')
  } finally {
    streamLoading.value = false
  }
}

const formatDateTime = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

const getImageUrl = (imagePath) => {
  if (!imagePath) return ''
  return `${API_BASE.replace('/api2', '')}${imagePath}`
}

const getVideoUrl = (videoPath) => {
  if (!videoPath) return ''
  return `${API_BASE.replace('/api2', '')}${videoPath}`
}

const handleImageError = (event) => {
  event.target.style.display = 'none'
  ElMessage.warning('图片加载失败')
}

// 视频流相关方法
const loadVideoStream = async () => {
  try {
    // 获取摄像头列表
    const camerasResponse = await axios.get(`${API_BASE}/cameras`)
    if (camerasResponse.data.error) {
      ElMessage.error(camerasResponse.data.error)
      return
    }
    
    const cameras = camerasResponse.data
    if (cameras.length === 0) {
      ElMessage.warning('没有可用的摄像头')
      return
    }
    
    // 使用第一个在线摄像头
    const camera = cameras.find(c => c.status === 'online') || cameras[0]
    
    // 获取视频流信息
    const feedResponse = await axios.get(`${API_BASE}/video-stream/feed/${camera.id}`)
    if (feedResponse.data.success) {
      // 直接显示MJPEG流
      const mjpegUrl = `${API_BASE}/mjpeg-stream/${camera.id}/`
      videoStreamUrl.value = mjpegUrl
      streamStatus.value = 'online'
      streamInfo.value = `摄像头: ${camera.name} (${camera.ip_address}:${camera.port})`
      ElMessage.success('视频流加载成功')
    } else {
      ElMessage.error(feedResponse.data.message || feedResponse.data.error)
    }
    
  } catch (error) {
    console.error('加载视频流失败:', error)
    ElMessage.error('加载视频流失败')
  }
}

const handleVideoError = (event) => {
  console.error('视频播放错误:', event)
  ElMessage.error('视频流连接失败，请检查网络或摄像头状态')
  streamStatus.value = 'offline'
}

const handleVideoLoadStart = () => {
  console.log('视频开始加载')
  streamStatus.value = 'loading'
}

const handleVideoCanPlay = () => {
  console.log('视频可以播放')
  streamStatus.value = 'online'
}

const startVideoFramePolling = (cameraId, frameUrl) => {
  // 停止现有的轮询
  if (framePollingInterval.value) {
    clearInterval(framePollingInterval.value)
  }
  
  currentCameraId.value = cameraId
  
  // 开始轮询视频帧
  framePollingInterval.value = setInterval(async () => {
    try {
      const response = await axios.get(frameUrl)
      if (response.data.success && response.data.frame) {
        // 更新视频显示
        updateVideoDisplay(response.data.frame)
      }
    } catch (error) {
      console.error('获取视频帧失败:', error)
    }
  }, 200) // 每200ms获取一帧（5fps）
}

const updateVideoDisplay = (frameBase64) => {
  const videoElement = document.querySelector('.live-video')
  if (videoElement) {
    // 创建新的img元素显示帧
    const img = document.createElement('img')
    img.src = `data:image/jpeg;base64,${frameBase64}`
    img.style.width = '100%'
    img.style.height = '100%'
    img.style.objectFit = 'cover'
    
    // 替换视频内容
    videoElement.innerHTML = ''
    videoElement.appendChild(img)
  }
}

const stopVideoFramePolling = () => {
  if (framePollingInterval.value) {
    clearInterval(framePollingInterval.value)
    framePollingInterval.value = null
  }
}

const getVideoStreamStatus = async () => {
  try {
    const response = await axios.get(`${API_BASE}/video-stream/status`)
    if (response.data.success) {
      return response.data
    }
  } catch (error) {
    console.error('获取视频流状态失败:', error)
  }
  return null
}

// 生命周期
// 获取视频分析服务状态
const checkAnalysisStatus = async () => {
  try {
    const response = await axios.get(`${API_BASE}/video-analysis/status`)
    if (response.data.success) {
      analysisStatus.value = response.data.running ? 'running' : 'stopped'
    }
  } catch (error) {
    console.error('获取视频分析状态失败:', error)
  }
}

onMounted(() => {
  // 首次加载显示loading
  loadAlarmEvents(true)
  checkAnalysisStatus()
  
  // 定期检查视频分析状态（每10秒）
  setInterval(async () => {
    checkAnalysisStatus()
  }, 10000)
  
  // 定期刷新报警事件列表（每5秒，不显示loading）
  setInterval(async () => {
    console.log('⏰ 定时刷新报警事件...')
    loadAlarmEvents(false)
  }, 5000)
})
</script>

<style scoped>
.alarm-events-container {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.page-description {
  margin: 5px 0 0 0;
  color: #909399;
  font-size: 14px;
}

.header-right {
  display: flex;
  gap: 10px;
}

.stats-section {
  margin-bottom: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.stat-card.total .stat-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-card.pending .stat-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-card.critical .stat-icon {
  background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
}

.stat-card.resolved .stat-icon {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 5px;
}

.stat-label {
  color: #909399;
  font-size: 14px;
}

.filter-section {
  margin-bottom: 20px;
}

.filter-row {
  display: flex;
  gap: 20px;
  align-items: center;
  flex-wrap: wrap;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-item label {
  font-weight: 500;
  color: #606266;
  white-space: nowrap;
}

.events-section {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.confidence-text {
  margin-left: 8px;
  font-size: 12px;
  color: #606266;
}

.event-detail {
  max-height: 600px;
  overflow-y: auto;
}

.detail-section {
  margin-bottom: 20px;
}

.detail-section h3 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 16px;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 5px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.detail-item label {
  font-weight: 500;
  color: #606266;
  min-width: 80px;
}

.image-container, .video-container {
  text-align: center;
  margin-top: 10px;
}

.detection-image {
  max-width: 100%;
  max-height: 300px;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.detection-video {
  max-width: 100%;
  max-height: 300px;
  border-radius: 4px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 视频流样式 */
.video-stream-section {
  margin-bottom: 20px;
}

.video-container {
  position: relative;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
}

.video-player {
  position: relative;
  width: 100%;
  height: 400px;
}

.live-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  background: #000;
}

.video-info {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(0, 0, 0, 0.7);
  padding: 8px 12px;
  border-radius: 4px;
  color: white;
  font-size: 12px;
}

.stream-info {
  color: #ccc;
}

.no-video {
  height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  border-radius: 8px;
}
</style>
