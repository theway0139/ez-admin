<template>
  <div class="robot-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">{{ $t('robots.title') }}</h1>
      </div>
      <div class="header-right">
        <el-input
          v-model="searchKeyword"
          :placeholder="$t('common.search') + $t('robots.title') + '...'"
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
        <label class="filter-label">{{ $t('robots.robotType') }}</label>
        <el-select v-model="selectedType" :placeholder="$t('robots.allTypes')" clearable>
          <el-option :label="$t('robots.allTypes')" value="" />
          <el-option :label="$t('robots.explorer')" value="探索者" />
          <el-option :label="$t('robots.guardian')" value="守护者" />
          <el-option :label="$t('robots.service')" value="服务者" />
          <el-option :label="$t('robots.transport')" value="运输者" />
        </el-select>
      </div>
      <div class="filter-item">
        <label class="filter-label">{{ $t('common.status') }}</label>
        <el-select v-model="selectedStatus" :placeholder="$t('robots.allStatus')" clearable>
          <el-option :label="$t('robots.allStatus')" value="" />
          <el-option :label="$t('robots.online')" value="在线" />
          <el-option :label="$t('robots.lowBattery')" value="低电量" />
          <el-option :label="$t('robots.abnormal')" value="异常" />
        </el-select>
      </div>
      <div class="filter-item">
        <label class="filter-label">{{ $t('robots.location') }}</label>
        <el-select v-model="selectedArea" :placeholder="$t('robots.allAreas')" clearable>
          <el-option :label="$t('robots.allAreas')" value="" />
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
        <el-table-column prop="id" :label="$t('common.id')" width="80" />
        <el-table-column :label="$t('common.name')" width="200">
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
        <el-table-column prop="type" :label="$t('common.type')" width="100" />
        <el-table-column :label="$t('common.status')" width="100">
          <template #default="{ row }">
            <el-tag
              :type="getStatusType(row.status)"
              size="small"
            >
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="location" :label="$t('common.location')" width="120" />
        <el-table-column :label="$t('common.battery')" width="150">
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
        <el-table-column prop="lastActivity" :label="$t('robots.lastActivity')" width="120" />
        <el-table-column :label="$t('common.actions')" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewDetails(row)">
              {{ $t('common.details') }}
            </el-button>
            <el-button type="primary" link size="small" @click="controlRobot(row)">
              {{ $t('common.control') }}
            </el-button>
            <el-button type="primary" link size="small" @click="configRobot(row)">
              {{ $t('common.config') }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 分页 -->
    <div class="pagination-section">
      <div class="pagination-info">
        {{ $t('common.showing') }} {{ (currentPage - 1) * pageSize + 1 }} {{ $t('common.to') }} {{ Math.min(currentPage * pageSize, totalRobots) }} {{ $t('common.of') }} {{ totalRobots }} {{ $t('common.records') }}
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
      :title="$t('common.details') + ' - ' + (currentRobot?.id || '')"
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
            <h3>{{ $t('common.basicInfo') }}</h3>
            <div class="info-grid">
              <div class="info-item">
                <div class="info-label">{{ $t('common.type') }}:</div>
                <div class="info-value">{{ currentRobot.type }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ $t('common.status') }}:</div>
                <div class="info-value">
                  <el-tag :type="getStatusType(currentRobot.status)" size="small">
                    {{ currentRobot.status }}
                  </el-tag>
                </div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ $t('common.location') }}:</div>
                <div class="info-value">{{ currentRobot.location }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ $t('robots.lastActivity') }}:</div>
                <div class="info-value">{{ currentRobot.lastActivity }}</div>
              </div>
            </div>
          </div>
          
          <div class="status-monitor">
            <h3>{{ $t('common.statusMonitor') }}</h3>
            <div class="monitor-item">
              <div class="monitor-header">
                <span>{{ $t('common.battery') }}</span>
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
                <span>{{ $t('common.cpuUsage') }}</span>
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
                <span>{{ $t('common.memoryUsage') }}</span>
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
          <el-button @click="detailsVisible = false">{{ $t('common.close') }}</el-button>
        </div>
      </div>
    </el-dialog>
    
    <!-- 机器人配置弹窗 -->
    <el-dialog
      v-model="configVisible"
      :title="$t('common.config') + ' - ' + (configRobotData?.id || '')"
      width="600px"
      destroy-on-close
      class="robot-config-dialog"
    >
      <div v-if="configRobotData" class="robot-config">
        <div class="config-section">
          <h3 class="section-title">{{ $t('common.basicConfig') }}</h3>
          
          <div class="config-item">
            <div class="config-label">{{ $t('robots.robotName') }}</div>
            <el-input v-model="configRobotData.name" :placeholder="$t('robots.robotNamePlaceholder')" />
          </div>

          <div class="config-item">
            <div class="config-label">{{ $t('common.version') }}</div>
            <el-input v-model="configRobotData.version" :placeholder="$t('common.version')" />
          </div>

          <div class="config-item">
            <div class="config-label">{{ $t('robots.defaultSpeed') }}</div>
            <el-select v-model="defaultSpeed" :placeholder="$t('robots.selectDefaultSpeed')" class="full-width">
              <el-option :label="$t('robots.lowSpeed')" value="low" />
              <el-option :label="$t('robots.mediumSpeed')" value="medium" />
              <el-option :label="$t('robots.highSpeed')" value="high" />
            </el-select>
          </div>

          <div class="config-item">
            <div class="config-label">{{ $t('robots.safetyMode') }}</div>
            <el-checkbox v-model="collisionDetection">{{ $t('robots.enableCollisionDetection') }}</el-checkbox>
          </div>
        </div>
        
        <div class="config-section">
          <h3 class="section-title">{{ $t('common.networkConfig') }}</h3>
          
          <div class="config-item">
            <div class="config-label">{{ $t('robots.ipAddress') }}</div>
            <el-input v-model="ipAddress" :placeholder="$t('robots.ipAddressPlaceholder')" />
          </div>

          <div class="config-item">
            <div class="config-label">{{ $t('robots.connectionType') }}</div>
            <el-select v-model="connectionType" :placeholder="$t('robots.selectConnectionType')" class="full-width">
              <el-option :label="$t('robots.wifi')" value="wifi" />
              <el-option :label="$t('robots.ethernet')" value="ethernet" />
              <el-option :label="$t('robots.bluetooth')" value="bluetooth" />
            </el-select>
          </div>
          <div class="config-item">
            <div class="config-label">用户名</div>
            <el-input v-model="cameraUsername" placeholder="摄像机用户名（如 admin）" />
          </div>
          <div class="config-item">
            <div class="config-label">密码</div>
            <el-input v-model="cameraPassword" type="password" placeholder="摄像机密码" show-password />
          </div>
        </div>
        
        <div class="dialog-footer">
          <el-button @click="configVisible = false">{{ $t('common.cancel') }}</el-button>
          <el-button type="primary" @click="saveConfig">{{ $t('common.save') + $t('common.config') }}</el-button>
        </div>
      </div>
    </el-dialog>
    
    <!-- 机器人控制弹窗 -->
    <el-dialog
      v-model="controlVisible"
      :title="`控制机器人 - ${controlRobotData?.id || ''}`"
      width="900px"
      destroy-on-close
      class="robot-control-dialog"
    >
      <div v-if="controlRobotData" class="robot-control">
        <!-- 连接状态指示 -->
        <div class="connection-status">
          <el-tag 
            :type="connectionStatus === 'connected' ? 'success' : connectionStatus === 'connecting' ? 'warning' : 'danger'"
            size="small"
          >
            {{ connectionStatus === 'connected' ? '已连接' : connectionStatus === 'connecting' ? '连接中...' : '已断开' }}
          </el-tag>
        </div>
        
        <div class="control-content">
          <!-- 左侧视频区域 -->
          <div class="video-section">
            <div class="video-container">
              <video 
                ref="videoPlayer"
                class="video-player"
                controls
                muted
                autoplay
              >
                您的浏览器不支持视频播放
              </video>
              <div v-if="!streamUrl || connectionStatus !== 'connected'" class="video-placeholder">
                <el-icon size="48" color="#d1d5db"><VideoCamera /></el-icon>
                <div class="placeholder-text">
                  {{ connectionStatus === 'connecting' ? '正在连接摄像头...' : '未配置摄像机地址' }}
                </div>
              </div>
            </div>
          </div>
          
          <!-- 右侧控制区域 -->
          <div class="control-section">
            <!-- 运动控制 -->
            <div class="movement-control">
              <h4>运动控制</h4>
              <div class="direction-buttons">
                <!-- 上方向按钮 -->
                <div class="button-row">
                  <button 
                    class="direction-btn up-btn"
                    @mousedown="startMove('up')"
                    @mouseup="stopMove"
                    @mouseleave="stopMove"
                    :disabled="connectionStatus !== 'connected'"
                  >
                    <el-icon size="24"><ArrowUp /></el-icon>
                  </button>
                </div>
                
                <!-- 左右方向按钮 -->
                <div class="button-row">
                  <button 
                    class="direction-btn left-btn"
                    @mousedown="startMove('left')"
                    @mouseup="stopMove"
                    @mouseleave="stopMove"
                    :disabled="connectionStatus !== 'connected'"
                  >
                    <el-icon size="24"><ArrowLeft /></el-icon>
                  </button>
                  
                  <button 
                    class="direction-btn stop-btn"
                    @click="stopMove"
                    :disabled="connectionStatus !== 'connected'"
                  >
                    <el-icon size="20"><Close /></el-icon>
                  </button>
                  
                  <button 
                    class="direction-btn right-btn"
                    @mousedown="startMove('right')"
                    @mouseup="stopMove"
                    @mouseleave="stopMove"
                    :disabled="connectionStatus !== 'connected'"
                  >
                    <el-icon size="24"><ArrowRight /></el-icon>
                  </button>
                </div>
                
                <!-- 下方向按钮 -->
                <div class="button-row">
                  <button 
                    class="direction-btn down-btn"
                    @mousedown="startMove('down')"
                    @mouseup="stopMove"
                    @mouseleave="stopMove"
                    :disabled="connectionStatus !== 'connected'"
                  >
                    <el-icon size="24"><ArrowDown /></el-icon>
                  </button>
                </div>
              </div>
            </div>
            
            <!-- 速度调节 -->
            <div class="speed-control">
              <h4>速度调节</h4>
              <div class="speed-slider">
                <el-slider
                  v-model="controlSpeed"
                  :min="0"
                  :max="100"
                  :step="10"
                  show-stops
                  :disabled="connectionStatus !== 'connected'"
                />
                <div class="speed-value">{{ controlSpeed }}%</div>
              </div>
            </div>
            
            <!-- 功能控制 -->
            <div class="function-control">
              <h4>功能控制</h4>
              <div class="function-buttons">
                <button 
                  class="function-btn"
                  @click="takeSnapshot"
                  :disabled="connectionStatus !== 'connected'"
                >
                  <el-icon size="20"><Camera /></el-icon>
                  <span>拍照</span>
                </button>
                
                <button 
                  class="function-btn"
                  @click="toggleRecording"
                  :disabled="connectionStatus !== 'connected'"
                >
                  <el-icon size="20"><VideoCamera /></el-icon>
                  <span>录像</span>
                </button>
                
                <button 
                  class="function-btn"
                  @click="triggerAlarm"
                  :disabled="connectionStatus !== 'connected'"
                >
                  <el-icon size="20"><Bell /></el-icon>
                  <span>报警</span>
                </button>
                
                <button 
                  class="function-btn"
                  @click="toggleLight"
                  :disabled="connectionStatus !== 'connected'"
                >
                  <el-icon size="20"><Sunny /></el-icon>
                  <span>灯光</span>
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <div class="dialog-footer">
          <el-button @click="controlVisible = false">关闭</el-button>
          <el-button type="primary">保存设置</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { Search, Close, ArrowDown, ArrowUp, ArrowLeft, ArrowRight, VideoCamera, Camera, Bell, Sunny } from '@element-plus/icons-vue'
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
const ipAddress = ref('192.168.1.64')
const cameraUsername = ref('admin')
const cameraPassword = ref('okwy1234')
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api'
const connectionType = ref('wifi')

// 控制弹窗相关
const controlVisible = ref(false)
const controlRobotData = ref(null)
const streamUrl = ref('')
const streamType = ref('hls')
const controlSpeed = ref(50)
const isPressing = ref(false)
const pressTimer = ref(null)
const currentDirection = ref(null)
const connectionStatus = ref('disconnected') // connected, disconnected, connecting
const videoPlayer = ref(null)
const hlsInstance = ref(null)

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
  controlRobotData.value = robot
  controlVisible.value = true
  connectionStatus.value = 'connecting'
  streamType.value = 'hls'
  // 使用与 RTSPPlayer 一致的 HLS 地址，后续可根据机器人ID映射
  streamUrl.value = '/streams/cam1/index.m3u8'
  nextTick(() => {
    startStream()
  })
}

const configRobot = (robot) => {
  configRobotData.value = robot
  
  // 初始化配置数据
  defaultSpeed.value = 'medium' // 默认中速
  collisionDetection.value = false // 默认不启用碰撞检测
  ipAddress.value = '192.168.1.64' // 默认IP地址
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

// 控制相关方法
const startMove = (direction) => {
  if (isPressing.value) return
  isPressing.value = true
  currentDirection.value = direction
  sendMoveStart(direction)
}

const stopMove = () => {
  if (!isPressing.value) return
  isPressing.value = false
  if (pressTimer.value) {
    clearInterval(pressTimer.value)
    pressTimer.value = null
  }
  if (currentDirection.value) {
    sendMoveStop(currentDirection.value)
    currentDirection.value = null
  }
}

const sendMoveStart = async (direction) => {
  if (!['up','down','left','right'].includes(direction)) return
  if (!ipAddress.value) {
    ElMessage.error('请先在配置中填写摄像机 IP')
    return
  }
  const url = `${API_BASE}/ptz/move/start`
  const speedInt = Math.max(1, Math.min(7, Math.round(controlSpeed.value / 15)))
  const payload = {
    ip: ipAddress.value,
    username: cameraUsername.value || 'admin',
    password: cameraPassword.value || '',
    direction,
    channel: 1,
    speed: speedInt
  }
  try {
    const resp = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    const data = await resp.json().catch(() => ({}))
    if (!resp.ok || !data || !data.success) {
      ElMessage.error((data && data.error) || `开始 ${direction} 失败`)
    }
  } catch (e) {
    ElMessage.error(`网络错误：${e.message}`)
  }
}

const sendMoveStop = async (direction) => {
  if (!['up','down','left','right'].includes(direction)) return
  const url = `${API_BASE}/ptz/move/stop`
  const speedInt = Math.max(1, Math.min(7, Math.round(controlSpeed.value / 15)))
  const payload = {
    ip: ipAddress.value,
    username: cameraUsername.value || 'admin',
    password: cameraPassword.value || '',
    direction,
    channel: 1,
    speed: speedInt
  }
  try {
    const resp = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    const data = await resp.json().catch(() => ({}))
    if (!resp.ok || !data || !data.success) {
      ElMessage.error((data && data.error) || `停止 ${direction} 失败`)
    }
  } catch (e) {
    ElMessage.error(`网络错误：${e.message}`)
  }
}
const takeSnapshot = () => {
  console.log('拍照')
  ElMessage.success('拍照成功')
}

const toggleRecording = () => {
  console.log('录像')
  ElMessage.success('录像已开始')
}

const triggerAlarm = () => {
  console.log('报警')
  ElMessage.warning('报警已触发')
}

const toggleLight = () => {
  console.log('灯光')
  ElMessage.success('灯光已切换')
}

onMounted(() => {
  // 页面加载时的初始化逻辑
})

// 控制弹窗打开/关闭时启动或停止视频
watch(controlVisible, (visible) => {
  if (visible) {
    connectionStatus.value = 'connecting'
    nextTick(() => startStream())
  } else {
    stopStream()
  }
})

// 当流地址变化且弹窗已打开时，重新开始播放
watch(streamUrl, () => {
  if (controlVisible.value) {
    startStream()
  }
})

const startStream = async () => {
  try {
    if (!videoPlayer.value) return
    const url = streamUrl.value || '/streams/cam1/index.m3u8'
    videoPlayer.value.src = url
    try {
      await videoPlayer.value.play()
    } catch (_) {
      // 某些浏览器需要用户交互，失败也不抛错
    }
    connectionStatus.value = 'connected'
  } catch (error) {
    console.error('播放失败:', error)
    connectionStatus.value = 'error'
    ElMessage.error('视频播放失败，请检查网络连接或使用兼容浏览器')
  }
}

const stopStream = () => {
  try {
    if (videoPlayer.value) {
      videoPlayer.value.pause()
      videoPlayer.value.removeAttribute('src')
      videoPlayer.value.load()
    }
    connectionStatus.value = 'disconnected'
  } catch (e) {
    console.error('停止播放失败:', e)
  }
}

const refreshStream = () => {
  stopStream()
  setTimeout(() => startStream(), 500)
}

onUnmounted(() => {
  stopStream()
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

/* 机器人控制弹窗样式 */
.robot-control {
  padding: 0;
}

.connection-status {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 16px;
}

.control-content {
  display: flex;
  gap: 24px;
  min-height: 400px;
}

/* 左侧视频区域 */
.video-section {
  flex: 1;
  min-width: 400px;
}

.video-container {
  width: 100%;
  height: 300px;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.video-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
  text-align: center;
}

.placeholder-text {
  margin-top: 12px;
  font-size: 14px;
}

.video-player {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 右侧控制区域 */
.control-section {
  flex: 0 0 280px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.control-section h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: #374151;
}

/* 运动控制 */
.movement-control {
  background: #f9fafb;
  padding: 16px;
  border-radius: 8px;
}

.direction-buttons {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.button-row {
  display: flex;
  gap: 8px;
  align-items: center;
}

.direction-btn {
  width: 60px;
  height: 60px;
  border: none;
  border-radius: 12px;
  background: #3b82f6;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  user-select: none;
}

.direction-btn:hover:not(:disabled) {
  background: #2563eb;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.direction-btn:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.4);
}

.direction-btn:disabled {
  background: #d1d5db;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.stop-btn {
  width: 50px;
  height: 50px;
  background: #ef4444;
}

.stop-btn:hover:not(:disabled) {
  background: #dc2626;
}

/* 速度控制 */
.speed-control {
  background: #f9fafb;
  padding: 16px;
  border-radius: 8px;
}

.speed-slider {
  display: flex;
  align-items: center;
  gap: 12px;
}

.speed-slider .el-slider {
  flex: 1;
}

.speed-value {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  min-width: 40px;
  text-align: right;
}

/* 功能控制 */
.function-control {
  background: #f9fafb;
  padding: 16px;
  border-radius: 8px;
}

.function-buttons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.function-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 12px 8px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: white;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 12px;
}

.function-btn:hover:not(:disabled) {
  border-color: #3b82f6;
  color: #3b82f6;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.function-btn:disabled {
  background: #f3f4f6;
  color: #9ca3af;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 弹窗样式覆盖 */
:deep(.robot-control-dialog .el-dialog) {
  border-radius: 12px;
}

:deep(.robot-control-dialog .el-dialog__header) {
  padding: 20px 24px 16px;
  border-bottom: 1px solid #e5e7eb;
}

:deep(.robot-control-dialog .el-dialog__body) {
  padding: 24px;
}

:deep(.robot-control-dialog .el-dialog__title) {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

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

/* 响应式设计 */
@media (max-width: 768px) {
  .control-content {
    flex-direction: column;
    gap: 16px;
  }
  
  .video-section {
    min-width: auto;
  }
  
  .control-section {
    flex: none;
  }
  
  .video-container {
    height: 200px;
  }
  
  .direction-btn {
    width: 50px;
    height: 50px;
  }
  
  .stop-btn {
    width: 40px;
    height: 40px;
  }
}

</style>