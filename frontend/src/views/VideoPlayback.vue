<template>
  <div class="video-playback-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">录像回放</h1>
      </div>
      <div class="header-right">
        <el-input
          v-model="searchText"
          placeholder="搜索录像文件..."
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
      <div class="filter-row">
        <div class="filter-item">
          <label class="filter-label">日期范围</label>
          <el-date-picker
            v-model="filters.dateRange"
            type="date"
            placeholder="mm/dd/yyyy"
            format="MM/DD/YYYY"
            value-format="YYYY-MM-DD"
            class="filter-input"
          />
        </div>
        
        <div class="filter-item">
          <label class="filter-label">摄像头位置</label>
          <el-select
            v-model="filters.cameraLocation"
            placeholder="全部摄像头"
            class="filter-input"
            clearable
          >
            <el-option label="全部摄像头" value="" />
            <el-option label="A区大厅" value="A区大厅" />
            <el-option label="B区走廊" value="B区走廊" />
            <el-option label="C区机房" value="C区机房" />
            <el-option label="D区停车场" value="D区停车场" />
          </el-select>
        </div>
        
        <div class="filter-item">
          <label class="filter-label">录像类型</label>
          <el-select
            v-model="filters.videoType"
            placeholder="全部类型"
            class="filter-input"
            clearable
          >
            <el-option label="全部类型" value="" />
            <el-option label="常规" value="常规" />
            <el-option label="事件" value="事件" />
            <el-option label="报警" value="报警" />
          </el-select>
        </div>
        
        <div class="filter-item">
          <label class="filter-label">时长范围</label>
          <el-select
            v-model="filters.duration"
            placeholder="全部时长"
            class="filter-input"
            clearable
          >
            <el-option label="全部时长" value="" />
            <el-option label="5分钟以下" value="short" />
            <el-option label="5-30分钟" value="medium" />
            <el-option label="30分钟以上" value="long" />
          </el-select>
        </div>
      </div>
    </div>

    <!-- 录像列表表格 -->
    <div class="table-container">
      <el-table
        :data="filteredVideoList"
        stripe
        class="video-table"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        
        <el-table-column prop="name" label="录像名称" min-width="200">
          <template #default="{ row }">
            <div class="video-name">
              <el-icon class="video-icon"><VideoPlay /></el-icon>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="location" label="摄像头位置" width="150" />
        
        <el-table-column prop="startTime" label="开始时间" width="180">
          <template #default="{ row }">
            <span>{{ formatDateTime(row.startTime) }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="duration" label="时长" width="120">
          <template #default="{ row }">
            <span>{{ row.duration }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag
              :type="getTypeTagType(row.type)"
              size="small"
            >
              {{ row.type }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="fileSize" label="文件大小" width="120" />
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button
                type="primary"
                size="small"
                @click="playVideo(row)"
              >
                <el-icon><VideoPlay /></el-icon>
                播放
              </el-button>
              <el-button
                type="success"
                size="small"
                @click="downloadVideo(row)"
              >
                <el-icon><Download /></el-icon>
                下载
              </el-button>
              <el-button
                type="danger"
                size="small"
                @click="deleteVideo(row)"
              >
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 分页 -->
    <div class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="totalVideos"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search,
  VideoPlay,
  Download,
  Delete
} from '@element-plus/icons-vue'

// 响应式数据
const searchText = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const totalVideos = ref(0)
const selectedVideos = ref([])

// 筛选器
const filters = reactive({
  dateRange: '',
  cameraLocation: '',
  videoType: '',
  duration: ''
})

// 模拟录像数据
const videoList = ref([
  {
    id: 1,
    name: 'A区大厅监控录像',
    location: 'A区大厅东侧',
    startTime: '2024-01-15 09:30:25',
    duration: '15分30秒',
    type: '常规',
    fileSize: '256 MB'
  },
  {
    id: 2,
    name: 'B区走廊事件录像',
    location: 'B区2楼走廊',
    startTime: '2024-01-15 14:20:10',
    duration: '8分45秒',
    type: '事件',
    fileSize: '128 MB'
  },
  {
    id: 3,
    name: 'C区机房报警录像',
    location: 'C区机房入口',
    startTime: '2024-01-15 18:05:33',
    duration: '22分15秒',
    type: '报警',
    fileSize: '512 MB'
  },
  {
    id: 4,
    name: 'D区停车场常规录像',
    location: 'D区停车场门口',
    startTime: '2024-01-15 11:45:20',
    duration: '45分10秒',
    type: '常规',
    fileSize: '1.2 GB'
  }
])

// 计算属性
const filteredVideoList = computed(() => {
  let filtered = videoList.value
  
  // 搜索过滤
  if (searchText.value) {
    filtered = filtered.filter(video => 
      video.name.toLowerCase().includes(searchText.value.toLowerCase()) ||
      video.location.toLowerCase().includes(searchText.value.toLowerCase())
    )
  }
  
  // 摄像头位置过滤
  if (filters.cameraLocation) {
    filtered = filtered.filter(video => video.location.includes(filters.cameraLocation))
  }
  
  // 录像类型过滤
  if (filters.videoType) {
    filtered = filtered.filter(video => video.type === filters.videoType)
  }
  
  // 时长过滤
  if (filters.duration) {
    filtered = filtered.filter(video => {
      const duration = video.duration
      if (filters.duration === 'short') {
        return duration.includes('分') && parseInt(duration) < 5
      } else if (filters.duration === 'medium') {
        const minutes = parseInt(duration)
        return minutes >= 5 && minutes <= 30
      } else if (filters.duration === 'long') {
        return parseInt(duration) > 30
      }
      return true
    })
  }
  
  totalVideos.value = filtered.length
  return filtered
})

// 方法
const formatDateTime = (dateTime) => {
  return dateTime
}

const getTypeTagType = (type) => {
  const typeMap = {
    '常规': '',
    '事件': 'warning',
    '报警': 'danger'
  }
  return typeMap[type] || ''
}

const handleSelectionChange = (selection) => {
  selectedVideos.value = selection
}

const playVideo = (video) => {
  ElMessage.success(`开始播放: ${video.name}`)
  // 这里可以实现视频播放逻辑
}

const downloadVideo = (video) => {
  ElMessage.success(`开始下载: ${video.name}`)
  // 这里可以实现下载逻辑
}

const deleteVideo = async (video) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除录像 "${video.name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 从列表中移除
    const index = videoList.value.findIndex(item => item.id === video.id)
    if (index > -1) {
      videoList.value.splice(index, 1)
      ElMessage.success('删除成功')
    }
  } catch {
    ElMessage.info('已取消删除')
  }
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (page) => {
  currentPage.value = page
}

// 生命周期
onMounted(() => {
  totalVideos.value = videoList.value.length
})
</script>

<style scoped>
.video-playback-container {
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
  gap: 24px;
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

/* 表格容器 */
.table-container {
  background: white;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.video-table {
  width: 100%;
}

.video-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.video-icon {
  color: #409eff;
  font-size: 16px;
}

.action-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.action-buttons .el-button {
  padding: 4px 8px;
  font-size: 12px;
}

/* 分页 */
.pagination-container {
  display: flex;
  justify-content: center;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .video-playback-container {
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
  
  .filter-row {
    flex-direction: column;
    gap: 16px;
  }
  
  .filter-item {
    min-width: auto;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 4px;
  }
  
  .action-buttons .el-button {
    width: 100%;
    justify-content: center;
  }
}

/* 暗色模式适配 */
@media (prefers-color-scheme: dark) {
  .video-playback-container {
    background-color: #1a1a1a;
  }
  
  .page-header,
  .filter-section,
  .table-container,
  .pagination-container {
    background: #2d2d2d;
    color: #ffffff;
  }
  
  .page-title {
    color: #ffffff;
  }
  
  .filter-label {
    color: #cccccc;
  }
}
</style>