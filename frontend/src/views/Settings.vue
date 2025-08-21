<template>
  <div class="settings">
    <div class="page-header">
      <h1 class="page-title">系统设置</h1>
      <p class="page-description">管理系统配置和个性化设置</p>
    </div>

    <!-- 设置选项卡 -->
    <el-tabs v-model="activeTab" class="settings-tabs">
      <!-- 基本设置 -->
      <el-tab-pane label="基本设置" name="basic">
        <el-card class="setting-card">
          <template #header>
            <div class="card-header">
              <span>系统信息</span>
            </div>
          </template>
          
          <el-form :model="basicSettings" label-width="120px">
            <el-form-item label="系统名称">
              <el-input v-model="basicSettings.systemName" placeholder="请输入系统名称" />
            </el-form-item>
            
            <el-form-item label="系统版本">
              <el-input v-model="basicSettings.version" disabled />
            </el-form-item>
            
            <el-form-item label="管理员邮箱">
              <el-input v-model="basicSettings.adminEmail" placeholder="请输入管理员邮箱" />
            </el-form-item>
            
            <el-form-item label="系统描述">
              <el-input
                v-model="basicSettings.description"
                type="textarea"
                :rows="3"
                placeholder="请输入系统描述"
              />
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <!-- 安全设置 -->
      <el-tab-pane label="安全设置" name="security">
        <el-card class="setting-card">
          <template #header>
            <div class="card-header">
              <span>安全配置</span>
            </div>
          </template>
          
          <el-form :model="securitySettings" label-width="120px">
            <el-form-item label="密码策略">
              <el-checkbox-group v-model="securitySettings.passwordPolicy">
                <el-checkbox label="uppercase">必须包含大写字母</el-checkbox>
                <el-checkbox label="lowercase">必须包含小写字母</el-checkbox>
                <el-checkbox label="numbers">必须包含数字</el-checkbox>
                <el-checkbox label="symbols">必须包含特殊字符</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
            
            <el-form-item label="最小密码长度">
              <el-input-number
                v-model="securitySettings.minPasswordLength"
                :min="6"
                :max="20"
                controls-position="right"
              />
            </el-form-item>
            
            <el-form-item label="登录失败锁定">
              <el-switch
                v-model="securitySettings.loginLock"
                active-text="启用"
                inactive-text="禁用"
              />
            </el-form-item>
            
            <el-form-item label="锁定阈值" v-if="securitySettings.loginLock">
              <el-input-number
                v-model="securitySettings.lockThreshold"
                :min="3"
                :max="10"
                controls-position="right"
              />
              <span class="form-help">次失败后锁定账户</span>
            </el-form-item>
            
            <el-form-item label="会话超时">
              <el-input-number
                v-model="securitySettings.sessionTimeout"
                :min="15"
                :max="480"
                controls-position="right"
              />
              <span class="form-help">分钟</span>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <!-- 通知设置 -->
      <el-tab-pane label="通知设置" name="notification">
        <el-card class="setting-card">
          <template #header>
            <div class="card-header">
              <span>通知配置</span>
            </div>
          </template>
          
          <el-form :model="notificationSettings" label-width="120px">
            <el-form-item label="邮件通知">
              <el-switch
                v-model="notificationSettings.emailNotification"
                active-text="启用"
                inactive-text="禁用"
              />
            </el-form-item>
            
            <el-form-item label="SMTP服务器" v-if="notificationSettings.emailNotification">
              <el-input v-model="notificationSettings.smtpServer" placeholder="请输入SMTP服务器地址" />
            </el-form-item>
            
            <el-form-item label="SMTP端口" v-if="notificationSettings.emailNotification">
              <el-input-number
                v-model="notificationSettings.smtpPort"
                :min="1"
                :max="65535"
                controls-position="right"
              />
            </el-form-item>
            
            <el-form-item label="系统通知">
              <el-checkbox-group v-model="notificationSettings.systemNotifications">
                <el-checkbox label="user_register">用户注册</el-checkbox>
                <el-checkbox label="user_login">用户登录</el-checkbox>
                <el-checkbox label="system_error">系统错误</el-checkbox>
                <el-checkbox label="security_alert">安全警报</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <!-- 界面设置 -->
      <el-tab-pane label="界面设置" name="ui">
        <el-card class="setting-card">
          <template #header>
            <div class="card-header">
              <span>界面配置</span>
            </div>
          </template>
          
          <el-form :model="uiSettings" label-width="120px">
            <el-form-item label="主题模式">
              <el-radio-group v-model="uiSettings.theme">
                <el-radio value="light">浅色主题</el-radio>
                <el-radio value="dark">深色主题</el-radio>
                <el-radio value="auto">跟随系统</el-radio>
              </el-radio-group>
            </el-form-item>
            
            <el-form-item label="主色调">
              <el-color-picker v-model="uiSettings.primaryColor" />
            </el-form-item>
            
            <el-form-item label="侧边栏宽度">
              <el-slider
                v-model="uiSettings.sidebarWidth"
                :min="200"
                :max="300"
                :step="10"
                show-input
                show-input-controls
              />
            </el-form-item>
            
            <el-form-item label="表格密度">
              <el-radio-group v-model="uiSettings.tableDensity">
                <el-radio value="default">默认</el-radio>
                <el-radio value="compact">紧凑</el-radio>
                <el-radio value="comfortable">舒适</el-radio>
              </el-radio-group>
            </el-form-item>
            
            <el-form-item label="动画效果">
              <el-switch
                v-model="uiSettings.animations"
                active-text="启用"
                inactive-text="禁用"
              />
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <!-- 备份设置 -->
      <el-tab-pane label="备份设置" name="backup">
        <el-card class="setting-card">
          <template #header>
            <div class="card-header">
              <span>备份配置</span>
            </div>
          </template>
          
          <el-form :model="backupSettings" label-width="120px">
            <el-form-item label="自动备份">
              <el-switch
                v-model="backupSettings.autoBackup"
                active-text="启用"
                inactive-text="禁用"
              />
            </el-form-item>
            
            <el-form-item label="备份频率" v-if="backupSettings.autoBackup">
              <el-select v-model="backupSettings.backupFrequency" placeholder="请选择备份频率">
                <el-option label="每天" value="daily" />
                <el-option label="每周" value="weekly" />
                <el-option label="每月" value="monthly" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="保留备份数">
              <el-input-number
                v-model="backupSettings.retentionCount"
                :min="1"
                :max="100"
                controls-position="right"
              />
            </el-form-item>
            
            <el-form-item label="备份路径">
              <el-input v-model="backupSettings.backupPath" placeholder="请输入备份路径" />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="handleManualBackup">
                <el-icon><Download /></el-icon>
                立即备份
              </el-button>
              <el-button @click="handleRestoreBackup">
                <el-icon><Upload /></el-icon>
                恢复备份
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- 操作按钮 -->
    <div class="action-buttons">
      <el-button @click="resetSettings">重置设置</el-button>
      <el-button type="primary" @click="saveSettings">保存设置</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Download,
  Upload
} from '@element-plus/icons-vue'

// 响应式数据
const activeTab = ref('basic')

// 基本设置
const basicSettings = reactive({
  systemName: '后台管理系统',
  version: 'v1.0.0',
  adminEmail: 'admin@example.com',
  description: '这是一个功能完善的后台管理系统，提供用户管理、数据统计等功能。'
})

// 安全设置
const securitySettings = reactive({
  passwordPolicy: ['uppercase', 'lowercase', 'numbers'],
  minPasswordLength: 8,
  loginLock: true,
  lockThreshold: 5,
  sessionTimeout: 30
})

// 通知设置
const notificationSettings = reactive({
  emailNotification: false,
  smtpServer: 'smtp.example.com',
  smtpPort: 587,
  systemNotifications: ['user_register', 'system_error']
})

// 界面设置
const uiSettings = reactive({
  theme: 'light',
  primaryColor: '#409eff',
  sidebarWidth: 240,
  tableDensity: 'default',
  animations: true
})

// 备份设置
const backupSettings = reactive({
  autoBackup: true,
  backupFrequency: 'daily',
  retentionCount: 30,
  backupPath: '/backup'
})

// 方法
const saveSettings = async () => {
  try {
    // 这里可以调用API保存设置
    await new Promise(resolve => setTimeout(resolve, 1000)) // 模拟API调用
    
    ElMessage.success('设置保存成功')
  } catch (error) {
    ElMessage.error('设置保存失败')
  }
}

const resetSettings = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要重置所有设置吗？此操作不可撤销。',
      '确认重置',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 重置所有设置到默认值
    Object.assign(basicSettings, {
      systemName: '后台管理系统',
      version: 'v1.0.0',
      adminEmail: 'admin@example.com',
      description: '这是一个功能完善的后台管理系统，提供用户管理、数据统计等功能。'
    })
    
    Object.assign(securitySettings, {
      passwordPolicy: ['uppercase', 'lowercase', 'numbers'],
      minPasswordLength: 8,
      loginLock: true,
      lockThreshold: 5,
      sessionTimeout: 30
    })
    
    Object.assign(notificationSettings, {
      emailNotification: false,
      smtpServer: 'smtp.example.com',
      smtpPort: 587,
      systemNotifications: ['user_register', 'system_error']
    })
    
    Object.assign(uiSettings, {
      theme: 'light',
      primaryColor: '#409eff',
      sidebarWidth: 240,
      tableDensity: 'default',
      animations: true
    })
    
    Object.assign(backupSettings, {
      autoBackup: true,
      backupFrequency: 'daily',
      retentionCount: 30,
      backupPath: '/backup'
    })
    
    ElMessage.success('设置已重置')
  } catch {
    // 用户取消重置
  }
}

const handleManualBackup = () => {
  ElMessage.info('开始备份，请稍候...')
  // 这里可以调用备份API
}

const handleRestoreBackup = () => {
  ElMessage.info('恢复备份功能开发中...')
  // 这里可以调用恢复备份API
}
</script>

<style scoped>
.settings {
  padding: 0;
  height: 100%;
  min-height: 100%;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 8px 0;
}

.page-description {
  color: #666;
  margin: 0;
  font-size: 14px;
}

/* 设置选项卡 */
.settings-tabs {
  margin-bottom: 24px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.settings-tabs .el-tabs__content {
  flex: 1;
  overflow-y: auto;
}

.settings-tabs .el-tab-pane {
  height: 100%;
}

.setting-card {
  margin-bottom: 20px;
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.setting-card:last-child {
  margin-bottom: 0;
}

.card-header {
  font-weight: 600;
  color: var(--text-color);
}

/* 表单项样式 */
.form-help {
  margin-left: 8px;
  color: #999;
  font-size: 12px;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  justify-content: center;
  gap: 16px;
  padding: 24px 0;
  border-top: 1px solid #f0f0f0;
  background-color: #fff;
  margin-top: auto;
  flex-shrink: 0;
}

.dark-mode .action-buttons {
  background-color: var(--header-bg);
  border-top-color: var(--border-color);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-title {
    font-size: 24px;
  }
  
  .action-buttons {
    flex-direction: column;
    align-items: center;
    padding: 20px 0;
  }
  
  .el-form-item {
    margin-bottom: 20px;
  }
  
  .settings-tabs .el-tabs__content {
    padding: 0 16px;
  }
}
</style>
