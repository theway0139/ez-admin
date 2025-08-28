<template>
  <div class="real-time-monitoring">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">实时监控</h1>
      </div>
      <div class="header-right">
        <el-input
          v-model="searchText"
          placeholder="搜索监控点..."
          class="search-input"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
    </div>

    <!-- 筛选器区域 -->
    <div class="filter-section">
      <div class="filter-row">
        <div class="filter-item">
          <label class="filter-label">监控类型</label>
          <el-select
            v-model="filters.monitorType"
            placeholder="全部类型"
            class="filter-input"
            clearable
          >
            <el-option label="全部类型" value="" />
            <el-option label="温湿度" value="temperature" />
            <el-option label="摄像头" value="camera" />
            <el-option label="空调" value="air_conditioner" />
            <el-option label="环境监测" value="environment" />
          </el-select>
        </div>
        
        <div class="filter-item">
          <label class="filter-label">状态</label>
          <el-select
            v-model="filters.status"
            placeholder="全部状态"
            class="filter-input"
            clearable
          >
            <el-option label="全部状态" value="" />
            <el-option label="在线" value="online" />
            <el-option label="离线" value="offline" />
            <el-option label="警告" value="warning" />
            <el-option label="故障" value="error" />
          </el-select>
        </div>
        
        <div class="filter-item">
          <label class="filter-label">所在区域</label>
          <el-select
            v-model="filters.location"
            placeholder="全部区域"
            class="filter-input"
            clearable
          >
            <el-option label="全部区域" value="" />
            <el-option label="A区" value="A区" />
            <el-option label="B区" value="B区" />
            <el-option label="C区" value="C区" />
            <el-option label="D区" value="D区" />
          </el-select>
        </div>
      </div>
    </div>

    <!-- 监控设备卡片区域 -->
    <div class="monitoring-cards">
      <div 
        v-for="device in filteredDevices" 
        :key="device.id" 
        class="monitoring-card"
        :class="getCardStatusClass(device.status)"
      >
        <!-- 卡片头部 -->
        <div class="card-header">
          <div class="device-info">
            <h3 class="device-name">{{ device.name }}</h3>
            <p class="device-location">{{ device.location }}</p>
          </div>
          <div class="status-badge">
            <el-tag 
              :type="getStatusTagType(device.status)"
              size="small"
            >
              {{ getStatusText(device.status) }}
            </el-tag>
          </div>
        </div>

        <!-- 卡片内容 -->
        <div class="card-content">
          <div class="metrics-grid">
            <div 
              v-for="metric in device.metrics" 
              :key="metric.key"
              class="metric-item"
            >
              <div class="metric-label">{{ metric.label }}</div>
              <div class="metric-value" :class="getMetricValueClass(metric.status)">
                {{ metric.value }}
                <span class="metric-unit">{{ metric.unit }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 卡片底部 -->
        <div class="card-footer">
          <div class="update-time">
            最后更新: {{ formatUpdateTime(device.lastUpdate) }}
          </div>
          <el-button 
            type="primary" 
            size="small" 
            @click="viewDetails(device)"
          >
            详情
            <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="filteredDevices.length === 0" class="empty-state">
      <el-empty description="暂无监控设备数据" />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Search,
  ArrowRight
} from '@element-plus/icons-vue'

// 响应式数据
const searchText = ref('')

// 筛选器
const filters = reactive({
  monitorType: '',
  status: '',
  location: ''
})

// 模拟监控设备数据
const devices = ref([
  {
    id: 1,
    name: 'A区3楼温湿度',
    location: 'A区3楼东侧',
    type: 'temperature',
    status: 'online',
    lastUpdate: '2分钟前',
    metrics: [
      { key: 'temperature', label: '温度', value: '24.5', unit: '℃', status: 'normal' },
      { key: 'humidity', label: '湿度', value: '45', unit: '%', status: 'normal' },
      { key: 'pm25', label: 'PM2.5', value: '12', unit: 'μg/m³', status: 'good' },
      { key: 'co2', label: 'CO2', value: '480', unit: 'ppm', status: 'warning' }
    ]
  },
  {
    id: 2,
    name: 'B区1楼摄像头',
    location: 'B区1楼大厅',
    type: 'camera',
    status: 'online',
    lastUpdate: '1分钟前',
    metrics: [
      { key: 'online_time', label: '在线时长', value: '8', unit: '小时', status: 'normal' },
      { key: 'storage_space', label: '存储空间', value: '65', unit: '%', status: 'normal' },
      { key: 'network_delay', label: '网络延迟', value: '28', unit: 'ms', status: 'good' },
      { key: 'cpu_usage', label: 'CPU使用率', value: '42', unit: '%', status: 'normal' }
    ]
  },
  {
    id: 3,
    name: 'C区5楼空调',
    location: 'C区5楼机房',
    type: 'air_conditioner',
    status: 'warning',
    lastUpdate: '5分钟前',
    metrics: [
      { key: 'running_status', label: '运行状态', value: '1', unit: '运行', status: 'normal' },
      { key: 'set_temperature', label: '设定温度', value: '22', unit: '℃', status: 'normal' },
      { key: 'current_temperature', label: '当前温度', value: '25', unit: '℃', status: 'warning' },
      { key: 'power_consumption', label: '运行功率', value: '85', unit: '%', status: 'high' }
    ]
  }
])

// 计算属性
const filteredDevices = computed(() => {
  let filtered = devices.value
  
  // 搜索过滤
  if (searchText.value) {
    filtered = filtered.filter(device => 
      device.name.toLowerCase().includes(searchText.value.toLowerCase()) ||
      device.location.toLowerCase().includes(searchText.value.toLowerCase())
    )
  }
  
  // 监控类型过滤
  if (filters.monitorType) {
    filtered = filtered.filter(device => device.type === filters.monitorType)
  }
  
  // 状态过滤
  if (filters.status) {
    filtered = filtered.filter(device => device.status === filters.status)
  }
  
  // 区域过滤
  if (filters.location) {
    filtered = filtered.filter(device => device.location.includes(filters.location))
  }
  
  return filtered
})

// 方法
const getStatusTagType = (status) => {
  const statusMap = {
    'online': 'success',
    'offline': 'info',
    'warning': 'warning',
    'error': 'danger'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status) => {
  const statusMap = {
    'online': '在线',
    'offline': '离线',
    'warning': '警告',
    'error': '故障'
  }
  return statusMap[status] || '未知'
}

const getCardStatusClass = (status) => {
  return {
    'card-online': status === 'online',
    'card-warning': status === 'warning',
    'card-error': status === 'error',
    'card-offline': status === 'offline'
  }
}

const getMetricValueClass = (status) => {
  return {
    'metric-normal': status === 'normal',
    'metric-good': status === 'good',
    'metric-warning': status === 'warning',
    'metric-high': status === 'high',
    'metric-danger': status === 'danger'
  }
}

const formatUpdateTime = (time) => {
  return time
}

const viewDetails = (device) => {
  ElMessage.success(`查看 ${device.name} 详细信息`)
  // 这里可以实现跳转到详情页面的逻辑
}

// 模拟实时数据更新
let updateInterval = null

const startRealTimeUpdate = () => {
  updateInterval = setInterval(() => {
    // 模拟数据更新
    devices.value.forEach(device => {
      device.metrics.forEach(metric => {
        if (metric.key === 'temperature') {
          const baseValue = parseFloat(metric.value)
          metric.value = (baseValue + (Math.random() - 0.5) * 2).toFixed(1)
        } else if (metric.key === 'humidity') {
          const baseValue = parseInt(metric.value)
          metric.value = Math.max(0, Math.min(100, baseValue + Math.floor((Math.random() - 0.5) * 10))).toString()
        }
      })
    })
  }, 5000) // 每5秒更新一次
}

const stopRealTimeUpdate = () => {
  if (updateInterval) {
    clearInterval(updateInterval)
    updateInterval = null
  }
}

// 生命周期
onMounted(() => {
  startRealTimeUpdate()
})

onUnmounted(() => {
  stopRealTimeUpdate()
})
</script>

<style scoped>
.real-time-monitoring {

}

/* 页面头部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;

}

.header-left {
  display: flex;
  align-items: center;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.search-input {
  width: 300px;
}

/* 筛选器区域 */
.filter-section {
  background: white;
  border-radius: 8px;
  padding: 20px 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.filter-row {
  display: flex;
  gap: 24px;
  align-items: end;
  flex-wrap: wrap;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 200px;
}

.filter-label {
  font-size: 14px;
  font-weight: 500;
  color: #606266;
}

.filter-input {
  width: 100%;
}

/* 监控卡片区域 */
.monitoring-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 24px;
  margin-bottom: 24px;
}

.monitoring-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  border-left: 4px solid #e5e7eb;
}

.monitoring-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.card-online {
  border-left-color: #67c23a;
}

.card-warning {
  border-left-color: #e6a23c;
}

.card-error {
  border-left-color: #f56c6c;
}

.card-offline {
  border-left-color: #909399;
}

/* 卡片头部 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.device-info {
  flex: 1;
}

.device-name {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 4px 0;
}

.device-location {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.status-badge {
  flex-shrink: 0;
}

/* 卡片内容 */
.card-content {
  margin-bottom: 16px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.metric-item {
  text-align: center;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
}

.metric-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.metric-value {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.metric-unit {
  font-size: 12px;
  font-weight: 400;
  color: #909399;
  margin-left: 2px;
}

/* 指标值颜色 */
.metric-normal {
  color: #303133;
}

.metric-good {
  color: #67c23a;
}

.metric-warning {
  color: #e6a23c;
}

.metric-high {
  color: #f56c6c;
}

.metric-danger {
  color: #f56c6c;
}

/* 卡片底部 */
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid #f0f2f5;
}

.update-time {
  font-size: 12px;
  color: #909399;
}

/* 空状态 */
.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .real-time-monitoring {
    padding: 16px;
  }
  
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .search-input {
    width: 100%;
  }
  
  .filter-row {
    flex-direction: column;
    gap: 16px;
  }
  
  .filter-item {
    min-width: auto;
  }
  
  .monitoring-cards {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .card-footer {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
}

/* 动画效果 */
@keyframes pulse {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
  100% {
    opacity: 1;
  }
}

.card-online .status-badge {
  animation: pulse 2s infinite;
}
</style>