<template>
  <div class="robot-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">机器人管理</h1>
      </div>
      <div class="header-right">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索机器人..."
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
      <div class="filter-item">
        <label class="filter-label">机器人类型</label>
        <el-select v-model="selectedType" placeholder="全部类型" clearable>
          <el-option label="全部类型" value="" />
          <el-option label="探索者" value="探索者" />
          <el-option label="守护者" value="守护者" />
          <el-option label="服务者" value="服务者" />
          <el-option label="运输者" value="运输者" />
        </el-select>
      </div>
      <div class="filter-item">
        <label class="filter-label">状态</label>
        <el-select v-model="selectedStatus" placeholder="全部状态" clearable>
          <el-option label="全部状态" value="" />
          <el-option label="在线" value="在线" />
          <el-option label="低电量" value="低电量" />
          <el-option label="异常" value="异常" />
        </el-select>
      </div>
      <div class="filter-item">
        <label class="filter-label">所在区域</label>
        <el-select v-model="selectedArea" placeholder="全部区域" clearable>
          <el-option label="全部区域" value="" />
          <el-option label="A区3楼" value="A区3楼" />
          <el-option label="B区1楼" value="B区1楼" />
          <el-option label="C区5楼" value="C区5楼" />
          <el-option label="D区2楼" value="D区2楼" />
        </el-select>
      </div>
    </div>

    <!-- 机器人列表表格 -->
    <div class="table-section">
      <el-table
        :data="filteredRobotList"
        class="robot-table"
        stripe
        @selection-change="handleSelectionChange"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="名称" width="200">
          <template #default="{ row }">
            <div class="robot-name-cell">
              <el-avatar :size="32" :src="row.avatar" class="robot-avatar" />
              <div>
                <div class="robot-name">{{ row.name }}</div>
                <div class="robot-version">{{ row.version }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="类型" width="100" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag
              :type="getStatusType(row.status)"
              size="small"
            >
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="location" label="位置" width="120" />
        <el-table-column label="电池" width="150">
          <template #default="{ row }">
            <div class="battery-cell">
              <el-progress
                :percentage="row.battery"
                :color="getBatteryColor(row.battery)"
                :stroke-width="8"
                class="battery-progress"
              />
              <span class="battery-text">{{ row.battery }}%</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="lastActivity" label="最后活动" width="120" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewDetails(row)">
              详情
            </el-button>
            <el-button type="primary" link size="small" @click="controlRobot(row)">
              控制
            </el-button>
            <el-button type="primary" link size="small" @click="configRobot(row)">
              配置
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 分页 -->
    <div class="pagination-section">
      <div class="pagination-info">
        显示 {{ (currentPage - 1) * pageSize + 1 }} 至 {{ Math.min(currentPage * pageSize, totalRobots) }} 条，共 {{ totalRobots }} 条
      </div>
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="totalRobots"
        :page-sizes="[10, 20, 50, 100]"
        layout="prev, pager, next"
        @current-change="handlePageChange"
      />
    </div>
    
    <!-- 机器人详情弹窗 -->
    <el-dialog
      v-model="detailsVisible"
      :title="`机器人详情 - ${currentRobot?.id || ''}`"
      width="600px"
      destroy-on-close
      class="robot-details-dialog"
    >
      <div v-if="currentRobot" class="robot-details">
        <div class="robot-header">
          <el-avatar :size="64" :src="currentRobot.avatar" class="robot-avatar-large" />
          <div class="robot-title">
            <h2>{{ currentRobot.name }}</h2>
            <div class="robot-subtitle">{{ currentRobot.version }}</div>
          </div>
          <el-button class="close-button" circle @click="detailsVisible = false">
            <el-icon><Close /></el-icon>
          </el-button>
        </div>
        
        <div class="details-content">
          <div class="basic-info">
            <h3>基本信息</h3>
            <div class="info-grid">
              <div class="info-item">
                <div class="info-label">类型:</div>
                <div class="info-value">{{ currentRobot.type }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">状态:</div>
                <div class="info-value">
                  <el-tag :type="getStatusType(currentRobot.status)" size="small">
                    {{ currentRobot.status }}
                  </el-tag>
                </div>
              </div>
              <div class="info-item">
                <div class="info-label">位置:</div>
                <div class="info-value">{{ currentRobot.location }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">最后活动:</div>
                <div class="info-value">{{ currentRobot.lastActivity }}</div>
              </div>
            </div>
          </div>
          
          <div class="status-monitor">
            <h3>状态监控</h3>
            <div class="monitor-item">
              <div class="monitor-header">
                <span>电池电量</span>
                <span class="monitor-value">{{ currentRobot.battery }}%</span>
              </div>
              <el-progress 
                :percentage="currentRobot.battery" 
                :color="getBatteryColor(currentRobot.battery)"
                :stroke-width="10"
              />
            </div>
            
            <div class="monitor-item">
              <div class="monitor-header">
                <span>CPU使用率</span>
                <span class="monitor-value">{{ currentRobot.cpuUsage }}%</span>
              </div>
              <el-progress 
                :percentage="currentRobot.cpuUsage" 
                :color="'#3b82f6'"
                :stroke-width="10"
              />
            </div>
            
            <div class="monitor-item">
              <div class="monitor-header">
                <span>内存使用</span>
                <span class="monitor-value">{{ currentRobot.memoryUsage }}%</span>
              </div>
              <el-progress 
                :percentage="currentRobot.memoryUsage" 
                :color="'#8b5cf6'"
                :stroke-width="10"
              />
            </div>
          </div>
        </div>
        
        <div class="dialog-footer">
          <el-button @click="detailsVisible = false">关闭</el-button>
        </div>
      </div>
    </el-dialog>
    
    <!-- 机器人配置弹窗 -->
    <el-dialog
      v-model="configVisible"
      :title="`配置机器人 - ${configRobotData?.id || ''}`"
      width="600px"
      destroy-on-close
      class="robot-config-dialog"
    >
      <div v-if="configRobotData" class="robot-config">
        <div class="config-section">
          <h3 class="section-title">基本配置</h3>
          
          <div class="config-item">
            <div class="config-label">机器人名称</div>
            <el-input v-model="configRobotData.name" placeholder="请输入机器人名称" />
          </div>
          
          <div class="config-item">
            <div class="config-label">默认速度</div>
            <el-select v-model="defaultSpeed" placeholder="请选择默认速度" class="full-width">
              <el-option label="低速" value="low" />
              <el-option label="中速" value="medium" />
              <el-option label="高速" value="high" />
            </el-select>
          </div>
          
          <div class="config-item">
            <div class="config-label">安全模式</div>
            <el-checkbox v-model="collisionDetection">启用碰撞检测</el-checkbox>
          </div>
        </div>
        
        <div class="config-section">
          <h3 class="section-title">网络配置</h3>
          
          <div class="config-item">
            <div class="config-label">IP地址</div>
            <el-input v-model="ipAddress" placeholder="请输入IP地址" />
          </div>
          
          <div class="config-item">
            <div class="config-label">连接方式</div>
            <el-select v-model="connectionType" placeholder="请选择连接方式" class="full-width">
              <el-option label="WiFi" value="wifi" />
              <el-option label="以太网" value="ethernet" />
              <el-option label="蓝牙" value="bluetooth" />
            </el-select>
          </div>
        </div>
        
        <div class="dialog-footer">
          <el-button @click="configVisible = false">取消</el-button>
          <el-button type="primary" @click="saveConfig">保存配置</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Search, Close, ArrowDown } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// 响应式数据
const searchKeyword = ref('')
const selectedType = ref('')
const selectedStatus = ref('')
const selectedArea = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const totalRobots = ref(24)
const selectedRobots = ref([])

// 详情弹窗相关
const detailsVisible = ref(false)
const currentRobot = ref(null)

// 配置弹窗相关
const configVisible = ref(false)
const configRobotData = ref(null)
const defaultSpeed = ref('medium')
const collisionDetection = ref(false)
const ipAddress = ref('')
const connectionType = ref('wifi')

// 机器人列表数据
const robotList = ref([
  {
    id: 'RX-001',
    name: '探索者-X1',
    version: 'V2.3.1',
    type: '探索者',
    status: '在线',
    location: 'A区3楼',
    battery: 85,
    cpuUsage: 45,
    memoryUsage: 68,
    lastActivity: '2分钟前',
    avatar: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHZpZXdCb3g9IjAgMCAzMiAzMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMTYiIGN5PSIxNiIgcj0iMTYiIGZpbGw9IiMxMGI5ODEiLz4KPHN2ZyB4PSI4IiB5PSI4IiB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0id2hpdGUiPgo8cGF0aCBkPSJNMTIgMkM2LjQ4IDIgMiA2LjQ4IDIgMTJzNC40OCAxMCAxMCAxMCAxMC00LjQ4IDEwLTEwUzE3LjUyIDIgMTIgMnptLTIgMTVsLTUtNSAxLjQxLTEuNDFMMTAgMTQuMTdsNy41OS03LjU5TDE5IDhsLTkgOXoiLz4KPC9zdmc+Cjwvc3ZnPgo='
  },
  {
    id: 'GZ-002',
    name: '守护者-Z2',
    version: 'V1.8.4',
    type: '守护者',
    status: '在线',
    location: 'B区1楼',
    battery: 65,
    cpuUsage: 32,
    memoryUsage: 54,
    lastActivity: '5分钟前',
    avatar: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHZpZXdCb3g9IjAgMCAzMiAzMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMTYiIGN5PSIxNiIgcj0iMTYiIGZpbGw9IiMzYjgyZjYiLz4KPHN2ZyB4PSI4IiB5PSI4IiB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0id2hpdGUiPgo8cGF0aCBkPSJNMTIgMkM2LjQ4IDIgMiA2LjQ4IDIgMTJzNC40OCAxMCAxMCAxMCAxMC00LjQ4IDEwLTEwUzE3LjUyIDIgMTIgMnptLTIgMTVsLTUtNSAxLjQxLTEuNDFMMTAgMTQuMTdsNy41OS03LjU5TDE5IDhsLTkgOXoiLz4KPC9zdmc+Cjwvc3ZnPgo='
  },
  {
    id: 'FW-003',
    name: '服务者-S3',
    version: 'V3.1.2',
    type: '服务者',
    status: '低电量',
    location: 'C区5楼',
    battery: 18,
    cpuUsage: 76,
    memoryUsage: 82,
    lastActivity: '12分钟前',
    avatar: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHZpZXdCb3g9IjAgMCAzMiAzMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMTYiIGN5PSIxNiIgcj0iMTYiIGZpbGw9IiNmNTllMGIiLz4KPHN2ZyB4PSI4IiB5PSI4IiB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0id2hpdGUiPgo8cGF0aCBkPSJNMTIgMkM2LjQ4IDIgMiA2LjQ4IDIgMTJzNC40OCAxMCAxMCAxMCAxMC00LjQ4IDEwLTEwUzE3LjUyIDIgMTIgMnptLTIgMTVsLTUtNSAxLjQxLTEuNDFMMTAgMTQuMTdsNy41OS03LjU5TDE5IDhsLTkgOXoiLz4KPC9zdmc+Cjwvc3ZnPgo='
  },
  {
    id: 'YS-004',
    name: '运输者-T5',
    version: 'V2.1.0',
    type: '运输者',
    status: '异常',
    location: 'D区2楼',
    battery: 45,
    cpuUsage: 92,
    memoryUsage: 63,
    lastActivity: '1小时前',
    avatar: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHZpZXdCb3g9IjAgMCAzMiAzMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMTYiIGN5PSIxNiIgcj0iMTYiIGZpbGw9IiNlZjQ0NDQiLz4KPHN2ZyB4PSI4IiB5PSI4IiB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0id2hpdGUiPgo8cGF0aCBkPSJNMTIgMkM2LjQ4IDIgMiA2LjQ4IDIgMTJzNC40OCAxMCAxMCAxMCAxMC00LjQ4IDEwLTEwUzE3LjUyIDIgMTIgMnptLTIgMTVsLTUtNSAxLjQxLTEuNDFMMTAgMTQuMTdsNy41OS03LjU5TDE5IDhsLTkgOXoiLz4KPC9zdmc+Cjwvc3ZnPgo='
  }
])

// 计算属性 - 过滤后的机器人列表
const filteredRobotList = computed(() => {
  let filtered = robotList.value

  // 搜索过滤
  if (searchKeyword.value) {
    filtered = filtered.filter(robot => 
      robot.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
      robot.id.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }

  // 类型过滤
  if (selectedType.value) {
    filtered = filtered.filter(robot => robot.type === selectedType.value)
  }

  // 状态过滤
  if (selectedStatus.value) {
    filtered = filtered.filter(robot => robot.status === selectedStatus.value)
  }

  // 区域过滤
  if (selectedArea.value) {
    filtered = filtered.filter(robot => robot.location === selectedArea.value)
  }

  return filtered
})

// 方法
const getStatusType = (status) => {
  switch (status) {
    case '在线': return 'success'
    case '低电量': return 'warning'
    case '异常': return 'danger'
    default: return 'info'
  }
}

const getBatteryColor = (percentage) => {
  if (percentage > 60) return '#10b981'
  if (percentage > 30) return '#f59e0b'
  return '#ef4444'
}

const handleSelectionChange = (selection) => {
  selectedRobots.value = selection
}

const handlePageChange = (page) => {
  currentPage.value = page
}

const viewDetails = (robot) => {
  currentRobot.value = robot
  detailsVisible.value = true
}

const controlRobot = (robot) => {
  console.log('控制机器人:', robot)
}

const configRobot = (robot) => {
  configRobotData.value = robot
  
  // 初始化配置数据
  defaultSpeed.value = 'medium' // 默认中速
  collisionDetection.value = false // 默认不启用碰撞检测
  ipAddress.value = '192.168.1.100' // 默认IP地址
  connectionType.value = 'wifi' // 默认WiFi连接
  
  configVisible.value = true
}

const saveConfig = () => {
  // 这里可以添加保存配置的逻辑，例如发送API请求
  console.log('保存配置:', {
    robot: configRobotData.value,
    defaultSpeed: defaultSpeed.value,
    collisionDetection: collisionDetection.value,
    ipAddress: ipAddress.value,
    connectionType: connectionType.value
  })
  
  // 显示保存成功提示
  ElMessage({
    message: '配置已保存',
    type: 'success'
  })
  
  // 关闭弹窗
  configVisible.value = false
}

onMounted(() => {
  // 页面加载时的初始化逻辑
})
</script>

<style scoped>
.robot-management {
}

/* 机器人详情弹窗 */
.robot-details {
  padding: 0;
}

.robot-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  position: relative;
}

.robot-avatar-large {
  border: 2px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.robot-title h2 {
  margin: 0 0 4px 0;
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
}

.robot-subtitle {
  font-size: 14px;
  color: #6b7280;
}

.close-button {
  position: absolute;
  top: 0;
  right: 0;
}

.details-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.basic-info h3,
.status-monitor h3 {
  font-size: 16px;
  font-weight: 600;
  color: #374151;
  margin: 0 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #e5e7eb;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.info-item {
  display: flex;
  align-items: center;
}

.info-label {
  font-size: 14px;
  font-weight: 500;
  color: #6b7280;
  width: 80px;
}

.info-value {
  font-size: 14px;
  color: #1f2937;
}

.monitor-item {
  margin-bottom: 16px;
}

.monitor-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
  color: #374151;
}

.monitor-value {
  font-weight: 600;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 24px;
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
  color: #1f2937;
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
  display: flex;
  gap: 24px;
  margin-bottom: 24px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-label {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.filter-item .el-select {
  width: 150px;
}

/* 表格区域 */
.table-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  margin-bottom: 24px;
}

.robot-table {
  width: 100%;
}

.robot-name-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.robot-avatar {
  flex-shrink: 0;
}

.robot-name {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 2px;
}

.robot-version {
  font-size: 12px;
  color: #9ca3af;
}

.battery-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.battery-progress {
  flex: 1;
  min-width: 80px;
}

.battery-text {
  font-size: 12px;
  color: #6b7280;
  min-width: 35px;
}

/* 分页区域 */
.pagination-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.pagination-info {
  font-size: 14px;
  color: #6b7280;
}

/* Element Plus 样式覆盖 */
:deep(.el-table) {
  border: none;
}

:deep(.el-table__header) {
  background-color: #f9fafb;
}

:deep(.el-table th) {
  background-color: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
  font-weight: 600;
  color: #374151;
}

:deep(.el-table td) {
  border-bottom: 1px solid #f3f4f6;
}

:deep(.el-table__row:hover) {
  background-color: #f9fafb;
}

:deep(.el-pagination) {
  justify-content: flex-end;
}

:deep(.el-pagination .el-pager li) {
  background-color: transparent;
  color: #6b7280;
  font-size: 14px;
}

:deep(.el-pagination .el-pager li.is-active) {
  background-color: #3b82f6;
  color: white;
}

:deep(.el-pagination .btn-prev),
:deep(.el-pagination .btn-next) {
  background-color: transparent;
  color: #6b7280;
}

:deep(.el-pagination .btn-prev:hover),
:deep(.el-pagination .btn-next:hover) {
  color: #3b82f6;
}

/* 弹窗样式覆盖 */
:deep(.robot-details-dialog .el-dialog__header),
:deep(.robot-config-dialog .el-dialog__header) {
  padding: 20px;
  margin-right: 0;
  border-bottom: 1px solid #e5e7eb;
}

:deep(.robot-details-dialog .el-dialog__title),
:deep(.robot-config-dialog .el-dialog__title) {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

:deep(.robot-details-dialog .el-dialog__body),
:deep(.robot-config-dialog .el-dialog__body) {
  padding: 24px;
}

:deep(.robot-details-dialog .el-dialog__headerbtn),
:deep(.robot-config-dialog .el-dialog__headerbtn) {
  display: none;
}

/* 配置弹窗样式 */
.robot-config {
  padding: 0;
}

.config-section {
  margin-bottom: 32px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #374151;
  margin: 0 0 20px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #e5e7eb;
}

.config-item {
  margin-bottom: 20px;
}

.config-label {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 8px;
}

.full-width {
  width: 100%;
}
</style>