<template>
  <div class="event-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">事件管理</h1>
      </div>
      <div class="header-right">
        <el-input
          v-model="searchText"
          placeholder="搜索事件..."
          class="search-input"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
    </div>

    <!-- 事件列表表格 -->
    <div class="table-container">
      <el-table
        :data="filteredEvents"
        style="width: 100%"
        class="event-table"
        stripe
        border
        :header-cell-style="{ backgroundColor: '#f5f7fa', color: '#606266' }"
      >
        <el-table-column prop="id" label="ID" width="150" align="center" />
        
        <el-table-column prop="type" label="类型" width="120" align="center">
          <template #default="{ row }">
            <el-tag
              :type="getEventTypeTagType(row.type)"
              size="small"
            >
              {{ getEventTypeText(row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="description" label="描述" min-width="200">
          <template #default="{ row }">
            <div class="description-content">
              {{ row.description }}
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="source" label="来源" width="180" align="center" />
        
        <el-table-column prop="severity" label="严重程度" width="120" align="center">
          <template #default="{ row }">
            <el-tag
              :type="getSeverityTagType(row.severity)"
              size="small"
            >
              {{ getSeverityText(row.severity) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态" width="120" align="center">
          <template #default="{ row }">
            <el-tag
              :type="getStatusTagType(row.status)"
              size="small"
            >
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="time" label="时间" width="180" align="center" />
        
        <el-table-column label="操作" width="150" align="center" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              link
              @click="viewDetails(row)"
            >
              详情
            </el-button>
            <el-button
              v-if="row.status === 'new'"
              type="success"
              size="small"
              link
              @click="handleEvent(row)"
            >
              处理
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 分页 -->
    <div class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="totalEvents"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 事件详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="事件详情"
      width="600px"
      :before-close="handleCloseDetail"
    >
      <div v-if="selectedEvent" class="event-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="事件ID">{{ selectedEvent.id }}</el-descriptions-item>
          <el-descriptions-item label="事件类型">
            <el-tag :type="getEventTypeTagType(selectedEvent.type)" size="small">
              {{ getEventTypeText(selectedEvent.type) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="严重程度">
            <el-tag :type="getSeverityTagType(selectedEvent.severity)" size="small">
              {{ getSeverityText(selectedEvent.severity) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusTagType(selectedEvent.status)" size="small">
              {{ getStatusText(selectedEvent.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="来源" :span="2">{{ selectedEvent.source }}</el-descriptions-item>
          <el-descriptions-item label="发生时间" :span="2">{{ selectedEvent.time }}</el-descriptions-item>
          <el-descriptions-item label="事件描述" :span="2">
            <div class="event-description">{{ selectedEvent.description }}</div>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="detailDialogVisible = false">关闭</el-button>
          <el-button
            v-if="selectedEvent && selectedEvent.status === 'new'"
            type="primary"
            @click="handleEventFromDialog"
          >
            处理事件
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'

// 响应式数据
const searchText = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const detailDialogVisible = ref(false)
const selectedEvent = ref(null)

// 模拟事件数据
const events = ref([
  {
    id: 'EV-20230825-001',
    type: 'alert',
    description: '温度超过安全阈值，当前温度32°C',
    source: 'A区3楼温湿度传感器',
    severity: 'high',
    status: 'new',
    time: '2023-08-25 01:45:23'
  },
  {
    id: 'EV-20230825-002',
    type: 'error',
    description: '机器人导航系统异常，已暂停任务',
    source: '探索者-X1机器人',
    severity: 'high',
    status: 'new',
    time: '2023-08-25 01:30:12'
  },
  {
    id: 'EV-20230825-003',
    type: 'warning',
    description: '检测到未授权人员进入',
    source: 'B区1楼摄像头',
    severity: 'medium',
    status: 'processing',
    time: '2023-08-25 01:16:05'
  },
  {
    id: 'EV-20230825-004',
    type: 'info',
    description: '系统定期备份完成',
    source: '系统管理模块',
    severity: 'low',
    status: 'resolved',
    time: '2023-08-25 01:00:00'
  },
  {
    id: 'EV-20230825-005',
    type: 'alert',
    description: '网络延迟异常，当前延迟156ms',
    source: '网络监控系统',
    severity: 'medium',
    status: 'new',
    time: '2023-08-25 00:45:33'
  },
  {
    id: 'EV-20230825-006',
    type: 'error',
    description: '存储空间不足，剩余空间5%',
    source: '存储管理系统',
    severity: 'high',
    status: 'processing',
    time: '2023-08-25 00:30:21'
  },
  {
    id: 'EV-20230825-007',
    type: 'warning',
    description: 'CPU使用率过高，当前使用率85%',
    source: '服务器监控',
    severity: 'medium',
    status: 'resolved',
    time: '2023-08-25 00:15:44'
  },
  {
    id: 'EV-20230825-008',
    type: 'info',
    description: '用户登录成功',
    source: '用户认证系统',
    severity: 'low',
    status: 'resolved',
    time: '2023-08-25 00:05:12'
  }
])

// 计算属性
const filteredEvents = computed(() => {
  let filtered = events.value
  
  // 搜索过滤
  if (searchText.value) {
    const searchLower = searchText.value.toLowerCase()
    filtered = filtered.filter(event => 
      event.id.toLowerCase().includes(searchLower) ||
      event.description.toLowerCase().includes(searchLower) ||
      event.source.toLowerCase().includes(searchLower)
    )
  }
  
  return filtered
})

const totalEvents = computed(() => filteredEvents.value.length)

// 方法
const getEventTypeTagType = (type) => {
  const typeMap = {
    'alert': 'danger',
    'error': 'danger',
    'warning': 'warning',
    'info': 'info'
  }
  return typeMap[type] || 'info'
}

const getEventTypeText = (type) => {
  const typeMap = {
    'alert': '警报',
    'error': '错误',
    'warning': '警告',
    'info': '信息'
  }
  return typeMap[type] || '未知'
}

const getSeverityTagType = (severity) => {
  const severityMap = {
    'high': 'danger',
    'medium': 'warning',
    'low': 'success'
  }
  return severityMap[severity] || 'info'
}

const getSeverityText = (severity) => {
  const severityMap = {
    'high': '严重',
    'medium': '中',
    'low': '低'
  }
  return severityMap[severity] || '未知'
}

const getStatusTagType = (status) => {
  const statusMap = {
    'new': 'danger',
    'processing': 'warning',
    'resolved': 'success'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status) => {
  const statusMap = {
    'new': '新事件',
    'processing': '处理中',
    'resolved': '已解决'
  }
  return statusMap[status] || '未知'
}

const viewDetails = (event) => {
  selectedEvent.value = event
  detailDialogVisible.value = true
}

const handleEvent = async (event) => {
  try {
    await ElMessageBox.confirm(
      `确定要处理事件 ${event.id} 吗？`,
      '确认处理',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 更新事件状态
    const eventIndex = events.value.findIndex(e => e.id === event.id)
    if (eventIndex !== -1) {
      events.value[eventIndex].status = 'processing'
      ElMessage.success('事件已标记为处理中')
    }
  } catch {
    ElMessage.info('已取消处理')
  }
}

const handleEventFromDialog = () => {
  if (selectedEvent.value) {
    handleEvent(selectedEvent.value)
    detailDialogVisible.value = false
  }
}

const handleCloseDetail = () => {
  detailDialogVisible.value = false
  selectedEvent.value = null
}

const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val) => {
  currentPage.value = val
}

// 生命周期
onMounted(() => {
  // 可以在这里加载事件数据
})
</script>

<style scoped>
.event-management {
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

/* 表格容器 */
.table-container {
  background: white;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.event-table {
  width: 100%;
}

.description-content {
  max-width: 300px;
  word-wrap: break-word;
  line-height: 1.4;
}

/* 分页容器 */
.pagination-container {
  display: flex;
  justify-content: center;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 事件详情对话框 */
.event-detail {
  padding: 16px 0;
}

.event-description {
  line-height: 1.6;
  color: #606266;
  word-wrap: break-word;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .event-management {
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
  
  .table-container {
    padding: 16px;
    overflow-x: auto;
  }
  
  .event-table {
    min-width: 800px;
  }
  
  .description-content {
    max-width: 200px;
  }
}

/* 表格样式优化 */
:deep(.el-table) {
  border-radius: 8px;
  overflow: hidden;
}

:deep(.el-table__header-wrapper) {
  border-radius: 8px 8px 0 0;
}

:deep(.el-table td) {
  border-bottom: 1px solid #f0f2f5;
}

:deep(.el-table tr:hover > td) {
  background-color: #f8f9fa !important;
}

/* 标签样式 */
:deep(.el-tag) {
  border-radius: 4px;
  font-weight: 500;
}

/* 按钮样式 */
:deep(.el-button--small.is-link) {
  padding: 4px 8px;
  font-size: 12px;
}
</style>