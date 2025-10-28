<template>
  <div class="log-audit">
    <!-- 页面标题和操作按钮 -->
    <div class="page-header">
      <h2>{{ $t('audit.title') }}</h2>
      <div class="header-actions">
        <el-button type="success" @click="exportAuditLogs">
          <el-icon><Download /></el-icon>
          {{ $t('audit.exportAuditLog') }}
        </el-button>
        <el-button type="primary" @click="generateAuditReport">
          <el-icon><Document /></el-icon>
          {{ $t('audit.generateAuditReport') }}
        </el-button>
      </div>
    </div>

    <!-- 筛选区域 -->
    <div class="filter-section">
      <el-form :model="filters" inline class="filter-form">
        <el-form-item :label="$t('audit.logType')">
          <el-select v-model="filters.log_type" :placeholder="$t('audit.all')" clearable>
            <el-option :label="$t('audit.all')" value="" />
            <el-option :label="$t('audit.systemLog')" value="system" />
            <el-option :label="$t('audit.securityLog')" value="security" />
            <el-option :label="$t('audit.operationLog')" value="operation" />
            <el-option :label="$t('audit.performanceLog')" value="performance" />
            <el-option :label="$t('audit.applicationLog')" value="application" />
          </el-select>
        </el-form-item>

        <el-form-item :label="$t('audit.logLevel')">
          <el-select v-model="filters.log_level" :placeholder="$t('audit.all')" clearable>
            <el-option :label="$t('audit.all')" value="" />
            <el-option :label="$t('audit.info')" value="INFO" />
            <el-option :label="$t('audit.warning')" value="WARNING" />
            <el-option :label="$t('audit.error')" value="ERROR" />
            <el-option :label="$t('audit.critical')" value="CRITICAL" />
            <el-option :label="$t('audit.debug')" value="DEBUG" />
          </el-select>
        </el-form-item>

        <el-form-item :label="$t('audit.sourceModule')">
          <el-input 
            v-model="filters.source_module" 
            :placeholder="$t('audit.moduleName')" 
            clearable
          />
        </el-form-item>

        <el-form-item :label="$t('audit.startTime')">
          <el-date-picker
            v-model="filters.start_time"
            type="datetime"
            :placeholder="$t('audit.selectStartTime')"
            format="YYYY/MM/DD HH:mm"
            value-format="YYYY-MM-DD HH:mm:ss"
            clearable
          />
        </el-form-item>

        <el-form-item :label="$t('audit.endTime')">
          <el-date-picker
            v-model="filters.end_time"
            type="datetime"
            :placeholder="$t('audit.selectEndTime')"
            format="YYYY/MM/DD HH:mm"
            value-format="YYYY-MM-DD HH:mm:ss"
            clearable
          />
        </el-form-item>

        <el-form-item>
          <el-button @click="resetFilters">{{ $t('audit.reset') }}</el-button>
          <el-button type="primary" @click="searchLogs">{{ $t('audit.query') }}</el-button>
          <el-button @click="toggleAdvancedFilter">{{ $t('audit.advancedFilter') }}</el-button>
        </el-form-item>
      </el-form>

      <!-- 高级筛选区域 -->
      <div v-if="showAdvancedFilter" class="advanced-filter-section">
        <el-form :model="filters" inline class="advanced-filter-form">
          <el-form-item :label="$t('audit.userId')">
            <el-input 
              v-model="filters.user_id" 
              :placeholder="$t('audit.userIdPlaceholder')" 
              clearable
              style="width: 200px"
            />
          </el-form-item>

          <el-form-item :label="$t('audit.ipAddress')">
            <el-input 
              v-model="filters.ip_address" 
              :placeholder="$t('audit.ipAddressPlaceholder')" 
              clearable
              style="width: 200px"
            />
          </el-form-item>

          <el-form-item :label="$t('audit.keyword')">
            <el-input 
              v-model="filters.keyword" 
              :placeholder="$t('audit.keywordPlaceholder')" 
              clearable
              style="width: 200px"
            />
          </el-form-item>
        </el-form>
      </div>
    </div>

    <!-- 日志表格 -->
    <div class="log-table-section">
      <el-table :data="auditLogs" v-loading="loading" stripe>
        <el-table-column prop="timestamp" :label="$t('audit.timestamp')" width="180">
          <template #default="{ row }">
            {{ formatTimestamp(row.timestamp) }}
          </template>
        </el-table-column>

        <el-table-column prop="log_type" :label="$t('audit.logType')" width="120">
          <template #default="{ row }">
            <el-tag :type="getLogTypeTag(row.log_type)">
              {{ getLogTypeText(row.log_type) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="level" :label="$t('audit.level')" width="100">
          <template #default="{ row }">
            <el-tag :type="getLevelTag(row.level)">
              {{ row.level }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="source_module" :label="$t('audit.sourceModule')" width="150" />

        <el-table-column prop="message" :label="$t('audit.messageContent')" min-width="300">
          <template #default="{ row }">
            <div class="message-content">
              <div class="message-text">{{ row.message }}</div>
              <div v-if="row.details" class="message-details">
                <el-button type="text" size="small" @click="showDetails(row)">
                  {{ $t('audit.viewDetails') }}
                </el-button>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="user" :label="$t('audit.user')" width="120" />

        <el-table-column prop="ip_address" :label="$t('audit.ipAddress')" width="140">
          <template #default="{ row }">
            {{ row.ip_address || 'N/A' }}
          </template>
        </el-table-column>

        <el-table-column :label="$t('audit.operation')" width="150" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button type="primary" size="small" @click="showDetails(row)" link>
                {{ $t('audit.viewDetails') }}
              </el-button>
              <el-button type="success" size="small" @click="exportSingleLog(row)" link>
                {{ $t('audit.export') }}
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- 日志详情对话框 -->
    <el-dialog 
      v-model="detailDialogVisible" 
      :title="$t('audit.logDetails')" 
      width="800px"
    >
      <div v-if="selectedLog" class="log-details">
        <el-descriptions :column="2" border>
          <el-descriptions-item :label="$t('audit.timestamp')">
            {{ formatTimestamp(selectedLog.timestamp) }}
          </el-descriptions-item>
          <el-descriptions-item :label="$t('audit.logType')">
            <el-tag :type="getLogTypeTag(selectedLog.log_type)">
              {{ getLogTypeText(selectedLog.log_type) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item :label="$t('audit.level')">
            <el-tag :type="getLevelTag(selectedLog.level)">
              {{ selectedLog.level }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item :label="$t('audit.sourceModule')">
            {{ selectedLog.source_module }}
          </el-descriptions-item>
          <el-descriptions-item :label="$t('audit.user')">
            {{ selectedLog.user }}
          </el-descriptions-item>
          <el-descriptions-item :label="$t('audit.ipAddress')">
            {{ selectedLog.ip_address || 'N/A' }}
          </el-descriptions-item>
          <el-descriptions-item :label="$t('audit.messageContent')" :span="2">
            {{ selectedLog.message }}
          </el-descriptions-item>
          <el-descriptions-item v-if="selectedLog.details" :label="$t('audit.details')" :span="2">
            <pre class="details-json">{{ formatDetails(selectedLog.details) }}</pre>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">{{ $t('common.close') }}</el-button>
        <el-button type="primary" @click="exportSingleLog(selectedLog)">{{ $t('audit.export') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useI18n } from 'vue-i18n'
import {
  Download,
  Document
} from '@element-plus/icons-vue'
import axios from 'axios'

// API基础URL
const API_BASE = 'http://172.16.160.100:8003/api2'

// 国际化
const { t } = useI18n()

// 响应式数据
const loading = ref(false)
const auditLogs = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

// 筛选条件
const filters = reactive({
  log_type: '',
  log_level: '',
  source_module: '',
  start_time: '',
  end_time: '',
  user_id: '',
  ip_address: '',
  keyword: ''
})

// 高级筛选显示状态
const showAdvancedFilter = ref(false)

// 详情对话框
const detailDialogVisible = ref(false)
const selectedLog = ref(null)

// 加载审计日志
const loadAuditLogs = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      ...filters
    }
    
    // 移除空值
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null || params[key] === undefined) {
        delete params[key]
      }
    })

    const response = await axios.get(`${API_BASE}/audit-logs`, { params })
    
    if (response.data.error) {
      ElMessage.error(response.data.error)
      return
    }
    
    auditLogs.value = response.data.data
    total.value = response.data.total
  } catch (error) {
    console.error('加载审计日志失败:', error)
    ElMessage.error(t('audit.loadLogsFailed'))
  } finally {
    loading.value = false
  }
}

// 搜索日志
const searchLogs = () => {
  currentPage.value = 1
  loadAuditLogs()
}

// 重置筛选条件
const resetFilters = () => {
  Object.keys(filters).forEach(key => {
    filters[key] = ''
  })
  showAdvancedFilter.value = false
  currentPage.value = 1
  loadAuditLogs()
}

// 切换高级筛选显示
const toggleAdvancedFilter = () => {
  showAdvancedFilter.value = !showAdvancedFilter.value
}

// 导出审计日志
const exportAuditLogs = async () => {
  try {
    const params = { ...filters }
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null || params[key] === undefined) {
        delete params[key]
      }
    })

    const response = await axios.get(`${API_BASE}/audit-logs/export`, {
      params,
      responseType: 'blob'
    })
    
    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.download = `audit_logs_${new Date().toISOString().split('T')[0]}.csv`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success(t('audit.exportSuccess'))
  } catch (error) {
    console.error('导出审计日志失败:', error)
    ElMessage.error(t('audit.exportFailed'))
  }
}

// 生成审计报告
const generateAuditReport = async () => {
  try {
    const response = await axios.post(`${API_BASE}/audit-logs/report`, filters)
    
    if (response.data.success) {
      ElMessage.success(response.data.message)
    } else {
      ElMessage.error(response.data.message)
    }
  } catch (error) {
    console.error('生成审计报告失败:', error)
    ElMessage.error(t('audit.generateReportFailed'))
  }
}

// 显示日志详情
const showDetails = (log) => {
  selectedLog.value = log
  detailDialogVisible.value = true
}

// 导出单个日志
const exportSingleLog = async (log) => {
  try {
    const response = await axios.get(`${API_BASE}/audit-logs/${log.id}/export`, {
      responseType: 'blob'
    })
    
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.download = `audit_log_${log.id}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success(t('audit.exportSuccess'))
  } catch (error) {
    console.error('导出单个日志失败:', error)
    ElMessage.error(t('audit.exportFailed'))
  }
}

// 分页处理
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  loadAuditLogs()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  loadAuditLogs()
}

// 格式化时间戳
const formatTimestamp = (timestamp) => {
  if (!timestamp) return '-'
  return new Date(timestamp).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 获取日志类型标签样式
const getLogTypeTag = (type) => {
  const typeMap = {
    'system': 'primary',
    'security': 'danger',
    'operation': 'success',
    'performance': 'warning',
    'application': 'info'
  }
  return typeMap[type] || ''
}

// 获取日志类型文本
const getLogTypeText = (type) => {
  const typeMap = {
    'system': t('audit.systemLog'),
    'security': t('audit.securityLog'),
    'operation': t('audit.operationLog'),
    'performance': t('audit.performanceLog'),
    'application': t('audit.applicationLog')
  }
  return typeMap[type] || type
}

// 获取级别标签样式
const getLevelTag = (level) => {
  const levelMap = {
    'DEBUG': 'info',
    'INFO': 'success',
    'WARNING': 'warning',
    'ERROR': 'danger',
    'CRITICAL': 'danger'
  }
  return levelMap[level] || ''
}

// 格式化详情JSON
const formatDetails = (details) => {
  try {
    return JSON.stringify(JSON.parse(details), null, 2)
  } catch {
    return details
  }
}

// 页面加载时初始化
onMounted(() => {
  loadAuditLogs()
})
</script>

<style scoped>
.log-audit {
  padding: 24px;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0;
  font-size: 24px;
  color: #1f2937;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.filter-section {
  background: white;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.filter-form {
  margin: 0;
}

.filter-form .el-form-item {
  margin-bottom: 16px;
}

.advanced-filter-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e4e7ed;
}

.advanced-filter-form {
  margin: 0;
}

.advanced-filter-form .el-form-item {
  margin-bottom: 16px;
  margin-right: 24px;
}

.log-table-section {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.message-content {
  max-width: 100%;
}

.message-text {
  margin-bottom: 8px;
  word-break: break-word;
}

.message-details {
  font-size: 12px;
  color: #666;
}

.action-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.log-details {
  max-height: 500px;
  overflow-y: auto;
}

.details-json {
  background-color: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 200px;
  overflow-y: auto;
}
</style>
