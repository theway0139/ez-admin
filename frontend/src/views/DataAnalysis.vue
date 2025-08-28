<template>
  <div class="data-analysis-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">数据分析</h1>
      <div class="search-box">
        <input type="text" placeholder="搜索分析报告..." class="search-input" />
        <i class="search-icon">🔍</i>
      </div>
    </div>

    <!-- 时间范围选择器 -->
    <div class="time-range-selector">
      <div class="time-range-label">分析时间范围:</div>
      <div class="time-range-options">
        <button 
          v-for="option in timeRangeOptions" 
          :key="option.value" 
          :class="['time-option', { active: selectedTimeRange === option.value }]"
          @click="selectTimeRange(option.value)"
        >
          {{ option.label }}
        </button>
        <div class="custom-date-range" v-if="selectedTimeRange === 'custom'">
          <div class="date-input-group">
            <input type="text" placeholder="mm/dd/yyyy" v-model="customDateRange.start" />
            <button class="date-picker-btn">
              <i class="calendar-icon">📅</i>
            </button>
          </div>
          <span class="date-separator">至</span>
          <div class="date-input-group">
            <input type="text" placeholder="mm/dd/yyyy" v-model="customDateRange.end" />
            <button class="date-picker-btn">
              <i class="calendar-icon">📅</i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 数据指标卡片 -->
    <div class="metrics-cards">
      <div class="metric-card">
        <div class="metric-header">
          <h3 class="metric-title">总任务数</h3>
          <button class="metric-detail-btn">
            <i class="list-icon">≡</i>
          </button>
        </div>
        <div class="metric-value">1,248</div>
        <div class="metric-trend">
          <span class="trend-label">同比增长</span>
          <span class="trend-value positive">12%</span>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-header">
          <h3 class="metric-title">成功率</h3>
          <button class="metric-detail-btn">
            <i class="check-icon">✓</i>
          </button>
        </div>
        <div class="metric-value">94.5%</div>
        <div class="metric-trend">
          <span class="trend-label">环比提升</span>
          <span class="trend-value positive">2.3%</span>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-header">
          <h3 class="metric-title">平均响应</h3>
          <button class="metric-detail-btn">
            <i class="time-icon">⏱</i>
          </button>
        </div>
        <div class="metric-value">156ms</div>
        <div class="metric-trend">
          <span class="trend-label">优化</span>
          <span class="trend-value positive">18ms</span>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-header">
          <h3 class="metric-title">数据量</h3>
          <button class="metric-detail-btn">
            <i class="data-icon">📊</i>
          </button>
        </div>
        <div class="metric-value">2.4GB</div>
        <div class="metric-trend">
          <span class="trend-label">日增长</span>
          <span class="trend-value">120MB</span>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-section">
      <div class="chart-container">
        <div class="chart-header">
          <h3 class="chart-title">机器人性能趋势</h3>
        </div>
        <div class="chart-content" ref="performanceChartRef"></div>
      </div>

      <div class="chart-container">
        <div class="chart-header">
          <h3 class="chart-title">任务完成率</h3>
        </div>
        <div class="chart-content" ref="completionRateChartRef"></div>
      </div>
      
      <div class="chart-container">
        <div class="chart-header">
          <h3 class="chart-title">资源使用分布</h3>
        </div>
        <div class="chart-content" ref="resourceDistributionChartRef"></div>
      </div>

      <div class="chart-container">
        <div class="chart-header">
          <h3 class="chart-title">事件分析</h3>
        </div>
        <div class="chart-content" ref="eventAnalysisChartRef"></div>
      </div>
    </div>
    
    <!-- 分析报告列表 -->
    <div class="report-list-section">
      <div class="section-header">
        <h2 class="section-title">分析报告列表</h2>
      </div>
      <div class="report-table-container">
        <table class="report-table">
          <thead>
            <tr>
              <th>报告名称</th>
              <th>生成时间</th>
              <th>时间范围</th>
              <th>分析类型</th>
              <th>数据量</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(report, index) in reportList" :key="index">
              <td>{{ report.name }}</td>
              <td>{{ report.createdAt }}</td>
              <td>{{ report.timeRange }}</td>
              <td>
                <span class="analysis-type" :class="report.typeClass">{{ report.type }}</span>
              </td>
              <td>{{ report.dataSize }}</td>
              <td class="action-buttons">
                <button class="action-btn view-btn" @click="viewReport(report.id)">
                  <i class="view-icon">👁️</i> 查看
                </button>
                <button class="action-btn export-btn" @click="exportReport(report.id)">
                  <i class="export-icon">⬇️</i> 导出
                </button>
                <button class="action-btn delete-btn" @click="deleteReport(report.id)">
                  <i class="delete-icon">🗑️</i> 删除
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
import * as echarts from 'echarts'
import { ElMessage, ElMessageBox } from 'element-plus'

// 图表引用
const performanceChartRef = ref(null);
const completionRateChartRef = ref(null);
const resourceDistributionChartRef = ref(null);
const eventAnalysisChartRef = ref(null);

let performanceChart = null;
let completionRateChart = null;
let resourceDistributionChart = null;
let eventAnalysisChart = null;

// 分析报告列表数据
const reportList = ref([
  {
    id: 1,
    name: '机器人性能趋势报告',
    createdAt: '2024-01-15 14:30',
    timeRange: '2024-01-08 ~ 2024-01-15',
    type: '性能分析',
    typeClass: 'performance-type',
    dataSize: '12500 条数据'
  },
  {
    id: 2,
    name: '任务执行分析',
    createdAt: '2024-01-14 09:15',
    timeRange: '2024-01-01 ~ 2024-01-14',
    type: '任务分析',
    typeClass: 'task-type',
    dataSize: '8900 条数据'
  },
  {
    id: 3,
    name: '资源使用月报',
    createdAt: '2024-01-01 08:00',
    timeRange: '2023-12-01 ~ 2023-12-31',
    type: '资源分析',
    typeClass: 'resource-type',
    dataSize: '35600 条数据'
  },
  {
    id: 4,
    name: '事件分析报告',
    createdAt: '2024-01-13 16:45',
    timeRange: '2024-01-10 ~ 2024-01-13',
    type: '事件分析',
    typeClass: 'event-type',
    dataSize: '4800 条数据'
  }
]);
// 时间范围选项
const timeRangeOptions = [
  { label: '24小时', value: '24h' },
  { label: '30天', value: '30d' },
  { label: '90天', value: '90d' },
  { label: '全年', value: 'year' },
  { label: '自定义', value: 'custom' }
]

const selectedTimeRange = ref('24h')
const customDateRange = reactive({
  start: '',
  end: ''
})

// 性能趋势数据
const performanceData = {
  days: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
  values: [65, 59, 80, 81, 56, 55, 40]
}

// 完成率数据
const completionRateData = {
  days: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
  values: [85, 78, 90, 93, 88, 95, 97]
}

// 资源使用分布数据
const resourceDistributionData = [
  { name: 'CPU', value: 25 },
  { name: '内存', value: 30 },
  { name: '存储', value: 20 },
  { name: '网络', value: 15 },
  { name: '其他', value: 10 }
]

// 事件分析数据
const eventAnalysisData = {
  days: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
  values: [12, 19, 8, 15, 7, 10, 14]
}

// 方法
const selectTimeRange = (range) => {
  selectedTimeRange.value = range
  // 这里可以添加根据时间范围更新数据的逻辑
  updateCharts()
}

// 报告操作功能
const viewReport = (id) => {
  console.log('查看报告:', id);
  ElMessage.success(`正在查看报告 #${id}`);
  // 实际应用中可以跳转到报告详情页或打开预览弹窗
};

const exportReport = (id) => {
  console.log('导出报告:', id);
  ElMessage.success(`报告 #${id} 导出成功`);
  // 实际应用中可以触发文件下载
};

const deleteReport = (id) => {
  ElMessageBox.confirm('确定要删除这份报告吗？', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    console.log('删除报告:', id);
    reportList.value = reportList.value.filter(report => report.id !== id);
    ElMessage.success('删除成功');
  }).catch(() => {
    ElMessage.info('已取消删除');
  });
}

const initPerformanceChart = () => {
  if (!performanceChartRef.value) return
  
  performanceChart = echarts.init(performanceChartRef.value)
  const option = {
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: performanceData.days,
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
      name: '性能趋势',
      type: 'line',
      data: performanceData.values,
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
    }],
    tooltip: {
      trigger: 'axis',
      formatter: '{b}: {c}%'
    }
  }
  performanceChart.setOption(option)
}

const initCompletionRateChart = () => {
  if (!completionRateChartRef.value) return
  
  completionRateChart = echarts.init(completionRateChartRef.value)
  const option = {
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: completionRateData.days,
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
      name: '完成率',
      type: 'line',
      data: completionRateData.values,
      smooth: true,
      lineStyle: {
        color: '#2196f3',
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
            color: 'rgba(33, 150, 243, 0.3)'
          }, {
            offset: 1,
            color: 'rgba(33, 150, 243, 0.1)'
          }]
        }
      },
      symbol: 'circle',
      symbolSize: 6,
      itemStyle: {
        color: '#2196f3'
      }
    }],
    tooltip: {
      trigger: 'axis',
      formatter: '{b}: {c}%'
    }
  }
  completionRateChart.setOption(option)
}

const initResourceDistributionChart = () => {
  if (!resourceDistributionChartRef.value) return
  
  resourceDistributionChart = echarts.init(resourceDistributionChartRef.value)
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'horizontal',
      top: 'top',
      data: resourceDistributionData.map(item => item.name),
      textStyle: {
        color: '#666'
      }
    },
    color: ['#b39ddb', '#9fa8da', '#90caf9', '#81d4fa', '#80deea'],
    series: [
      {
        name: '资源使用',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '14',
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: resourceDistributionData
      }
    ]
  }
  resourceDistributionChart.setOption(option)
}

const initEventAnalysisChart = () => {
  if (!eventAnalysisChartRef.value) return
  
  eventAnalysisChart = echarts.init(eventAnalysisChartRef.value)
  const option = {
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: eventAnalysisData.days,
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
    tooltip: {
      trigger: 'axis',
      formatter: '{b}: {c} 事件'
    },
    series: [
      {
        name: '事件统计',
        type: 'line',
        stack: 'Total',
        smooth: true,
        lineStyle: {
          width: 0
        },
        showSymbol: true,
        areaStyle: {
          opacity: 0.8,
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              {
                offset: 0,
                color: 'rgba(255, 99, 132, 0.8)'
              },
              {
                offset: 1,
                color: 'rgba(255, 99, 132, 0.1)'
              }
            ]
          }
        },
        emphasis: {
          focus: 'series'
        },
        data: eventAnalysisData.values
      }
    ]
  }
  eventAnalysisChart.setOption(option)
}

const updateCharts = () => {
  // 根据时间范围更新图表数据
  // 这里可以添加实际的数据更新逻辑
  if (performanceChart) {
    performanceChart.setOption({
      series: [{
        data: performanceData.values
      }]
    })
  }
  
  if (completionRateChart) {
    completionRateChart.setOption({
      series: [{
        data: completionRateData.values
      }]
    })
  }
  
  if (eventAnalysisChart) {
    eventAnalysisChart.setOption({
      series: [{
        data: eventAnalysisData.values
      }]
    })
  }
}

// 生命周期钩子
onMounted(() => {
  nextTick(() => {
    initPerformanceChart()
    initCompletionRateChart()
    initResourceDistributionChart()
    initEventAnalysisChart()
    
    // 窗口大小变化时重新调整图表大小
    window.addEventListener('resize', handleResize)
  })
})

onUnmounted(() => {
  if (performanceChart) {
    performanceChart.dispose()
  }
  if (completionRateChart) {
    completionRateChart.dispose()
  }
  if (resourceDistributionChart) {
    resourceDistributionChart.dispose()
  }
  if (eventAnalysisChart) {
    eventAnalysisChart.dispose()
  }
  window.removeEventListener('resize', handleResize)
})

const handleResize = () => {
  if (performanceChart) {
    performanceChart.resize()
  }
  if (completionRateChart) {
    completionRateChart.resize()
  }
  if (resourceDistributionChart) {
    resourceDistributionChart.resize()
  }
  if (eventAnalysisChart) {
    eventAnalysisChart.resize()
  }
}
</script>

<style scoped>
.data-analysis-container {
}

/* 页面头部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.search-box {
  position: relative;
  width: 300px;
}

.search-input {
  width: 100%;
  padding: 10px 16px;
  padding-right: 40px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 14px;
  outline: none;
  transition: all 0.3s;
}

.search-input:focus {
  border-color: #2196f3;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.1);
}

.search-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #999;
  font-size: 16px;
}

/* 时间范围选择器 */
.time-range-selector {
  display: flex;
  align-items: center;
  margin-bottom: 24px;
  background-color: #f9f9f9;
  padding: 16px;
  border-radius: 8px;
}

.time-range-label {
  font-size: 14px;
  color: #666;
  margin-right: 16px;
  white-space: nowrap;
}

.time-range-options {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.time-option {
  padding: 8px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  background-color: white;
  color: #333;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.time-option:hover {
  border-color: #2196f3;
  color: #2196f3;
}

.time-option.active {
  background-color: #2196f3;
  color: white;
  border-color: #2196f3;
}

.custom-date-range {
  display: flex;
  align-items: center;
  margin-left: 16px;
}

.date-input-group {
  position: relative;
  width: 140px;
}

.date-input-group input {
  width: 100%;
  padding: 8px 36px 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 14px;
  outline: none;
}

.date-picker-btn {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  color: #666;
}

.date-separator {
  margin: 0 8px;
  color: #666;
}

/* 数据指标卡片 */
.metrics-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  margin-bottom: 32px;
}

.metric-card {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.metric-title {
  font-size: 16px;
  color: #666;
  margin: 0;
  font-weight: 500;
}

.metric-detail-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #2196f3;
  font-size: 18px;
  padding: 0;
}

.metric-value {
  font-size: 28px;
  font-weight: 600;
  color: #333;
  margin-bottom: 12px;
}

.metric-trend {
  display: flex;
  align-items: center;
  font-size: 14px;
}

.trend-label {
  color: #666;
  margin-right: 8px;
}

.trend-value {
  font-weight: 500;
}

.trend-value.positive {
  color: #4caf50;
}

.trend-value.negative {
  color: #f44336;
}

/* 图表区域 */
.charts-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

/* 报告列表样式 */
.report-list-section {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 20px;
}

.section-header {
  margin-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 10px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.report-table-container {
  width: 100%;
  overflow-x: auto;
}

.report-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.report-table th,
.report-table td {
  padding: 12px 8px;
  text-align: left;
  border-bottom: 1px solid #ebeef5;
}

.report-table th {
  font-weight: 600;
  color: #606266;
  background-color: #f5f7fa;
}

.report-table tr:hover {
  background-color: #f5f7fa;
}

.analysis-type {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  color: #fff;
}

.performance-type {
  background-color: #409eff;
}

.task-type {
  background-color: #67c23a;
}

.resource-type {
  background-color: #9254de;
}

.event-type {
  background-color: #ff9f43;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.action-btn {
  border: none;
  background: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.3s;
}

.view-btn {
  color: #409eff;
}

.export-btn {
  color: #67c23a;
}

.delete-btn {
  color: #f56c6c;
}

.action-btn:hover {
  background-color: #ecf5ff;
}.chart-container {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.chart-header {
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.chart-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.chart-content {
  height: 300px;
  width: 100%;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .metrics-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .search-box {
    width: 100%;
    margin-top: 16px;
  }
  
  .time-range-selector {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .time-range-label {
    margin-bottom: 12px;
  }
  
  .metrics-cards {
    grid-template-columns: 1fr;
  }
  
  .charts-section {
    grid-template-columns: 1fr;
  }
  
  .custom-date-range {
    flex-direction: column;
    margin-left: 0;
    margin-top: 12px;
    width: 100%;
  }
  
  .date-input-group {
    width: 100%;
    margin-bottom: 8px;
  }
  
  .date-separator {
    margin: 8px 0;
  }
}
</style>