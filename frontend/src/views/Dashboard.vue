<template>
  <div class="dashboard">
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">{{ $t('dashboard.title') }}</h1>
      </div>
      <div class="header-actions">
        <el-button type="default" size="default">
          <el-icon><Download /></el-icon>
          {{ $t('common.export') + $t('common.data') }}
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <el-card class="stat-card">
        <div class="stat-header">
          <div class="stat-left">
            <div class="stat-icon">
              <el-icon><Monitor /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">{{ $t('dashboard.onlineRobots') }}</div>
              <div class="stat-number">24</div>
              <div class="stat-trend positive">
                <el-icon><ArrowUp /></el-icon>
                12% {{ $t('dashboard.vsLastWeek') }}
              </div>
            </div>
          </div>
        </div>
        <div class="stat-chart">
          <svg class="mini-chart" viewBox="0 0 100 30">
            <path d="M5,25 Q15,20 25,15 T45,10 T65,8 T85,5 L95,3" stroke="#3b82f6" stroke-width="2" fill="none"/>
            <path d="M5,25 Q15,20 25,15 T45,10 T65,8 T85,5 L95,3 L95,30 L5,30 Z" fill="url(#blueGradient)" opacity="0.3"/>
            <defs>
              <linearGradient id="blueGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" style="stop-color:#3b82f6;stop-opacity:0.8" />
                <stop offset="100%" style="stop-color:#3b82f6;stop-opacity:0.1" />
              </linearGradient>
            </defs>
          </svg>
        </div>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-header">
          <div class="stat-left">
            <div class="stat-icon running-icon">
              <el-icon><Loading /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">{{ $t('dashboard.runningTasks') }}</div>
              <div class="stat-number">168</div>
              <div class="stat-trend negative">
                <el-icon><ArrowDown /></el-icon>
                3% {{ $t('dashboard.vsLastWeek') }}
              </div>
            </div>
          </div>
        </div>
        <div class="stat-chart">
          <svg class="mini-chart" viewBox="0 0 100 30">
            <path d="M5,15 Q15,12 25,18 T45,20 T65,22 T85,25 L95,27" stroke="#06b6d4" stroke-width="2" fill="none"/>
            <path d="M5,15 Q15,12 25,18 T45,20 T65,22 T85,25 L95,27 L95,30 L5,30 Z" fill="url(#cyanGradient)" opacity="0.3"/>
            <defs>
              <linearGradient id="cyanGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" style="stop-color:#06b6d4;stop-opacity:0.8" />
                <stop offset="100%" style="stop-color:#06b6d4;stop-opacity:0.1" />
              </linearGradient>
            </defs>
          </svg>
        </div>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-header">
          <div class="stat-left">
            <div class="stat-icon completed-icon">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">{{ $t('dashboard.completedTasks') }}</div>
              <div class="stat-number">2,876</div>
              <div class="stat-trend positive">
                <el-icon><ArrowUp /></el-icon>
                8% {{ $t('dashboard.vsLastWeek') }}
              </div>
            </div>
          </div>
        </div>
        <div class="stat-chart">
          <svg class="mini-chart" viewBox="0 0 100 30">
            <path d="M5,20 Q15,18 25,12 T45,8 T65,5 T85,3 L95,2" stroke="#10b981" stroke-width="2" fill="none"/>
            <path d="M5,20 Q15,18 25,12 T45,8 T65,5 T85,3 L95,2 L95,30 L5,30 Z" fill="url(#greenGradient)" opacity="0.3"/>
            <defs>
              <linearGradient id="greenGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" style="stop-color:#10b981;stop-opacity:0.8" />
                <stop offset="100%" style="stop-color:#10b981;stop-opacity:0.1" />
              </linearGradient>
            </defs>
          </svg>
        </div>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-header">
          <div class="stat-left">
            <div class="stat-icon alert-icon">
              <el-icon><Warning /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">{{ $t('dashboard.alerts') }}</div>
              <div class="stat-number">7</div>
              <div class="stat-trend positive">
                <el-icon><ArrowDown /></el-icon>
                15% {{ $t('dashboard.vsLastWeek') }}
              </div>
            </div>
          </div>
        </div>
        <div class="stat-chart">
          <svg class="mini-chart" viewBox="0 0 100 30">
            <path d="M5,8 Q15,12 25,15 T45,18 T65,22 T85,25 L95,27" stroke="#f59e0b" stroke-width="2" fill="none"/>
            <path d="M5,8 Q15,12 25,15 T45,18 T65,22 T85,25 L95,27 L95,30 L5,30 Z" fill="url(#orangeGradient)" opacity="0.3"/>
            <defs>
              <linearGradient id="orangeGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" style="stop-color:#f59e0b;stop-opacity:0.8" />
                <stop offset="100%" style="stop-color:#f59e0b;stop-opacity:0.1" />
              </linearGradient>
            </defs>
          </svg>
        </div>
      </el-card>
    </div>

    <!-- 图表区域 -->
    <div class="charts-section">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>{{ $t('dashboard.robotTypeDistribution') }}</span>
                <el-button type="text" size="small">
                  <el-icon><MoreFilled /></el-icon>
                </el-button>
              </div>
            </template>
            <div class="pie-chart-container">
              <div class="pie-chart">
                <svg viewBox="0 0 200 200" class="pie-svg">
                  <!-- 探索者 (8) - 蓝色 -->
                  <circle cx="100" cy="100" r="80" fill="none" stroke="#3b82f6" stroke-width="20" 
                    stroke-dasharray="125.66 314.16" stroke-dashoffset="0" transform="rotate(-90 100 100)"/>
                  <!-- 守护者 (6) - 橙色 -->
                  <circle cx="100" cy="100" r="80" fill="none" stroke="#f97316" stroke-width="20" 
                    stroke-dasharray="94.25 314.16" stroke-dashoffset="-125.66" transform="rotate(-90 100 100)"/>
                  <!-- 服务者 (5) - 绿色 -->
                  <circle cx="100" cy="100" r="80" fill="none" stroke="#10b981" stroke-width="20" 
                    stroke-dasharray="78.54 314.16" stroke-dashoffset="-219.91" transform="rotate(-90 100 100)"/>
                  <!-- 运输者 (5) - 青色 -->
                  <circle cx="100" cy="100" r="80" fill="none" stroke="#06b6d4" stroke-width="20" 
                    stroke-dasharray="78.54 314.16" stroke-dashoffset="-298.45" transform="rotate(-90 100 100)"/>
                </svg>
              </div>
              <div class="pie-legend">
                <div class="legend-item">
                  <span class="legend-color" style="background-color: #3b82f6;"></span>
                  <span class="legend-text">探索者 (8)</span>
                </div>
                <div class="legend-item">
                  <span class="legend-color" style="background-color: #f97316;"></span>
                  <span class="legend-text">守护者 (6)</span>
                </div>
                <div class="legend-item">
                  <span class="legend-color" style="background-color: #10b981;"></span>
                  <span class="legend-text">服务者 (5)</span>
                </div>
                <div class="legend-item">
                  <span class="legend-color" style="background-color: #06b6d4;"></span>
                  <span class="legend-text">运输者 (5)</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>{{ $t('dashboard.taskCompletion') }}</span>
                <div class="time-tabs">
                  <el-button type="text" size="small" :class="{ active: activeTab === 'week' }" @click="activeTab = 'week'">{{ $t('dashboard.week') }}</el-button>
                  <el-button type="text" size="small" :class="{ active: activeTab === 'month' }" @click="activeTab = 'month'">{{ $t('dashboard.month') }}</el-button>
                  <el-button type="text" size="small" :class="{ active: activeTab === 'year' }" @click="activeTab = 'year'">{{ $t('dashboard.year') }}</el-button>
                </div>
              </div>
            </template>
            <div class="bar-chart-container">
              <div class="bar-chart">
                <div class="chart-bars">
                  <div class="bar-group" v-for="(day, index) in weekData" :key="index">
                    <div class="bar-stack">
                      <div class="bar completed" :style="{ height: day.completed + '%' }"></div>
                      <div class="bar running" :style="{ height: day.running + '%' }"></div>
                      <div class="bar failed" :style="{ height: day.failed + '%' }"></div>
                    </div>
                    <div class="bar-label">{{ day.label }}</div>
                  </div>
                </div>
              </div>
              <div class="bar-legend">
                <div class="legend-item">
                  <span class="legend-color" style="background-color: #10b981;"></span>
                  <span class="legend-text">{{ $t('common.completed') }}</span>
                 </div>
                 <div class="legend-item">
                   <span class="legend-color" style="background-color: #3b82f6;"></span>
                   <span class="legend-text">{{ $t('common.running') }}</span>
                 </div>
                 <div class="legend-item">
                   <span class="legend-color" style="background-color: #ef4444;"></span>
                   <span class="legend-text">{{ $t('common.failed') }}</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 地图区域 -->
    <div class="map-section">
      <el-card class="map-card">
        <template #header>
          <div class="card-header">
            <span>{{ $t('dashboard.robotDistribution') }}</span>
            <el-button type="text" size="small">
              <el-icon><FullScreen /></el-icon>
            </el-button>
          </div>
        </template>
        <div class="map-container">
          <div class="map-wrapper">
            <!-- 地图控制按钮 -->
            <div class="map-controls">
              <div class="zoom-controls">
                <button class="zoom-btn">+</button>
                <button class="zoom-btn">-</button>
              </div>
            </div>
            
            <!-- 地图内容 -->
            <div class="map-content">
              <!-- 模拟地图背景 -->
              <div class="map-background"></div>
              
              <!-- 机器人标记点 -->
              <div class="robot-marker" style="top: 20%; left: 15%;">
                <div class="marker-icon green">R</div>
              </div>
              <div class="robot-marker" style="top: 35%; left: 45%;">
                <div class="marker-icon blue">R</div>
              </div>
              <div class="robot-marker" style="top: 60%; left: 25%;">
                <div class="marker-icon red">R</div>
              </div>
              <div class="robot-marker" style="top: 45%; left: 70%;">
                <div class="marker-icon green">R</div>
              </div>
              <div class="robot-marker" style="top: 75%; left: 60%;">
                <div class="marker-icon red">R</div>
              </div>
              <div class="robot-marker" style="top: 25%; left: 80%;">
                <div class="marker-icon blue">R</div>
              </div>
            </div>
            
            <!-- 地图底部信息 -->
            <div class="map-footer">
              <div class="map-attribution">
                <span>© Leaflet | © OpenStreetMap contributors</span>
              </div>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 在线机器人列表 -->
    <div class="robot-list-section">
      <el-card class="robot-list-card">
        <template #header>
          <div class="card-header">
            <span>{{ $t('dashboard.onlineRobots') }}</span>
          </div>
        </template>
        <div class="robot-table-container">
          <el-table :data="robotList" style="width: 100%" stripe>
            <el-table-column prop="id" :label="$t('common.id')" width="80" />
            <el-table-column :label="$t('common.name')" width="120">
              <template #default="scope">
                <div class="robot-name-cell">
                  <el-avatar :size="32" :src="scope.row.avatar" class="robot-avatar" />
                  <span class="robot-name">{{ scope.row.name }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="type" :label="$t('common.type')" width="100" />
            <el-table-column :label="$t('common.status')" width="80">
              <template #default="scope">
                <el-tag :type="scope.row.status === '在线' ? 'success' : 'danger'" size="small">
                  {{ scope.row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="location" :label="$t('common.location')" width="100" />
            <el-table-column :label="$t('common.battery')" width="120">
              <template #default="scope">
                <div class="battery-cell">
                  <el-progress 
                    :percentage="scope.row.battery" 
                    :stroke-width="8" 
                    :color="getBatteryColor(scope.row.battery)"
                    :show-text="false"
                    class="battery-progress"
                  />
                  <span class="battery-text">{{ scope.row.battery }}%</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column :label="$t('common.actions')" width="120">
              <template #default="scope">
                <el-button type="primary" link size="small">{{ $t('common.details') }}</el-button>
                <el-button type="primary" link size="small">{{ $t('common.control') }}</el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <!-- 分页 -->
          <div class="pagination-container">
            <div class="pagination-info">
              {{ $t('common.showing') }} 1 {{ $t('common.to') }} 2 {{ $t('common.of') }} 12 {{ $t('common.records') }}
            </div>
            <el-pagination
              v-model:current-page="currentPage"
              :page-size="pageSize"
              :total="totalRobots"
              layout="prev, pager, next"
              small
              @current-change="handlePageChange"
            />
          </div>
        </div>
      </el-card>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import {
  Monitor,
  Loading,
  CircleCheck,
  Warning,
  ArrowUp,
  ArrowDown,
  Download,
  MoreFilled,
  FullScreen
} from '@element-plus/icons-vue'

// 响应式数据
const activeTab = ref('week')
const currentPage = ref(1)
const pageSize = ref(10)
const totalRobots = ref(12)

// 周数据
const weekData = ref([
  { label: '周一', completed: 60, running: 20, failed: 5 },
  { label: '周二', completed: 70, running: 25, failed: 3 },
  { label: '周三', completed: 80, running: 15, failed: 4 },
  { label: '周四', completed: 75, running: 20, failed: 2 },
  { label: '周五', completed: 90, running: 12, failed: 3 },
  { label: '周六', completed: 55, running: 8, failed: 2 },
  { label: '周日', completed: 45, running: 6, failed: 1 }
])

// 机器人列表数据
const robotList = ref([
  {
    id: 'RX-001',
    name: '探索者-X1',
    type: '探索者',
    status: '在线',
    location: 'A区3楼',
    battery: 85,
    avatar: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHZpZXdCb3g9IjAgMCAzMiAzMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMTYiIGN5PSIxNiIgcj0iMTYiIGZpbGw9IiMxMGI5ODEiLz4KPHN2ZyB4PSI4IiB5PSI4IiB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0id2hpdGUiPgo8cGF0aCBkPSJNMTIgMkM2LjQ4IDIgMiA2LjQ4IDIgMTJzNC40OCAxMCAxMCAxMCAxMC00LjQ4IDEwLTEwUzE3LjUyIDIgMTIgMnptLTIgMTVsLTUtNSAxLjQxLTEuNDFMMTAgMTQuMTdsNy41OS03LjU5TDE5IDhsLTkgOXoiLz4KPC9zdmc+Cjwvc3ZnPgo='
  },
  {
    id: 'GZ-002',
    name: '守护者-Z2',
    type: '守护者',
    status: '在线',
    location: 'B区1楼',
    battery: 65,
    avatar: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHZpZXdCb3g9IjAgMCAzMiAzMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMTYiIGN5PSIxNiIgcj0iMTYiIGZpbGw9IiMzYjgyZjYiLz4KPHN2ZyB4PSI4IiB5PSI4IiB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0id2hpdGUiPgo8cGF0aCBkPSJNMTIgMkM2LjQ4IDIgMiA2LjQ4IDIgMTJzNC40OCAxMCAxMCAxMCAxMC00LjQ4IDEwLTEwUzE3LjUyIDIgMTIgMnptLTIgMTVsLTUtNSAxLjQxLTEuNDFMMTAgMTQuMTdsNy41OS03LjU5TDE5IDhsLTkgOXoiLz4KPC9zdmc+Cjwvc3ZnPgo='
  }
])

// 方法
const getBatteryColor = (percentage: number) => {
  if (percentage > 60) return '#10b981'
  if (percentage > 30) return '#f59e0b'
  return '#ef4444'
}

const handlePageChange = (page: number) => {
  currentPage.value = page
  // 这里可以添加获取数据的逻辑
}
</script>

<style scoped>
.dashboard {
  padding: 0;
  height: 100%;
  min-height: 100%;
}

.page-header {
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.header-actions .el-button {
  border: 1px solid #d1d5db;
  background: white;
  color: #374151;
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  border: none;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  background: white;
  padding: 0;
}

.stat-card :deep(.el-card__body) {
  padding: 20px;
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.stat-left {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: #3b82f6;
  background-color: #eff6ff;
  flex-shrink: 0;
}

.running-icon {
  color: #f97316;
  background-color: #fff7ed;
}

.completed-icon {
  color: #10b981;
  background-color: #f0fdf4;
}

.alert-icon {
  color: #f59e0b;
  background-color: #fffbeb;
}

.stat-info {
  flex: 1;
  min-width: 0;
}

.stat-label {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 4px;
}

.stat-number {
  font-size: 32px;
  font-weight: 700;
  color: #111827;
  line-height: 1;
  margin-bottom: 8px;
}

.stat-trend {
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.stat-trend.positive {
  color: #10b981;
}

.stat-trend.negative {
  color: #ef4444;
}

.stat-trend .el-icon {
  font-size: 12px;
}

.stat-chart {
  height: 60px;
  margin-top: 8px;
}

.mini-chart {
  width: 100%;
  height: 100%;
}

/* 图表区域 */
.charts-section {
  margin-bottom: 24px;
}

.chart-card {
  border: none;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  background: white;
  height: 400px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #111827;
}

.time-tabs {
  display: flex;
  gap: 8px;
}

.time-tabs .el-button {
  padding: 4px 12px;
  font-size: 12px;
  border: none;
  background: transparent;
  color: #6b7280;
}

.time-tabs .el-button.active {
  background: #3b82f6;
  color: white;
  border-radius: 4px;
}

/* 饼图样式 */
.pie-chart-container {
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 40px;
  height: 320px;
}

.pie-chart {
  width: 200px;
  height: 200px;
  flex-shrink: 0;
}

.pie-svg {
  width: 100%;
  height: 100%;
}

.pie-legend {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
  flex-shrink: 0;
}

.legend-text {
  font-size: 14px;
  color: #374151;
}

/* 柱状图样式 */
.bar-chart-container {
  padding: 20px;
  height: 320px;
  display: flex;
  flex-direction: column;
}

.bar-chart {
  flex: 1;
  display: flex;
  align-items: end;
  padding-bottom: 40px;
}

.chart-bars {
  display: flex;
  align-items: end;
  gap: 12px;
  width: 100%;
  height: 200px;
}

.bar-group {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
}

.bar-stack {
  display: flex;
  flex-direction: column-reverse;
  width: 24px;
  height: 160px;
  position: relative;
}

.bar {
  width: 100%;
  border-radius: 2px 2px 0 0;
  transition: all 0.3s ease;
}

.bar.completed {
  background-color: #10b981;
}

.bar.running {
  background-color: #3b82f6;
}

.bar.failed {
  background-color: #ef4444;
}

.bar-label {
  font-size: 12px;
  color: #6b7280;
  margin-top: 8px;
  text-align: center;
}

.bar-legend {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-top: 20px;
}

/* 地图区域 */
.map-section {
  margin-bottom: 24px;
}

.map-card {
  border: none;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  background: white;
}

.map-container {
  height: 380px;
  position: relative;
}

.map-wrapper {
  width: 100%;
  height: 100%;
  position: relative;
  overflow: hidden;
  border-radius: 8px;
}

.map-content {
  width: 100%;
  height: 100%;
  position: relative;
  background: #f8f9fa;
}

.map-background {
  width: 100%;
  height: 100%;
  background-image: 
    linear-gradient(45deg, #e9ecef 25%, transparent 25%), 
    linear-gradient(-45deg, #e9ecef 25%, transparent 25%), 
    linear-gradient(45deg, transparent 75%, #e9ecef 75%), 
    linear-gradient(-45deg, transparent 75%, #e9ecef 75%);
  background-size: 20px 20px;
  background-position: 0 0, 0 10px, 10px -10px, -10px 0px;
  opacity: 0.3;
}

.map-controls {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 10;
}

.zoom-controls {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.zoom-btn {
  width: 30px;
  height: 30px;
  background: white;
  border: 1px solid #ccc;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
}

.zoom-btn:hover {
  background: #f5f5f5;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}

.robot-marker {
  position: absolute;
  transform: translate(-50%, -50%);
  z-index: 5;
}

.marker-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
  color: white;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
  cursor: pointer;
  transition: all 0.2s ease;
}

.marker-icon:hover {
  transform: scale(1.2);
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.3);
}

.marker-icon.green {
  background-color: #10b981;
}

.marker-icon.blue {
  background-color: #3b82f6;
}

.marker-icon.red {
  background-color: #ef4444;
}

.map-footer {
  position: absolute;
  bottom: 5px;
  right: 10px;
  z-index: 10;
}

.map-attribution {
  font-size: 11px;
  color: #666;
  background: rgba(255, 255, 255, 0.8);
  padding: 2px 6px;
  border-radius: 3px;
}

/* 机器人列表区域 */
.robot-list-section {
  margin-bottom: 24px;
}

.robot-list-card {
  border: none;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  background: white;
}

.robot-table-container {
  padding: 0;
}

.robot-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.robot-avatar {
  flex-shrink: 0;
}

.robot-name {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.battery-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.battery-progress {
  flex: 1;
  min-width: 60px;
}

.battery-text {
  font-size: 12px;
  color: #6b7280;
  min-width: 30px;
}

.pagination-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
  border-top: 1px solid #f3f4f6;
  margin-top: 16px;
}

.pagination-info {
  font-size: 14px;
  color: #6b7280;
}

/* Element Plus 表格样式覆盖 */
.robot-list-card :deep(.el-table) {
  border: none;
}

.robot-list-card :deep(.el-table__header) {
  background-color: #f9fafb;
}

.robot-list-card :deep(.el-table th) {
  background-color: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
  font-weight: 600;
  color: #374151;
}

.robot-list-card :deep(.el-table td) {
  border-bottom: 1px solid #f3f4f6;
}

.robot-list-card :deep(.el-table__row:hover) {
  background-color: #f9fafb;
}

.robot-list-card :deep(.el-pagination) {
  justify-content: flex-end;
}

.robot-list-card :deep(.el-pagination .el-pager li) {
  background-color: transparent;
  color: #6b7280;
  font-size: 14px;
}

.robot-list-card :deep(.el-pagination .el-pager li.is-active) {
  background-color: #3b82f6;
  color: white;
}

.robot-list-card :deep(.el-pagination .btn-prev),
.robot-list-card :deep(.el-pagination .btn-next) {
  background-color: transparent;
  color: #6b7280;
}

.robot-list-card :deep(.el-pagination .btn-prev:hover),
.robot-list-card :deep(.el-pagination .btn-next:hover) {
  color: #3b82f6;
}



/* 响应式设计 */
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .main-content .el-col,
  .bottom-charts .el-col {
    margin-bottom: 16px;
  }
  
  .page-title {
    font-size: 24px;
  }
  
  .chart-placeholder,
  .map-placeholder {
    height: 200px;
  }
  
  .map-card,
  .robot-list-card {
    height: auto;
  }
}
</style>
