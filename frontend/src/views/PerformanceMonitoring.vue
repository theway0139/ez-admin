<template>
  <div class="performance-monitoring-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">性能监控</h1>
      </div>
      <div class="header-right">
        <el-input
          v-model="searchText"
          placeholder="搜索监控项..."
          class="search-input"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
    </div>

    <!-- 时间范围选择器 -->
    <div class="time-range-section">
      <div class="time-range-label">时间范围:</div>
      <div class="time-range-buttons">
        <el-button
          v-for="range in timeRanges"
          :key="range.value"
          :type="selectedTimeRange === range.value ? 'primary' : 'default'"
          size="small"
          @click="selectTimeRange(range.value)"
        >
          {{ range.label }}
        </el-button>
        <el-date-picker
          v-if="selectedTimeRange === 'custom'"
          v-model="customDateRange"
          type="datetimerange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          format="MM/DD/YYYY HH:mm"
          value-format="YYYY-MM-DD HH:mm:ss"
          class="custom-date-picker"
        />
      </div>
    </div>

    <!-- 性能指标卡片 -->
    <div class="metrics-grid">
      <div class="metric-card cpu-card">
        <div class="metric-header">
          <div class="metric-icon cpu-icon">
            <el-icon><Cpu /></el-icon>
          </div>
          <div class="metric-info">
            <div class="metric-title">CPU使用率</div>
            <div class="metric-value">{{ cpuUsage }}%</div>
          </div>
        </div>
        <div class="metric-progress">
          <el-progress
            :percentage="cpuUsage"
            :stroke-width="8"
            :show-text="false"
            color="#ff4757"
          />
          <div class="progress-labels">
            <span>0%</span>
            <span>96%</span>
            <span>100%</span>
          </div>
        </div>
      </div>

      <div class="metric-card memory-card">
        <div class="metric-header">
          <div class="metric-icon memory-icon">
            <el-icon><Monitor /></el-icon>
          </div>
          <div class="metric-info">
            <div class="metric-title">内存使用</div>
            <div class="metric-value">{{ memoryUsage }}%</div>
          </div>
        </div>
        <div class="metric-progress">
          <el-progress
            :percentage="memoryUsage"
            :stroke-width="8"
            :show-text="false"
            color="#ff4757"
          />
          <div class="progress-labels">
            <span>0%</span>
            <span>95%</span>
            <span>100%</span>
          </div>
        </div>
      </div>

      <div class="metric-card disk-card">
        <div class="metric-header">
          <div class="metric-icon disk-icon">
            <el-icon><FolderOpened /></el-icon>
          </div>
          <div class="metric-info">
            <div class="metric-title">磁盘使用</div>
            <div class="metric-value">{{ diskUsage }}%</div>
          </div>
        </div>
        <div class="metric-progress">
          <el-progress
            :percentage="diskUsage"
            :stroke-width="8"
            :show-text="false"
            color="#ffa502"
          />
          <div class="progress-labels">
            <span>0%</span>
            <span>88%</span>
            <span>100%</span>
          </div>
        </div>
      </div>

      <div class="metric-card network-card">
        <div class="metric-header">
          <div class="metric-icon network-icon">
            <el-icon><Connection /></el-icon>
          </div>
          <div class="metric-info">
            <div class="metric-title">网络流量</div>
            <div class="metric-value">{{ networkTraffic }}</div>
          </div>
        </div>
        <div class="metric-progress">
          <el-progress
            :percentage="networkUsagePercent"
            :stroke-width="8"
            :show-text="false"
            color="#2ed573"
          />
          <div class="progress-labels">
            <span>0%</span>
            <span>70%</span>
            <span>100%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-section">
      <div class="chart-container">
        <div class="chart-header">
          <h3 class="chart-title">CPU 使用率</h3>
        </div>
        <div class="chart-content" ref="cpuChartRef"></div>
      </div>

      <div class="chart-container">
        <div class="chart-header">
          <h3 class="chart-title">内存使用率</h3>
        </div>
        <div class="chart-content" ref="memoryChartRef"></div>
      </div>

      <div class="chart-container">
        <div class="chart-header">
          <h3 class="chart-title">网络流量</h3>
        </div>
        <div class="chart-content" ref="networkChartRef"></div>
      </div>

      <div class="chart-container">
        <div class="chart-header">
          <h3 class="chart-title">磁盘 I/O</h3>
        </div>
        <div class="chart-content" ref="diskChartRef"></div>
      </div>
    </div>

    <!-- 系统监控指标表格 -->
    <div class="monitoring-table-section">
      <div class="table-header">
        <h3 class="table-title">系统监控指标</h3>
      </div>
      <div class="table-container">
        <table class="monitoring-table">
          <thead>
            <tr>
              <th>监控项</th>
              <th>当前值</th>
              <th>阈值</th>
              <th>状态</th>
              <th>趋势</th>
              <th>最后更新</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in monitoringItems" :key="item.id">
              <td>
                <div class="metric-info">
                  <div class="metric-indicator" :style="{ backgroundColor: item.color }"></div>
                  <span>{{ item.name }}</span>
                </div>
              </td>
              <td class="current-value">{{ item.currentValue }}</td>
              <td class="threshold-value">{{ item.threshold }}</td>
              <td>
                <span class="status-badge" :class="item.status">{{ item.statusText }}</span>
              </td>
              <td>
                <div class="trend-indicator" :class="item.trend">
                  <i class="trend-icon" :class="getTrendIcon(item.trend)"></i>
                  <span>{{ item.trendText }}</span>
                </div>
              </td>
              <td class="update-time">{{ item.lastUpdate }}</td>
              <td>
                <button class="action-btn detail-btn" @click="viewDetails(item)">
                  <i class="icon-eye"></i>
                  详情
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Search,
  Cpu,
  Monitor,
  FolderOpened,
  Connection
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'

// 响应式数据
const searchText = ref('')
const selectedTimeRange = ref('6h')
const customDateRange = ref([])
const cpuUsage = ref(77)
const memoryUsage = ref(81)
const diskUsage = ref(79)
const networkTraffic = ref('350')
const networkUsagePercent = ref(70)

// 图表引用
const cpuChartRef = ref(null)
const memoryChartRef = ref(null)
const networkChartRef = ref(null)
const diskChartRef = ref(null)
let cpuChart = null
let memoryChart = null
let networkChart = null
let diskChart = null

// 时间范围选项
const timeRanges = [
  { label: '6小时', value: '6h' },
  { label: '24小时', value: '24h' },
  { label: '7天', value: '7d' },
  { label: '30天', value: '30d' },
  { label: '自定义', value: 'custom' }
]

// 模拟数据
const cpuData = {
  times: ['10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00'],
  values: [65, 59, 80, 81, 56, 55, 40]
}

const memoryData = {
  times: ['10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00'],
  values: [28, 48, 40, 19, 86, 27, 90]
}

const networkData = {
  times: ['10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00'],
  values: [65, 59, 80, 81, 56, 55, 40]
}

const diskData = {
  times: ['10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00'],
  values: [28, 48, 40, 19, 86, 27, 90]
}

// 监控指标数据
const monitoringItems = ref([
  {
    id: 1,
    name: '系统CPU使用率',
    currentValue: '45%',
    threshold: '80%',
    status: 'normal',
    statusText: '正常',
    trend: 'up',
    trendText: '上升',
    lastUpdate: '2分钟前',
    color: '#4caf50'
  },
  {
    id: 2,
    name: '内存使用率',
    currentValue: '65%',
    threshold: '85%',
    status: 'normal',
    statusText: '正常',
    trend: 'stable',
    trendText: '平稳',
    lastUpdate: '2分钟前',
    color: '#4caf50'
  },
  {
    id: 3,
    name: '磁盘I/O等待',
    currentValue: '12ms',
    threshold: '50ms',
    status: 'normal',
    statusText: '正常',
    trend: 'down',
    trendText: '下降',
    lastUpdate: '2分钟前',
    color: '#4caf50'
  },
  {
    id: 4,
    name: '网络带宽使用',
    currentValue: '120Mbps',
    threshold: '500Mbps',
    status: 'normal',
    statusText: '正常',
    trend: 'up',
    trendText: '上升',
    lastUpdate: '2分钟前',
    color: '#4caf50'
  },
  {
    id: 5,
    name: '数据库连接数',
    currentValue: '85',
    threshold: '100',
    status: 'warning',
    statusText: '警告',
    trend: 'up',
    trendText: '上升',
    lastUpdate: '2分钟前',
    color: '#ff9800'
  },
  {
    id: 6,
    name: 'API响应时间',
    currentValue: '250ms',
    threshold: '500ms',
    status: 'normal',
    statusText: '正常',
    trend: 'stable',
    trendText: '平稳',
    lastUpdate: '2分钟前',
    color: '#4caf50'
  }
])

// 方法
const selectTimeRange = (range) => {
  selectedTimeRange.value = range
  if (range !== 'custom') {
    customDateRange.value = []
  }
  updateCharts()
}

const initCpuChart = () => {
  if (!cpuChartRef.value) return
  
  cpuChart = echarts.init(cpuChartRef.value)
  const option = {
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: cpuData.times,
      axisLine: {
        lineStyle: {
          color: '#e0e0e0'
        }
      },
      axisLabel: {
        color: '#666'
      }
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100,
      axisLine: {
        lineStyle: {
          color: '#e0e0e0'
        }
      },
      axisLabel: {
        color: '#666'
      },
      splitLine: {
        lineStyle: {
          color: '#f0f0f0'
        }
      }
    },
    series: [{
      name: 'CPU使用率 (%)',
      type: 'line',
      data: cpuData.values,
      smooth: true,
      lineStyle: {
        color: '#4caf50',
        width: 3
      },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [{
            offset: 0,
            color: 'rgba(76, 175, 80, 0.3)'
          }, {
            offset: 1,
            color: 'rgba(76, 175, 80, 0.1)'
          }]
        }
      },
      symbol: 'circle',
      symbolSize: 6,
      itemStyle: {
        color: '#4caf50'
      }
    }]
  }
  cpuChart.setOption(option)
}

const initMemoryChart = () => {
  if (!memoryChartRef.value) return
  
  memoryChart = echarts.init(memoryChartRef.value)
  const option = {
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: memoryData.times,
      axisLine: {
        lineStyle: {
          color: '#e0e0e0'
        }
      },
      axisLabel: {
        color: '#666'
      }
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100,
      axisLine: {
        lineStyle: {
          color: '#e0e0e0'
        }
      },
      axisLabel: {
        color: '#666'
      },
      splitLine: {
        lineStyle: {
          color: '#f0f0f0'
        }
      }
    },
    series: [{
      name: '内存使用 (MB)',
      type: 'line',
      data: memoryData.values,
      smooth: true,
      lineStyle: {
        color: '#ff6b9d',
        width: 3
      },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [{
            offset: 0,
            color: 'rgba(255, 107, 157, 0.3)'
          }, {
            offset: 1,
            color: 'rgba(255, 107, 157, 0.1)'
          }]
        }
      },
      symbol: 'circle',
      symbolSize: 6,
      itemStyle: {
        color: '#ff6b9d'
      }
    }]
  }
  memoryChart.setOption(option)
}

const initNetworkChart = () => {
  if (!networkChartRef.value) return
  
  networkChart = echarts.init(networkChartRef.value)
  const option = {
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: networkData.times,
      axisLine: {
        lineStyle: {
          color: '#e0e0e0'
        }
      },
      axisLabel: {
        color: '#666'
      }
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100,
      axisLine: {
        lineStyle: {
          color: '#e0e0e0'
        }
      },
      axisLabel: {
        color: '#666'
      },
      splitLine: {
        lineStyle: {
          color: '#f0f0f0'
        }
      }
    },
    series: [{
      name: '网络流量 (Mbps)',
      type: 'line',
      data: networkData.values,
      smooth: true,
      lineStyle: {
        color: '#5dade2',
        width: 3
      },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [{
            offset: 0,
            color: 'rgba(93, 173, 226, 0.3)'
          }, {
            offset: 1,
            color: 'rgba(93, 173, 226, 0.1)'
          }]
        }
      },
      symbol: 'circle',
      symbolSize: 6,
      itemStyle: {
        color: '#5dade2'
      }
    }]
  }
  networkChart.setOption(option)
}

const initDiskChart = () => {
  if (!diskChartRef.value) return
  
  diskChart = echarts.init(diskChartRef.value)
  const option = {
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: diskData.times,
      axisLine: {
        lineStyle: {
          color: '#e0e0e0'
        }
      },
      axisLabel: {
        color: '#666'
      }
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100,
      axisLine: {
        lineStyle: {
          color: '#e0e0e0'
        }
      },
      axisLabel: {
        color: '#666'
      },
      splitLine: {
        lineStyle: {
          color: '#f0f0f0'
        }
      }
    },
    series: [{
      name: '磁盘 I/O (MB/s)',
      type: 'line',
      data: diskData.values,
      smooth: true,
      lineStyle: {
        color: '#bb86fc',
        width: 3
      },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [{
            offset: 0,
            color: 'rgba(187, 134, 252, 0.3)'
          }, {
            offset: 1,
            color: 'rgba(187, 134, 252, 0.1)'
          }]
        }
      },
      symbol: 'circle',
      symbolSize: 6,
      itemStyle: {
        color: '#bb86fc'
      }
    }]
  }
  diskChart.setOption(option)
}

const updateCharts = () => {
  // 根据时间范围更新图表数据
  if (cpuChart) {
    cpuChart.setOption({
      xAxis: {
        data: cpuData.times
      },
      series: [{
        data: cpuData.values
      }]
    })
  }
  
  if (memoryChart) {
    memoryChart.setOption({
      xAxis: {
        data: memoryData.times
      },
      series: [{
        data: memoryData.values
      }]
    })
  }
}

const resizeCharts = () => {
  if (cpuChart) cpuChart.resize()
  if (memoryChart) memoryChart.resize()
}

// 模拟实时数据更新
const updateMetrics = () => {
  cpuUsage.value = Math.floor(Math.random() * 20) + 70
  memoryUsage.value = Math.floor(Math.random() * 20) + 75
  diskUsage.value = Math.floor(Math.random() * 15) + 75
  networkTraffic.value = Math.floor(Math.random() * 100) + 300
  networkUsagePercent.value = Math.floor(Math.random() * 30) + 60
}

// 获取趋势图标
const getTrendIcon = (trend) => {
  switch (trend) {
    case 'up':
      return 'trend-up'
    case 'down':
      return 'trend-down'
    case 'stable':
      return 'trend-stable'
    default:
      return 'trend-stable'
  }
}

// 查看详情
const viewDetails = (item) => {
  console.log('查看详情:', item)
  // 这里可以实现详情弹窗或跳转到详情页面
}

let metricsInterval = null

// 生命周期
onMounted(async () => {
  await nextTick()
  initCpuChart()
  initMemoryChart()
  initNetworkChart()
  initDiskChart()
  
  // 启动实时数据更新
  metricsInterval = setInterval(updateMetrics, 5000)
  
  // 监听窗口大小变化
  window.addEventListener('resize', resizeCharts)
})

onUnmounted(() => {
  if (cpuChart) {
    cpuChart.dispose()
    cpuChart = null
  }
  if (memoryChart) {
    memoryChart.dispose()
    memoryChart = null
  }
  if (networkChart) {
    networkChart.dispose()
    networkChart = null
  }
  if (diskChart) {
    diskChart.dispose()
    diskChart = null
  }
  if (metricsInterval) {
    clearInterval(metricsInterval)
  }
  window.removeEventListener('resize', resizeCharts)
})
</script>

<style scoped>
.performance-monitoring-container {
  min-height: 100vh;
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

/* 时间范围选择器 */
.time-range-section {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  padding: 16px 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.time-range-label {
  font-size: 14px;
  font-weight: 500;
  color: #606266;
  white-space: nowrap;
}

.time-range-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.custom-date-picker {
  margin-left: 8px;
}

/* 性能指标卡片 */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.metric-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.metric-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.metric-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.cpu-icon {
  background: linear-gradient(135deg, #ff6b6b, #ff8e8e);
}

.memory-icon {
  background: linear-gradient(135deg, #ff6b6b, #ff8e8e);
}

.disk-icon {
  background: linear-gradient(135deg, #ffa726, #ffcc02);
}

.network-icon {
  background: linear-gradient(135deg, #66bb6a, #81c784);
}

.metric-info {
  flex: 1;
}

.metric-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 4px;
}

.metric-value {
  font-size: 32px;
  font-weight: 700;
  color: #303133;
  line-height: 1;
}

.metric-progress {
  position: relative;
}

.progress-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}

/* 图表区域 */
.charts-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-top: 24px;
}

.chart-container {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.chart-header {
  margin-bottom: 20px;
}

.chart-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.chart-content {
  height: 300px;
  width: 100%;
}

/* 监控指标表格样式 */
.monitoring-table-section {
  margin-top: 32px;
}

.table-header {
  margin-bottom: 16px;
}

.table-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.monitoring-table {
  width: 100%;
  border-collapse: collapse;
}

.monitoring-table th {
  background: #f8f9fa;
  padding: 16px;
  text-align: left;
  font-weight: 600;
  color: #333;
  border-bottom: 1px solid #e9ecef;
}

.monitoring-table td {
  padding: 16px;
  border-bottom: 1px solid #f1f3f4;
  vertical-align: middle;
}

.monitoring-table tbody tr:hover {
  background: #f8f9fa;
}

.metric-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.metric-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.current-value {
  font-weight: 600;
  color: #333;
}

.threshold-value {
  color: #666;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.normal {
  background: #e8f5e8;
  color: #2e7d32;
}

.status-badge.warning {
  background: #fff3e0;
  color: #f57c00;
}

.status-badge.error {
  background: #ffebee;
  color: #d32f2f;
}

.trend-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
}

.trend-icon {
  width: 16px;
  height: 16px;
}

.trend-icon.trend-up::before {
  content: '↑';
  color: #f44336;
}

.trend-icon.trend-down::before {
  content: '↓';
  color: #4caf50;
}

.trend-icon.trend-stable::before {
  content: '→';
  color: #666;
}

.update-time {
  color: #666;
  font-size: 14px;
}

.action-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  transition: all 0.2s;
}

.detail-btn {
  background: #e3f2fd;
  color: #1976d2;
}

.detail-btn:hover {
  background: #bbdefb;
}

.icon-eye::before {
  content: '👁';
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .charts-section {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .performance-monitoring-container {
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
  
  .time-range-section {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .time-range-buttons {
    justify-content: center;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .chart-content {
    height: 250px;
  }
}

/* 暗色模式适配 */
@media (prefers-color-scheme: dark) {
  .performance-monitoring-container {
    background-color: #1a1a1a;
  }
  
  .time-range-section,
  .metric-card,
  .chart-container {
    background: #2d2d2d;
    color: #ffffff;
  }
  
  .page-title,
  .chart-title {
    color: #ffffff;
  }
  
  .metric-value {
    color: #ffffff;
  }
  
  .time-range-label {
    color: #cccccc;
  }
}
</style>