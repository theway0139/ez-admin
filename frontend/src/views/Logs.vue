<template>
  <div class="logs-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">{{ $t('logs.title') }}</h1>
      </div>
      <div class="header-right">
        <el-button type="success" @click="exportLogs">
          <el-icon><Download /></el-icon>
          {{ $t('logs.exportLogs') }}
        </el-button>
        <el-button type="danger" @click="clearLogs">
          <el-icon><Delete /></el-icon>
          {{ $t('logs.clearLogs') }}
        </el-button>
      </div>
    </div>

    <!-- 筛选器区域 -->
    <div class="filter-section">
      <div class="filter-row">
        <div class="filter-item">
          <label class="filter-label">{{ $t('logs.operationType') }}</label>
          <el-select
            v-model="filters.operationType"
            :placeholder="$t('logs.allTypes')"
            class="filter-input"
            clearable
            @change="loadLogs"
          >
            <el-option :label="$t('logs.allTypes')" value="" />
            <el-option label="登录" value="login" />
            <el-option label="创建" value="create" />
            <el-option label="更新" value="update" />
            <el-option label="删除" value="delete" />
            <el-option label="系统设置" value="config" />
            <el-option label="用户管理" value="user_mgmt" />
            <el-option label="机器人配置" value="robot_mgmt" />
            <el-option label="任务调度" value="task_mgmt" />
            <el-option label="录像文件" value="file_mgmt" />
      </el-select>
        </div>
        
        <div class="filter-item">
          <label class="filter-label">{{ $t('logs.operator') }}</label>
          <el-input
            v-model="filters.operator"
            :placeholder="$t('logs.searchOperator')"
            class="filter-input"
            clearable
            @change="loadLogs"
          />
        </div>
        
        <div class="filter-item">
          <label class="filter-label">{{ $t('logs.startTime') }}</label>
      <el-date-picker
            v-model="filters.startTime"
            type="datetime"
            :placeholder="$t('logs.selectStartTime')"
            format="YYYY/MM/DD HH:mm"
            value-format="YYYY-MM-DD HH:mm:ss"
            class="filter-input"
            @change="loadLogs"
          />
        </div>
        
        <div class="filter-item">
          <label class="filter-label">{{ $t('logs.endTime') }}</label>
          <el-date-picker
            v-model="filters.endTime"
            type="datetime"
            :placeholder="$t('logs.selectEndTime')"
            format="YYYY/MM/DD HH:mm"
            value-format="YYYY-MM-DD HH:mm:ss"
            class="filter-input"
            @change="loadLogs"
          />
    </div>
    
        <div class="filter-item">
          <label class="filter-label">{{ $t('common.actions') }}</label>
          <div class="filter-actions">
            <el-button type="primary" @click="loadLogs">
              <el-icon><Search /></el-icon>
              {{ $t('logs.query') }}
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 日志列表表格 -->
    <div class="table-container">
      <el-table
        :data="logs"
        stripe
        class="logs-table"
        v-loading="loading"
      >
        <el-table-column prop="operation_time" :label="$t('logs.time')" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.operation_time) }}
        </template>
      </el-table-column>
        
        <el-table-column prop="operator_name" :label="$t('logs.operator')" width="120" />
        
        <el-table-column prop="operation_type_display" :label="$t('logs.operationType')" width="120">
          <template #default="{ row }">
            <el-tag 
              :type="getOperationTypeTagType(row.operation_type)"
              size="small"
            >
              {{ row.operation_type_display }}
          </el-tag>
        </template>
      </el-table-column>
        
        <el-table-column prop="operation_target" :label="$t('logs.target')" width="150" />
        
        <el-table-column prop="operation_detail" :label="$t('logs.details')" min-width="300">
          <template #default="{ row }">
            <div class="operation-detail">
              {{ row.operation_detail }}
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="operator_ip" label="IP地址" width="140" />
        
        <el-table-column prop="result" :label="$t('logs.status')" width="100">
          <template #default="{ row }">
            <el-tag 
              :type="getResultTagType(row.result)"
              size="small"
            >
              {{ row.result_display }}
            </el-tag>
        </template>
      </el-table-column>
    </el-table>
    </div>
    
    <!-- 分页 -->
    <div class="pagination-container">
      <div class="pagination-info">
        {{ $t('logs.showing') }} {{ Math.min((currentPage - 1) * pageSize + 1, totalLogs) }} {{ $t('common.to') }} {{ Math.min(currentPage * pageSize, totalLogs) }} {{ $t('common.of') }} {{ totalLogs }} {{ $t('logs.records') }}
      </div>
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[5, 10, 20, 50]"
        :total="totalLogs"
        layout="sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useI18n } from 'vue-i18n'
import {
  Search,
  Download,
  Delete
} from '@element-plus/icons-vue'
import axios from 'axios'

// API基础URL
const API_BASE = 'http://172.16.160.100:8003/api2'

// 国际化
const { t } = useI18n()

// 响应式数据
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(5)
const totalLogs = ref(0)

// 数据列表
const logs = ref([])

// 筛选器
const filters = reactive({
  operationType: '',
  operator: '',
  startTime: '',
  endTime: ''
})

// 模拟日志数据
const mockLogs = [
  {
    id: 1,
    operation_time: '2024-01-15T10:30:00',
    operator_name: 'admin',
    operation_type: 'login',
    operation_type_display: '登录',
    operation_target: '系统',
    operation_detail: '用户登录系统',
    operator_ip: '192.168.1.100',
    result: 'success',
    result_display: '成功',
    duration: 0.5
  },
  {
    id: 2,
    operation_time: '2024-01-15T11:15:00',
    operator_name: 'admin',
    operation_type: 'create',
    operation_type_display: '创建',
    operation_target: '机器人配置',
    operation_detail: '创建新的机器人配置: 型号X-1000',
    operator_ip: '192.168.1.100',
    result: 'success',
    result_display: '成功',
    duration: 1.2
  },
  {
    id: 3,
    operation_time: '2024-01-15T14:20:00',
    operator_name: 'operator1',
    operation_type: 'update',
    operation_type_display: '更新',
    operation_target: '任务调度',
    operation_detail: '更新任务#1234的执行参数',
    operator_ip: '192.168.1.101',
    result: 'success',
    result_display: '成功',
    duration: 0.8
  },
  {
    id: 4,
    operation_time: '2024-01-15T16:45:00',
    operator_name: 'admin',
    operation_type: 'config',
    operation_type_display: '系统设置',
    operation_target: '系统设置',
    operation_detail: '修改系统安全设置',
    operator_ip: '192.168.1.100',
    result: 'success',
    result_display: '成功',
    duration: 2.1
  },
  {
    id: 5,
    operation_time: '2024-01-15T17:30:00',
    operator_name: 'operator2',
    operation_type: 'delete',
    operation_type_display: '删除',
    operation_target: '录像文件',
    operation_detail: '删除录像文件: record_20240115_1630.mp4',
    operator_ip: '192.168.1.102',
    result: 'failed',
    result_display: '失败',
    duration: 0.3
  }
]

// 方法
const formatDateTime = (dateTimeStr) => {
  if (!dateTimeStr) return '-'
  const date = new Date(dateTimeStr)
  return date.toLocaleString('zh-CN')
}

const getOperationTypeTagType = (type) => {
  const typeMap = {
    'login': 'info',
    'logout': 'info',
    'create': 'success',
    'update': 'warning',
    'delete': 'danger',
    'export': 'primary',
    'config': 'warning',
    'user_mgmt': 'primary',
    'robot_mgmt': 'success',
    'task_mgmt': 'warning',
    'file_mgmt': 'info'
  }
  return typeMap[type] || 'info'
}

const getResultTagType = (result) => {
  const resultMap = {
    'success': 'success',
    'failed': 'danger',
    'warning': 'warning'
  }
  return resultMap[result] || 'info'
}

// 加载日志列表
const loadLogs = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    if (filters.operationType) params.operation_type = filters.operationType
    if (filters.operator) params.operator = filters.operator
    if (filters.startTime) params.start_time = new Date(filters.startTime).toISOString()
    if (filters.endTime) params.end_time = new Date(filters.endTime).toISOString()
    
    const response = await axios.get(`${API_BASE}/operation-logs`, { params })
    
    if (response.data.data) {
      // 新的分页响应格式
      logs.value = response.data.data
      totalLogs.value = response.data.total
      console.log('操作日志数据:', response.data)
    } else {
      // 旧的响应格式（兼容性）
      logs.value = response.data
      totalLogs.value = response.data.length
    }
  } catch (error) {
    console.error('加载操作日志失败:', error)
    ElMessage.error('加载操作日志失败')
    // 如果API失败，使用模拟数据作为后备
    logs.value = mockLogs
    totalLogs.value = mockLogs.length
  } finally {
    loading.value = false
  }
}

// 导出日志
const exportLogs = async () => {
  try {
    await ElMessageBox.confirm(
      t('logs.confirmExport'),
      t('logs.confirmExportTitle'),
      {
        confirmButtonText: t('common.confirm'),
        cancelButtonText: t('common.cancel'),
        type: 'info'
      }
    )
    
    const params = {}
    if (filters.operationType) params.operation_type = filters.operationType
    if (filters.startTime) params.start_time = new Date(filters.startTime).toISOString()
    if (filters.endTime) params.end_time = new Date(filters.endTime).toISOString()
    
    // 使用blob响应类型来处理文件下载
    const response = await axios.get(`${API_BASE}/operation-logs/export`, { 
      params,
      responseType: 'blob'
    })
    
    // 创建下载链接
    const blob = new Blob([response.data], { type: 'text/csv;charset=utf-8' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    
    // 生成文件名（包含当前时间）
    const now = new Date()
    const timestamp = now.toISOString().slice(0, 19).replace(/[:-]/g, '')
    link.download = `operation_logs_${timestamp}.csv`
    
    // 触发下载
    document.body.appendChild(link)
    link.click()
    
    // 清理
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success(t('logs.exportSuccess'))
  } catch (error) {
    if (error !== 'cancel') {
      console.error('导出日志失败:', error)
      
      // 如果是JSON错误响应，尝试解析错误信息
      if (error.response && error.response.data instanceof Blob) {
        try {
          const text = await error.response.data.text()
          const errorData = JSON.parse(text)
          ElMessage.error(errorData.message || t('logs.exportFailed'))
        } catch {
          ElMessage.error(t('logs.exportFailed'))
        }
      } else {
        ElMessage.error(t('logs.exportFailed'))
      }
    }
  }
}

// 清空日志
const clearLogs = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有操作日志吗？此操作不可恢复！',
      '确认清空',
      {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
      }
    )
    
    const response = await axios.delete(`${API_BASE}/operation-logs`)
    if (response.data.success) {
      ElMessage.success(response.data.message)
      loadLogs()
    } else {
      ElMessage.error(response.data.message)
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('清空日志失败:', error)
      ElMessage.error('清空日志失败')
    }
  }
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  loadLogs()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  loadLogs()
}

// 生命周期
onMounted(() => {
  loadLogs()
})
</script>

<style scoped>
.logs-container {
  padding: 24px;
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
  gap: 12px;
}

/* 筛选器区域 */
.filter-section {
  background: white;
  border-radius: 8px;
  padding: 20px 24px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.filter-row {
  display: flex;
  gap: 20px;
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

.filter-actions {
  display: flex;
  gap: 8px;
}

/* 表格容器 */
.table-container {
  background: white;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.logs-table {
  width: 100%;
}

.operation-detail {
  max-width: 300px;
  word-break: break-word;
  line-height: 1.4;
}

/* 分页 */
.pagination-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.pagination-info {
  font-size: 14px;
  color: #606266;
}

.pagination-controls {
  display: flex;
  gap: 8px;
  align-items: center;
}

.current-page {
  font-size: 14px;
  color: #409eff;
  font-weight: 500;
  margin: 0 12px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .logs-container {
    padding: 16px;
  }
  
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .filter-row {
    flex-direction: column;
    gap: 16px;
  }
  
  .filter-item {
    min-width: auto;
  }
  
  .pagination-container {
    flex-direction: column;
    gap: 16px;
  }
}
</style>