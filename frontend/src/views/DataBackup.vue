<template>
  <div class="data-backup">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>{{ $t('backup.title') }}</h2>
      <el-button type="primary" @click="showAutoBackupSettings">
        {{ $t('backup.autoBackupSettings') }}
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-icon">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-label">{{ $t('backup.lastBackupTime') }}</div>
          <div class="stat-value">{{ formatBackupTime(stats.last_backup_time) }}</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon" :class="getStatusClass(stats.backup_status)">
          <el-icon>
            <CircleCheck v-if="stats.backup_status === 'normal'" />
            <Warning v-else-if="stats.backup_status === 'warning'" />
            <CircleClose v-else />
          </el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-label">{{ $t('backup.backupStatus') }}</div>
          <div class="stat-value">{{ getStatusText(stats.backup_status) }}</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">
          <el-icon><Files /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-label">{{ $t('backup.backupFileCount') }}</div>
          <div class="stat-value">{{ stats.backup_count }}</div>
        </div>
      </div>
    </div>

    <!-- 备份文件列表 -->
    <div class="backup-list-section">
      <div class="section-header">
        <h3>{{ $t('backup.backupFileList') }}</h3>
        <el-dropdown @command="handleCreateBackup">
          <el-button type="primary">
            {{ $t('backup.createBackup') }}
            <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="full">{{ $t('backup.fullBackup') }}</el-dropdown-item>
              <el-dropdown-item command="incremental">{{ $t('backup.incrementalBackup') }}</el-dropdown-item>
              <el-dropdown-item command="differential">{{ $t('backup.differentialBackup') }}</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>

      <!-- 备份文件表格 -->
      <el-table :data="backups" v-loading="loading" stripe>
        <el-table-column prop="name" :label="$t('backup.backupName')" min-width="200" />
        <el-table-column prop="created_at" :label="$t('backup.createdTime')" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="file_size_display" :label="$t('backup.size')" width="100" />
        <el-table-column prop="backup_type_display" :label="$t('backup.type')" width="120">
          <template #default="{ row }">
            <el-tag :type="getBackupTypeTag(row.backup_type)">
              {{ row.backup_type_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status_display" :label="$t('backup.status')" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)">
              {{ row.status_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="$t('backup.actions')" width="200" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button 
                type="primary" 
                size="small" 
                @click="downloadBackup(row)"
                :disabled="row.status !== 'completed'"
                link
              >
                <el-icon><Download /></el-icon>
                {{ $t('backup.download') }}
              </el-button>
              <el-button 
                type="success" 
                size="small" 
                @click="restoreBackup(row)"
                :disabled="row.status !== 'completed'"
                link
              >
                <el-icon><Refresh /></el-icon>
                {{ $t('backup.restore') }}
              </el-button>
              <el-button 
                type="danger" 
                size="small" 
                @click="deleteBackup(row)"
                link
              >
                <el-icon><Delete /></el-icon>
                {{ $t('backup.delete') }}
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

    <!-- 自动备份设置对话框 -->
    <el-dialog 
      v-model="autoBackupDialogVisible" 
      :title="$t('backup.autoBackupSettings')" 
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form :model="backupSettings" label-width="140px" class="backup-settings-form">
        <el-form-item :label="$t('backup.enableAutoBackup')">
          <el-switch 
            v-model="backupSettings.auto_backup_enabled" 
            :active-text="$t('backup.enabled')"
            :inactive-text="$t('backup.disabled')"
          />
        </el-form-item>
        
        <el-form-item :label="$t('backup.backupFrequency')">
          <el-select v-model="backupSettings.backup_frequency" style="width: 200px">
            <el-option :label="$t('backup.daily')" value="daily" />
            <el-option :label="$t('backup.weekly')" value="weekly" />
            <el-option :label="$t('backup.monthly')" value="monthly" />
          </el-select>
        </el-form-item>
        
        <el-form-item :label="$t('backup.maxBackupFiles')">
          <el-input-number 
            v-model="backupSettings.max_backup_files" 
            :min="1" 
            :max="100"
            style="width: 200px"
          />
        </el-form-item>
        
        <el-form-item :label="$t('backup.backupType')">
          <el-select v-model="backupSettings.backup_type" style="width: 200px">
            <el-option :label="$t('backup.fullBackup')" value="full" />
            <el-option :label="$t('backup.incrementalBackup')" value="incremental" />
            <el-option :label="$t('backup.differentialBackup')" value="differential" />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="autoBackupDialogVisible = false" size="large">
            {{ $t('common.cancel') }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useI18n } from 'vue-i18n'
import {
  Clock,
  CircleCheck,
  Warning,
  CircleClose,
  Files,
  ArrowDown,
  Download,
  Refresh,
  Delete
} from '@element-plus/icons-vue'
import axios from 'axios'

// API基础URL
const API_BASE = 'http://172.16.160.100:8003/api2'

// 国际化
const { t } = useI18n()

// 响应式数据
const loading = ref(false)
const backups = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

// 统计数据
const stats = reactive({
  last_backup_time: null,
  backup_status: 'normal',
  backup_count: 0,
  total_size: 0
})

// 自动备份设置
const autoBackupDialogVisible = ref(false)
const backupSettings = reactive({
  auto_backup_enabled: true,
  backup_frequency: 'daily',
  max_backup_files: 30,
  backup_type: 'full'
})

// 加载统计数据
const loadStats = async () => {
  try {
    const response = await axios.get(`${API_BASE}/backups/stats`)
    if (response.data.error) {
      ElMessage.error(response.data.error)
      return
    }
    Object.assign(stats, response.data)
  } catch (error) {
    console.error('加载统计数据失败:', error)
    ElMessage.error(t('backup.loadStatsFailed'))
  }
}

// 加载备份列表
const loadBackups = async () => {
  loading.value = true
  try {
    const response = await axios.get(`${API_BASE}/backups`, {
      params: {
        page: currentPage.value,
        page_size: pageSize.value
      }
    })
    
    if (response.data.error) {
      ElMessage.error(response.data.error)
      return
    }
    
    backups.value = response.data.data
    total.value = response.data.total
  } catch (error) {
    console.error('加载备份列表失败:', error)
    ElMessage.error(t('backup.loadBackupsFailed'))
  } finally {
    loading.value = false
  }
}

// 创建备份
const handleCreateBackup = async (backupType) => {
  try {
    await ElMessageBox.confirm(
      t('backup.confirmCreateBackup'),
      t('backup.confirmCreateBackupTitle'),
      {
        confirmButtonText: t('common.confirm'),
        cancelButtonText: t('common.cancel'),
        type: 'info'
      }
    )
    
    const response = await axios.post(`${API_BASE}/backups`, {
      backup_type: backupType
    })
    
    if (response.data.success) {
      ElMessage.success(response.data.message)
      loadBackups()
      loadStats()
    } else {
      ElMessage.error(response.data.message)
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('创建备份失败:', error)
      ElMessage.error(t('backup.createBackupFailed'))
    }
  }
}

// 下载备份
const downloadBackup = async (backup) => {
  try {
    // 创建下载链接并触发下载
    const downloadUrl = `${API_BASE}/backups/${backup.id}/download`
    
    // 创建临时链接元素
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = `${backup.name}.sql.gz`
    link.target = '_blank'
    
    // 添加到页面并点击
    document.body.appendChild(link)
    link.click()
    
    // 清理临时元素
    document.body.removeChild(link)
    
    ElMessage.success(t('backup.downloadSuccess'))
  } catch (error) {
    console.error('下载备份失败:', error)
    ElMessage.error(t('backup.downloadFailed'))
  }
}

// 恢复备份
const restoreBackup = async (backup) => {
  try {
    await ElMessageBox.confirm(
      t('backup.confirmRestore'),
      t('backup.confirmRestoreTitle'),
      {
        confirmButtonText: t('common.confirm'),
        cancelButtonText: t('common.cancel'),
        type: 'warning'
      }
    )
    
    const response = await axios.post(`${API_BASE}/backups/${backup.id}/restore`)
    
    if (response.data.success) {
      ElMessage.success(response.data.message)
    } else {
      ElMessage.error(response.data.message)
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('恢复备份失败:', error)
      ElMessage.error(t('backup.restoreFailed'))
    }
  }
}

// 删除备份
const deleteBackup = async (backup) => {
  try {
    await ElMessageBox.confirm(
      t('backup.confirmDelete'),
      t('backup.confirmDeleteTitle'),
      {
        confirmButtonText: t('common.confirm'),
        cancelButtonText: t('common.cancel'),
        type: 'warning'
      }
    )
    
    const response = await axios.delete(`${API_BASE}/backups/${backup.id}`)
    
    if (response.data.success) {
      ElMessage.success(response.data.message)
      loadBackups()
      loadStats()
    } else {
      ElMessage.error(response.data.message)
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除备份失败:', error)
      ElMessage.error(t('backup.deleteFailed'))
    }
  }
}

// 显示自动备份设置
const showAutoBackupSettings = async () => {
  try {
    const response = await axios.get(`${API_BASE}/backup-settings`)
    if (response.data.error) {
      ElMessage.error(response.data.error)
      return
    }
    Object.assign(backupSettings, response.data)
    autoBackupDialogVisible.value = true
  } catch (error) {
    console.error('加载备份设置失败:', error)
    ElMessage.error(t('backup.loadSettingsFailed'))
  }
}

// 保存备份设置
const saveBackupSettings = async () => {
  try {
    const response = await axios.put(`${API_BASE}/backup-settings`, backupSettings)
    
    if (response.data.success) {
      ElMessage.success(response.data.message)
      autoBackupDialogVisible.value = false
    } else {
      ElMessage.error(response.data.message)
    }
  } catch (error) {
    console.error('保存备份设置失败:', error)
    ElMessage.error(t('backup.saveSettingsFailed'))
  }
}

// 分页处理
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  loadBackups()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  loadBackups()
}

// 格式化时间
const formatTime = (timeStr) => {
  if (!timeStr) return '-'
  return new Date(timeStr).toLocaleString()
}

const formatBackupTime = (timeStr) => {
  if (!timeStr) return t('backup.noBackup')
  return new Date(timeStr).toLocaleString()
}

// 获取状态样式类
const getStatusClass = (status) => {
  switch (status) {
    case 'normal': return 'status-success'
    case 'warning': return 'status-warning'
    default: return 'status-error'
  }
}

// 获取状态文本
const getStatusText = (status) => {
  switch (status) {
    case 'normal': return t('backup.statusNormal')
    case 'warning': return t('backup.statusWarning')
    case 'error': return t('backup.statusError')
    default: return t('backup.statusUnknown')
  }
}

// 获取备份类型标签样式
const getBackupTypeTag = (type) => {
  switch (type) {
    case 'full': return 'success'
    case 'incremental': return 'warning'
    case 'differential': return 'info'
    default: return ''
  }
}

// 获取状态标签样式
const getStatusTag = (status) => {
  switch (status) {
    case 'completed': return 'success'
    case 'running': return 'warning'
    case 'failed': return 'danger'
    case 'cancelled': return 'info'
    default: return ''
  }
}

// 页面加载时初始化
onMounted(() => {
  loadStats()
  loadBackups()
})
</script>

<style scoped>
.data-backup {
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

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 24px;
  display: flex;
  align-items: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  background-color: #e0f2fe;
  color: #0277bd;
}

.stat-icon.status-success {
  background-color: #e8f5e8;
  color: #2e7d32;
}

.stat-icon.status-warning {
  background-color: #fff3e0;
  color: #f57c00;
}

.stat-icon.status-error {
  background-color: #ffebee;
  color: #d32f2f;
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
}

.backup-list-section {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  margin: 0;
  font-size: 18px;
  color: #1f2937;
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

.backup-settings-form {
  padding: 20px 0;
}

.backup-settings-form .el-form-item {
  margin-bottom: 24px;
}

.backup-settings-form .el-form-item__label {
  font-weight: 500;
  color: #374151;
}

.dialog-footer {
  text-align: center;
  padding: 20px 0 0 0;
}
</style>