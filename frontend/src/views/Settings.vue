<template>
  <div class="settings-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">{{ $t('settings.title') }}</h1>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="restoreDefaults">
          {{ $t('settings.restoreDefaults') }}
        </el-button>
      </div>
    </div>

    <!-- 设置标签页 -->
    <div class="settings-content">
    <el-tabs v-model="activeTab" class="settings-tabs">
        <!-- 常规设置 -->
        <el-tab-pane :label="$t('settings.generalSettings')" name="general">
          <div class="settings-form">
            <div class="form-section">
              <div class="form-row">
                <div class="form-item">
                  <label class="form-label">{{ $t('settings.systemName') }}</label>
                  <el-input 
                    v-model="generalSettings.system_name" 
                    placeholder="请输入系统名称"
                    class="form-input"
                  />
                </div>
            </div>
              
              <div class="form-row">
                <div class="form-item">
                  <label class="form-label">{{ $t('settings.systemVersion') }}</label>
                  <el-input 
                    v-model="generalSettings.system_version" 
                    disabled
                    class="form-input"
                  />
                </div>
              </div>
              
              <div class="form-row">
                <div class="form-item half-width">
                  <label class="form-label">{{ $t('settings.timezone') }}</label>
                  <el-select 
                    v-model="generalSettings.timezone" 
                    placeholder="选择时区"
                    class="form-input"
                  >
                    <el-option label="中国标准时间 (UTC+8)" value="Asia/Shanghai" />
                    <el-option label="美国东部时间 (UTC-5)" value="America/New_York" />
                    <el-option label="欧洲中部时间 (UTC+1)" value="Europe/Paris" />
                  </el-select>
                </div>
                
                <div class="form-item half-width">
                  <label class="form-label">{{ $t('settings.language') }}</label>
                  <el-select
                    v-model="generalSettings.language"
                    :placeholder="$t('settings.language')"
                    class="form-input"
                    @change="handleLanguageChange"
                  >
                    <el-option :label="$t('settings.chinese')" value="zh-CN" />
                    <el-option :label="$t('settings.english')" value="en-US" />
                    <el-option :label="$t('settings.japanese')" value="ja-JP" />
                  </el-select>
                </div>
              </div>
              
              <div class="form-row">
                <div class="form-item">
                  <label class="form-label">{{ $t('settings.systemDescription') }}</label>
              <el-input
                    v-model="generalSettings.system_description" 
                type="textarea"
                    :rows="4"
                placeholder="请输入系统描述"
                    class="form-input"
                  />
                </div>
              </div>
            </div>
          </div>
      </el-tab-pane>

      <!-- 安全设置 -->
        <el-tab-pane :label="$t('settings.securitySettings')" name="security">
          <div class="settings-form">
            <div class="form-section">
              <div class="form-row">
                <div class="form-item half-width">
                  <label class="form-label">{{ $t('settings.speed') }}</label>
                  <el-select 
                    v-model="securitySettings.password_strength" 
                    class="form-input"
                  >
                    <el-option label="低强度" value="low" />
                    <el-option label="中等强度" value="medium" />
                    <el-option label="高强度" value="high" />
                  </el-select>
            </div>
                
                <div class="form-item half-width">
                  <label class="form-label">{{ $t('settings.sessionTimeout') }}</label>
                  <el-select 
                    v-model="securitySettings.session_timeout" 
                    class="form-input"
                  >
                    <el-option label="30分钟" :value="30" />
                    <el-option label="60分钟" :value="60" />
                    <el-option label="120分钟" :value="120" />
                  </el-select>
                </div>
              </div>
              
              <div class="form-row">
                <div class="form-item half-width">
                  <label class="form-label">{{ $t('settings.passwordPolicy') }}</label>
                  <el-select 
                    v-model="securitySettings.password_strength" 
                    class="form-input"
                  >
                    <el-option label="低强度" value="low" />
                    <el-option label="中等强度" value="medium" />
                    <el-option label="高强度" value="high" />
                  </el-select>
                </div>
                
                <div class="form-item half-width">
                  <label class="form-label">{{ $t('settings.maxLoginAttempts') }}</label>
                  <el-input 
                    v-model.number="securitySettings.max_login_attempts" 
                    type="number"
                    class="form-input"
                  />
                </div>
              </div>
              
              <div class="form-row">
                <div class="form-item half-width">
                  <label class="form-label">{{ $t('settings.accountLockoutTime') }}</label>
                  <el-select 
                    v-model="securitySettings.account_lockout_time" 
                    class="form-input"
                  >
                    <el-option label="15分钟" :value="15" />
                    <el-option label="30分钟" :value="30" />
                    <el-option label="60分钟" :value="60" />
                  </el-select>
                </div>
              </div>
              
              <div class="form-section-title">{{ $t('settings.securityOptions') }}</div>
              <div class="checkbox-group">
                <el-checkbox v-model="securitySettings.two_factor_auth">
                  {{ $t('settings.twoFactorAuth') }}
                </el-checkbox>
                <el-checkbox v-model="securitySettings.force_password_change">
                  {{ $t('settings.forcePasswordChange') }}
                </el-checkbox>
                <el-checkbox v-model="securitySettings.audit_logging">
                  {{ $t('settings.auditLogging') }}
                </el-checkbox>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- 通知设置设置 -->
        <el-tab-pane :label="$t('settings.notificationSettings')" name="notification">
          <div class="settings-form">
            <div class="form-section">
              <div class="form-section-title">{{ $t('settings.notificationMethods') }}</div>
              <div class="checkbox-group">
                <div class="checkbox-row">
                  <el-checkbox v-model="notificationSettings.email_enabled">
                    {{ $t('settings.emailNotification') }}
                  </el-checkbox>
                  <el-checkbox v-model="notificationSettings.sms_enabled">
                    {{ $t('settings.smsNotification') }}
                  </el-checkbox>
                </div>
                <div class="checkbox-row">
                  <el-checkbox v-model="notificationSettings.push_enabled">
                    {{ $t('settings.pushNotification') }}
                  </el-checkbox>
                  <el-checkbox v-model="notificationSettings.webhook_enabled">
                    {{ $t('settings.webhookNotification') }}
                  </el-checkbox>
                </div>
              </div>
              
              <div class="form-section-title">{{ $t('settings.emailServerConfig') }}</div>
              <div class="form-row">
                <div class="form-item half-width">
                  <label class="form-label">{{ $t('settings.smtpServer') }}</label>
                  <el-input 
                    v-model="notificationSettings.smtp_server" 
                    placeholder="请输入SMTP服务器"
                    class="form-input"
                  />
                </div>
                
                <div class="form-item half-width">
                  <label class="form-label">{{ $t('settings.smtpPort') }}</label>
                  <el-input 
                    v-model.number="notificationSettings.smtp_port" 
                    placeholder="587"
                    class="form-input"
                  />
                </div>
              </div>
              
              <div class="form-row">
                <div class="form-item half-width">
                  <label class="form-label">{{ $t('settings.senderEmail') }}</label>
                  <el-input 
                    v-model="notificationSettings.smtp_username" 
                    placeholder="noreply@example.com"
                    class="form-input"
                  />
                </div>
                
                <div class="form-item half-width">
                  <label class="form-label">{{ $t('settings.senderName') }}</label>
                  <el-input 
                    v-model="notificationSettings.sender_name" 
                    placeholder="系统通知"
                    class="form-input"
                  />
                </div>
              </div>
              
              <div class="form-section-title">{{ $t('settings.notificationEvents') }}</div>
              <div class="checkbox-group">
                <div class="checkbox-row">
                  <el-checkbox v-model="notificationSettings.system_error_notify">
                    {{ $t('settings.systemError') }}
                  </el-checkbox>
                  <el-checkbox v-model="notificationSettings.security_alert_notify">
                    {{ $t('settings.securityAlert') }}
                  </el-checkbox>
                </div>
                <div class="checkbox-row">
                  <span class="checkbox-item">false</span>
                  <span class="label-text">性能问题</span>
                  <el-checkbox v-model="notificationSettings.task_complete_notify">
                    {{ $t('settings.backupComplete') }}
                  </el-checkbox>
                </div>
              </div>
            </div>
          </div>
      </el-tab-pane>

        <!-- 性能设置 -->
        <el-tab-pane :label="$t('settings.performanceSettings')" name="performance">
          <div class="settings-form">
            <div class="form-section">
              <div class="form-row">
                <div class="form-item half-width">
                  <label class="form-label">{{ $t('settings.dataRetentionTime') }}</label>
                  <el-select 
                    v-model="performanceSettings.data_retention_days" 
                    class="form-input"
                  >
                    <el-option label="30天" :value="30" />
                    <el-option label="90天" :value="90" />
                    <el-option label="180天" :value="180" />
                    <el-option label="365天" :value="365" />
                  </el-select>
            </div>
                
                <div class="form-item half-width">
                  <label class="form-label">{{ $t('settings.logLevel') }}</label>
                  <el-select 
                    v-model="performanceSettings.log_level" 
                    class="form-input"
                  >
                    <el-option label="调试" value="DEBUG" />
                    <el-option label="信息" value="INFO" />
                    <el-option label="警告" value="WARNING" />
                    <el-option label="错误" value="ERROR" />
                  </el-select>
                </div>
              </div>
              
              <div class="form-row">
                <div class="form-item half-width">
                  <label class="form-label">{{ $t('settings.autoBackupInterval') }}</label>
                  <el-select 
                    v-model="performanceSettings.backup_interval" 
                    class="form-input"
                  >
                    <el-option label="每天极速" value="daily" />
                <el-option label="每周" value="weekly" />
                <el-option label="每月" value="monthly" />
              </el-select>
                </div>
                
                <div class="form-item half-width">
                  <label class="form-label">{{ $t('settings.monitoringInterval') }}</label>
                  <el-select 
                    v-model="performanceSettings.monitoring_interval" 
                    class="form-input"
                  >
                    <el-option label="30秒" :value="30" />
                    <el-option label="60秒" :value="60" />
                    <el-option label="120秒" :value="120" />
                  </el-select>
                </div>
              </div>
              
              <div class="form-section-title">{{ $t('settings.performanceOptimization') }}</div>
              <div class="checkbox-group">
                <el-checkbox v-model="performanceSettings.enable_data_compression">
                  {{ $t('settings.enableDataCache') }}
                </el-checkbox>
                <el-checkbox v-model="performanceSettings.enable_cache_optimization">
                  {{ $t('settings.enableCacheOptimization') }}
                </el-checkbox>
                <el-checkbox v-model="performanceSettings.enable_realtime_monitoring">
                  {{ $t('settings.enableRealtimeMonitoring') }}
                </el-checkbox>
              </div>
            </div>
          </div>
      </el-tab-pane>
    </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useI18n } from 'vue-i18n'
import axios from 'axios'

// API基础URL
const API_BASE = 'http://172.16.160.100:8003/api'

// 国际化
const { t, locale } = useI18n()

// 导入语言切换函数
import { changeLanguage } from '../main.js'

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const activeTab = ref('general')

// 常规设置
const generalSettings = reactive({
  system_name: '国粒智能边缘控制台',
  system_version: 'v2.1.0',
  timezone: 'Asia/Shanghai',
  language: 'zh-CN',
  system_description: '智能机器人管理与监控系统'
})

// 安全设置
const securitySettings = reactive({
  session_timeout: 60,
  password_strength: 'medium',
  max_login_attempts: 5,
  account_lockout_time: 30,
  two_factor_auth: false,
  force_password_change: true,
  audit_logging: true
})

// 通知设置
const notificationSettings = reactive({
  email_enabled: true,
  sms_enabled: false,
  push_enabled: true,
  webhook_enabled: false,
  smtp_server: '',
  smtp_port: 587,
  smtp_username: 'noreply@example.com',
  sender_name: '系统通知',
  system_error_notify: true,
  security_alert_notify: true,
  task_complete_notify: true
})

// 性能设置
const performanceSettings = reactive({
  data_retention_days: 90,
  log_level: 'INFO',
  auto_backup_enabled: false,
  backup_interval: 'daily',
  monitoring_interval: 60,
  enable_data_compression: true,
  enable_cache_optimization: false,
  enable_realtime_monitoring: true
})

// 语言切换处理
const handleLanguageChange = async (newLanguage) => {
  try {
    // 使用全局语言切换函数
    await changeLanguage(newLanguage)

    // 更新本地设置
    generalSettings.language = newLanguage

    // 保存到后端
    await axios.put(`${API_BASE}/settings/general`, generalSettings)

    ElMessage.success(newLanguage === 'zh-CN' ? '语言已切换为中文' : 'Language switched to English')

    // 延迟刷新页面确保所有组件都更新
    setTimeout(() => {
      window.location.reload()
    }, 1000)
  } catch (error) {
    console.error('保存语言设置失败:', error)
    ElMessage.error('保存语言设置失败')
  }
}

// 加载设置数据
const loadGeneralSettings = async () => {
  try {
    const response = await axios.get(`${API_BASE}/settings/general`)
    Object.assign(generalSettings, response.data)
    
    // 同步语言设置
    if (response.data.language && response.data.language !== locale.value) {
      locale.value = response.data.language
      localStorage.setItem('language', response.data.language)
    }
  } catch (error) {
    console.error('加载常规设置失败:', error)
  }
}

const loadSecuritySettings = async () => {
  try {
    const response = await axios.get(`${API_BASE}/settings/security`)
    Object.assign(securitySettings, response.data)
  } catch (error) {
    console.error('加载安全设置失败:', error)
  }
}

const loadNotificationSettings = async () => {
  try {
    const response = await axios.get(`${API_BASE}/settings/notification`)
    Object.assign(notificationSettings, response.data)
  } catch (error) {
    console.error('加载通知设置失败:', error)
  }
}

const loadPerformanceSettings = async () => {
  try {
    const response = await axios.get(`${API_BASE}/settings/performance`)
    Object.assign(performanceSettings, response.data)
  } catch (error) {
    console.error('加载性能设置失败:', error)
  }
}

// 保存设置
const saveCurrentTabSettings = async () => {
  saving.value = true
  try {
    let response
    switch (activeTab.value) {
      case 'general':
        response = await axios.put(`${API_BASE}/settings/general`, generalSettings)
        break
      case 'security':
        response = await axios.put(`${API_BASE}/settings/security`, securitySettings)
        break
      case 'notification':
        response = await axios.put(`${API_BASE}/settings/notification`, notificationSettings)
        break
      case 'performance':
        response = await axios.put(`${API_BASE}/settings/performance`, performanceSettings)
        break
    }
    
    if (response?.data?.success) {
      ElMessage.success(response.data.message || '设置保存成功')
    } else {
      ElMessage.error('设置保存失败')
    }
  } catch (error) {
    console.error('保存设置失败:', error)
    ElMessage.error('设置保存失败')
  } finally {
    saving.value = false
  }
}

// 恢复默认设置
const restoreDefaults = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要恢复当前标签页的默认设置吗？此操作不可撤销。',
      '确认恢复默认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await axios.post(`${API_BASE}/settings/restore-defaults`, {
      setting_type: activeTab.value
    })
    
    // 重新加载设置
    switch (activeTab.value) {
      case 'general':
        await loadGeneralSettings()
        break
      case 'security':
        await loadSecuritySettings()
        break
      case 'notification':
        await loadNotificationSettings()
        break
      case 'performance':
        await loadPerformanceSettings()
        break
    }
    
    ElMessage.success('设置已恢复默认值')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('恢复默认设置失败:', error)
      ElMessage.error('恢复默认设置失败')
    }
  }
}

// 生命周期
onMounted(() => {
  loadGeneralSettings()
  loadSecuritySettings()
  loadNotificationSettings()
  loadPerformanceSettings()
})
</script>

<style scoped>
.settings-container {
  padding: 24px;
  height: 100%;
  display: flex;
  flex-direction: column;
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

/* 设置内容区域 */
.settings-content {
  flex: 1;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.settings-tabs {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.settings-tabs :deep(.el-tabs__content) {
  flex: 1;
  overflow-y: auto;
  padding: 0;
}

.settings-tabs :deep(.el-tabs__header) {
  margin: 0;
  padding: 0 24px;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.settings-tabs :deep(.el-tabs__nav-wrap) {
  padding: 0;
}

.settings-tabs :deep(.el-tabs__item) {
  padding: 16px 24px;
  font-weight: 500;
  color: #666;
}

.settings-tabs :deep(.el-tabs__item.is-active) {
  color: #409eff;
  font-weight: 600;
}

/* 表单样式 */
.settings-form {
  padding: 24px;
}

.form-section {
  margin-bottom: 32px;
}

.form-section-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 24px 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #e9ecef;
}

.form-row {
  display: flex;
  gap: 24px;
  margin-bottom: 20px;
  align-items: flex-end;
}

.form-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-item.half-width {
  flex: 0 0 calc(50% - 12px);
}

.form-label {
  font-size: 14px;
  font-weight: 500;
  color: #606266;
  margin-bottom: 4px;
}

.form-input {
  width: 100%;
}

/* 复选框组样式 */
.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.checkbox-row {
  display: flex;
  gap: 32px;
  align-items: center;
}

.checkbox-item {
  font-size: 14px;
  color: #666;
  background: #f5f5f5;
  padding: 4px 8px;
  border-radius: 4px;
  font-family: monospace;
}

.label-text {
  font-size: 14px;
  color: #606266;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .settings-container {
    padding: 16px;
  }
  
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .form-row {
    flex-direction: column;
    gap: 16px;
  }
  
  .form-item.half-width {
    flex: 1;
  }
  
  .checkbox-row {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .settings-tabs :deep(.el-tabs__header) {
    padding: 0 16px;
  }
  
  .settings-form {
    padding: 16px;
  }
}
</style>