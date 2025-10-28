<template>
  <div class="event-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">事件管理</h1>
      <el-input
        v-model="searchKeyword"
        placeholder="搜索事件..."
        class="search-input"
        clearable
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
    </div>

    <!-- 事件列表表格 -->
    <div class="table-section">
      <el-table
        :data="filteredEventList"
        class="event-table"
        stripe
        v-loading="loading"
      >
        <el-table-column prop="event_id" label="ID" width="150" />
        
        <el-table-column label="类型" width="120">
          <template #default="{ row }">
            <el-tag
              :type="getEventTypeColor(row.event_type)"
              size="small"
            >
              {{ getEventTypeLabel(row.event_type) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="description" label="描述" min-width="250" />
        
        <el-table-column prop="location" label="来源" width="180" />
        
        <el-table-column label="严重程度" width="100">
          <template #default="{ row }">
            <el-tag
              :type="getSeverityColor(row.severity)"
              size="small"
            >
              {{ getSeverityLabel(row.severity) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag
              :type="getStatusColor(row.status)"
              size="small"
            >
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="detected_at" label="时间" width="180" />
        
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDetail(row)">
              详情
            </el-button>
            <el-button 
              link 
              type="success" 
              size="small" 
              @click="handleEvent(row)"
              v-if="row.status === 'pending'"
            >
              处理
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <span class="total-count">显示 {{ filteredEventList.length }} 条，共 {{ totalCount }} 条</span>
        <el-pagination
          v-model:current-page="currentPage"
          :page-sizes="[10, 20, 50, 100]"
          :page-size="pageSize"
          :total="totalCount"
          layout="prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="事件详情"
      width="800px"
    >
      <div v-if="currentEvent" class="event-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="事件ID">{{ currentEvent.event_id }}</el-descriptions-item>
          <el-descriptions-item label="事件类型">
            <el-tag :type="getEventTypeColor(currentEvent.event_type)" size="small">
              {{ getEventTypeLabel(currentEvent.event_type) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="严重程度">
            <el-tag :type="getSeverityColor(currentEvent.severity)" size="small">
              {{ getSeverityLabel(currentEvent.severity) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusColor(currentEvent.status)" size="small">
              {{ getStatusLabel(currentEvent.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="来源" :span="2">{{ currentEvent.location }}</el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">{{ currentEvent.description }}</el-descriptions-item>
          <el-descriptions-item label="检测时间" :span="2">{{ currentEvent.detected_at }}</el-descriptions-item>
          <el-descriptions-item label="置信度" v-if="currentEvent.confidence">
            {{ (currentEvent.confidence * 100).toFixed(1) }}%
          </el-descriptions-item>
        </el-descriptions>

        <!-- 截图/视频 -->
        <div v-if="currentEvent.image_path || currentEvent.video_path" class="media-section">
          <h4>相关媒体</h4>
          <img 
            v-if="currentEvent.image_path" 
            :src="getMediaUrl(currentEvent.image_path)" 
            alt="事件截图"
            class="event-image"
          />
          <video 
            v-if="currentEvent.video_path" 
            :src="getMediaUrl(currentEvent.video_path)" 
            controls
            class="event-video"
          />
        </div>
      </div>
      
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
        <el-button 
          type="primary" 
          @click="handleEvent(currentEvent)"
          v-if="currentEvent && currentEvent.status === 'pending'"
        >
          处理事件
        </el-button>
      </template>
    </el-dialog>

    <!-- 处理事件对话框 -->
    <el-dialog
      v-model="handleDialogVisible"
      title="处理事件"
      width="500px"
    >
      <el-form :model="handleForm" label-width="100px">
        <el-form-item label="处理状态">
          <el-radio-group v-model="handleForm.status">
            <el-radio label="processing">处理中</el-radio>
            <el-radio label="resolved">已解决</el-radio>
            <el-radio label="ignored">忽略</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="处理备注">
          <el-input
            v-model="handleForm.note"
            type="textarea"
            :rows="4"
            placeholder="请输入处理备注..."
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="handleDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitHandle">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'

// 数据状态
const loading = ref(false)
const eventList = ref([])
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const totalCount = ref(0)

// 对话框状态
const detailDialogVisible = ref(false)
const handleDialogVisible = ref(false)
const currentEvent = ref(null)

// 处理表单
const handleForm = ref({
  status: 'resolved',
  note: ''
})

// 自动刷新定时器
let refreshTimer = null

// 计算过滤后的列表
const filteredEventList = computed(() => {
  let list = eventList.value
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    list = list.filter(event => 
      event.event_id?.toLowerCase().includes(keyword) ||
      event.description?.toLowerCase().includes(keyword) ||
      event.location?.toLowerCase().includes(keyword)
    )
  }
  
  return list
})

// 获取报警事件列表
const loadAlarmEvents = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams({
      page: currentPage.value,
      page_size: pageSize.value
    })
    
    // 添加可选的过滤参数
    // if (filters.event_type) params.append('event_type', filters.event_type)
    // if (filters.severity) params.append('severity', filters.severity)
    // if (filters.status) params.append('status', filters.status)
    
    const response = await fetch(`/api2/alarm-events?${params}`)
    const result = await response.json()
    
    if (result.success && result.data) {
      eventList.value = result.data.map(event => ({
        ...event,
        event_id: `EV-${event.detected_at?.substring(0, 10).replace(/-/g, '')}${String(event.id).padStart(3, '0')}`,
        location: `${event.camera_name || '摄像头' + event.camera_id} - ${event.camera_location || ''}`,
        detected_at: formatDateTime(event.detected_at)
      }))
      totalCount.value = result.total || 0
      console.log('成功加载报警事件:', eventList.value.length, '条')
    } else {
      // 如果后端返回失败，使用模拟数据
      throw new Error('API返回失败')
    }
  } catch (error) {
    console.error('获取报警事件失败:', error)
    ElMessage.warning('获取报警事件失败，使用模拟数据')
    
    // 使用模拟数据
    eventList.value = [
      {
        id: 1,
        event_id: 'EV-20230825-001',
        event_type: 'fire',
        description: '温度超过安全阈值，当前温度32℃',
        location: 'A区3楼温度传感器',
        severity: 'critical',
        status: 'pending',
        detected_at: '2023-08-25 01:45:23',
        confidence: 0.95
      },
      {
        id: 2,
        event_id: 'EV-20230825-002',
        event_type: 'stranger',
        description: '机器人导航系统故障，已断开任务',
        location: '探索者-X1机器人',
        severity: 'high',
        status: 'pending',
        detected_at: '2023-08-25 01:30:12',
        confidence: 0.88
      },
      {
        id: 3,
        event_id: 'EV-20230825-003',
        event_type: 'phone',
        description: '检测到未授权人员进入',
        location: 'B区1楼摄像头',
        severity: 'medium',
        status: 'processing',
        detected_at: '2023-08-25 01:16:05',
        confidence: 0.76
      },
      {
        id: 4,
        event_id: 'EV-20230824-045',
        event_type: 'smoking',
        description: '空调压缩机故障，已自动切换备用机组',
        location: 'C区5楼空调系统',
        severity: 'high',
        status: 'resolved',
        detected_at: '2023-08-24 23:10:56',
        confidence: 0.92
      },
      {
        id: 5,
        event_id: 'EV-20230824-044',
        event_type: 'fighting',
        description: '完成每日巡检扫描的',
        location: '系统维护',
        severity: 'low',
        status: 'resolved',
        detected_at: '2023-08-24 22:30:00',
        confidence: 1.0
      },
      {
        id: 6,
        event_id: 'EV-20230824-043',
        event_type: 'rubbish',
        description: '烟雾探测器触发报, 已虚惊',
        location: 'D区2楼消防系统',
        severity: 'medium',
        status: 'resolved',
        detected_at: '2023-08-24 21:45:18',
        confidence: 0.65
      }
    ]
    totalCount.value = eventList.value.length
  } finally {
    loading.value = false
  }
}

// 查看详情
const viewDetail = (event) => {
  currentEvent.value = event
  detailDialogVisible.value = true
}

// 处理事件
const handleEvent = (event) => {
  currentEvent.value = event
  handleForm.value = {
    status: 'resolved',
    note: ''
  }
  handleDialogVisible.value = true
}

// 提交处理
const submitHandle = async () => {
  try {
    // TODO: 调用API更新事件状态
    // await fetch(`/api2/alarm-events/${currentEvent.value.id}/handle`, {
    //   method: 'POST',
    //   body: JSON.stringify(handleForm.value)
    // })
    
    // 更新本地数据
    const index = eventList.value.findIndex(e => e.id === currentEvent.value.id)
    if (index > -1) {
      eventList.value[index].status = handleForm.value.status
    }
    
    ElMessage.success('事件处理成功')
    handleDialogVisible.value = false
    detailDialogVisible.value = false
  } catch (error) {
    ElMessage.error('事件处理失败')
  }
}

// 获取事件类型标签
const getEventTypeLabel = (type) => {
  const labels = {
    'smoking': '吸烟',
    'phone': '打电话',
    'fire': '火灾',
    'stranger': '陌生人',
    'fighting': '打架',
    'rubbish': '垃圾',
    'crossover': '翻越'
  }
  return labels[type] || type
}

// 获取事件类型颜色
const getEventTypeColor = (type) => {
  const colors = {
    'fire': 'danger',
    'fighting': 'danger',
    'stranger': 'warning',
    'smoking': 'warning',
    'phone': 'warning',
    'rubbish': 'info',
    'crossover': 'warning'
  }
  return colors[type] || 'info'
}

// 获取严重程度标签
const getSeverityLabel = (severity) => {
  const labels = {
    'low': '低',
    'medium': '中',
    'high': '高',
    'critical': '严重'
  }
  return labels[severity] || severity
}

// 获取严重程度颜色
const getSeverityColor = (severity) => {
  const colors = {
    'low': 'info',
    'medium': 'warning',
    'high': 'danger',
    'critical': 'danger'
  }
  return colors[severity] || 'info'
}

// 获取状态标签
const getStatusLabel = (status) => {
  const labels = {
    'pending': '新事件',
    'processing': '处理中',
    'resolved': '已解决',
    'ignored': '已关闭'
  }
  return labels[status] || status
}

// 获取状态颜色
const getStatusColor = (status) => {
  const colors = {
    'pending': 'danger',
    'processing': 'warning',
    'resolved': 'success',
    'ignored': 'info'
  }
  return colors[status] || 'info'
}

// 获取媒体URL
const getMediaUrl = (path) => {
  if (!path) return ''
  return path.startsWith('http') ? path : `http://localhost:8000${path}`
}

// 格式化日期时间
const formatDateTime = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }).replace(/\//g, '-')
}

// 分页处理
const handleSizeChange = (size) => {
  pageSize.value = size
  loadAlarmEvents()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  loadAlarmEvents()
}

// 启动自动刷新
const startAutoRefresh = () => {
  refreshTimer = setInterval(() => {
    loadAlarmEvents()
  }, 30000) // 每30秒刷新一次
}

// 停止自动刷新
const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

// 页面加载时获取数据
onMounted(() => {
  loadAlarmEvents()
  startAutoRefresh()
})

// 页面卸载时清理定时器
onBeforeUnmount(() => {
  stopAutoRefresh()
})
</script>

<style scoped>
.event-management {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
  color: #303133;
}

.search-input {
  width: 300px;
}

.table-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.event-table {
  width: 100%;
}

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
}

.total-count {
  font-size: 14px;
  color: #606266;
}

.event-detail {
  padding: 10px 0;
}

.media-section {
  margin-top: 20px;
}

.media-section h4 {
  margin-bottom: 10px;
  color: #303133;
}

.event-image {
  max-width: 100%;
  border-radius: 4px;
  margin-top: 10px;
}

.event-video {
  max-width: 100%;
  border-radius: 4px;
  margin-top: 10px;
}
</style>
