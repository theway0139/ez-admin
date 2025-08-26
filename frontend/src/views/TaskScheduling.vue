<template>
  <div class="task-scheduling">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">任务调度</h1>
      </div>
      <div class="header-right">
        <el-button type="primary" class="export-btn">
          <el-icon><Download /></el-icon>
          导出任务
        </el-button>
      </div>
    </div>

    <!-- 筛选器区域 -->
    <div class="filter-section">
      <div class="filter-item">
        <label class="filter-label">任务状态</label>
        <el-select v-model="selectedStatus" placeholder="全部状态" clearable>
          <el-option label="全部状态" value="" />
          <el-option label="进行中" value="进行中" />
          <el-option label="已暂停" value="已暂停" />
          <el-option label="已完成" value="已完成" />
        </el-select>
      </div>
      <div class="filter-item">
        <label class="filter-label">优先级</label>
        <el-select v-model="selectedPriority" placeholder="全部优先级" clearable>
          <el-option label="全部优先级" value="" />
          <el-option label="高" value="高" />
          <el-option label="中" value="中" />
          <el-option label="低" value="低" />
        </el-select>
      </div>
      <div class="filter-item">
        <label class="filter-label">机器人</label>
        <el-select v-model="selectedRobot" placeholder="全部机器人" clearable>
          <el-option label="全部机器人" value="" />
          <el-option label="探索者-X1" value="探索者-X1" />
          <el-option label="守护者-Z2" value="守护者-Z2" />
          <el-option label="服务者-S3" value="服务者-S3" />
          <el-option label="运输者-T5" value="运输者-T5" />
        </el-select>
      </div>
    </div>

    <!-- 任务列表表格 -->
    <div class="table-section">
      <el-table
        :data="filteredTaskList"
        class="task-table"
        stripe
        @selection-change="handleSelectionChange"
      >
        <el-table-column prop="taskName" label="任务名称" width="200">
          <template #default="{ row }">
            <div class="task-name-cell">
              <div class="task-name">{{ row.taskName }}</div>
              <div class="task-id">{{ row.taskId }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="机器人" width="150">
          <template #default="{ row }">
            <div class="robot-cell">
              <el-avatar :size="24" :src="row.robotAvatar" class="robot-avatar" />
              <span class="robot-name">{{ row.robotName }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="优先级" width="100">
          <template #default="{ row }">
            <el-tag
              :type="getPriorityType(row.priority)"
              size="small"
            >
              {{ row.priority }}
            </el-tag>
          </template>
        </el-table-column>
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
        <el-table-column label="进度" width="150">
          <template #default="{ row }">
            <div class="progress-cell">
              <el-progress
                :percentage="row.progress"
                :color="getProgressColor(row.progress)"
                :stroke-width="8"
                class="task-progress"
              />
              <span class="progress-text">{{ row.progress }}%</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="startTime" label="开始时间" width="150" />
        <el-table-column prop="estimatedCompletion" label="预计完成" width="150" />
      </el-table>
    </div>

    <!-- 分页 -->
    <div class="pagination-section">
      <div class="pagination-info">
        显示 {{ (currentPage - 1) * pageSize + 1 }} 至 {{ Math.min(currentPage * pageSize, totalTasks) }} 条，共 {{ totalTasks }} 条
      </div>
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="totalTasks"
        :page-sizes="[10, 20, 50, 100]"
        layout="prev, pager, next"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Download } from '@element-plus/icons-vue'

// 响应式数据
const selectedStatus = ref('')
const selectedPriority = ref('')
const selectedRobot = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const totalTasks = ref(32)
const selectedTasks = ref([])

// 任务列表数据
const taskList = ref([
  {
    taskName: 'A区3楼环境巡检',
    taskId: 'TASK-2023056',
    robotName: '探索者-X1',
    robotAvatar: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMTIiIGN5PSIxMiIgcj0iMTIiIGZpbGw9IiMxMGI5ODEiLz4KPHN2ZyB4PSI2IiB5PSI2IiB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0id2hpdGUiPgo8cGF0aCBkPSJNMTIgMkM2LjQ4IDIgMiA2LjQ4IDIgMTJzNC40OCAxMCAxMCAxMCAxMC00LjQ4IDEwLTEwUzE3LjUyIDIgMTIgMnptLTIgMTVsLTUtNSAxLjQxLTEuNDFMMTAgMTQuMTdsNy41OS03LjU5TDE5IDhsLTkgOXoiLz4KPC9zdmc+Cjwvc3ZnPgo=',
    priority: '中',
    status: '进行中',
    progress: 75,
    startTime: '2023-07-29 08:30',
    estimatedCompletion: '2023-07-29 09:45'
  },
  {
    taskName: 'B区1楼安全巡逻',
    taskId: 'TASK-2023057',
    robotName: '守护者-Z2',
    robotAvatar: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMTIiIGN5PSIxMiIgcj0iMTIiIGZpbGw9IiMzYjgyZjYiLz4KPHN2ZyB4PSI2IiB5PSI2IiB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0id2hpdGUiPgo8cGF0aCBkPSJNMTIgMkM2LjQ4IDIgMiA2LjQ4IDIgMTJzNC40OCAxMCAxMCAxMCAxMC00LjQ4IDEwLTEwUzE3LjUyIDIgMTIgMnptLTIgMTVsLTUtNSAxLjQxLTEuNDFMMTAgMTQuMTdsNy41OS03LjU5TDE5IDhsLTkgOXoiLz4KPC9zdmc+Cjwvc3ZnPgo=',
    priority: '高',
    status: '进行中',
    progress: 45,
    startTime: '2023-07-29 09:15',
    estimatedCompletion: '2023-07-29 11:00'
  },
  {
    taskName: 'C区5楼物资配送',
    taskId: 'TASK-2023058',
    robotName: '服务者-S3',
    robotAvatar: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMTIiIGN5PSIxMiIgcj0iMTIiIGZpbGw9IiNmNTllMGIiLz4KPHN2ZyB4PSI2IiB5PSI2IiB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0id2hpdGUiPgo8cGF0aCBkPSJNMTIgMkM2LjQ4IDIgMiA2LjQ4IDIgMTJzNC40OCAxMCAxMCAxMCAxMC00LjQ4IDEwLTEwUzE3LjUyIDIgMTIgMnptLTIgMTVsLTUtNSAxLjQxLTEuNDFMMTAgMTQuMTdsNy41OS03LjU5TDE5IDhsLTkgOXoiLz4KPC9zdmc+Cjwvc3ZnPgo=',
    priority: '低',
    status: '已暂停',
    progress: 25,
    startTime: '2023-07-29 10:00',
    estimatedCompletion: '2023-07-29 11:30'
  },
  {
    taskName: 'B区3楼故障修复',
    taskId: 'TASK-2023060',
    robotName: '运输者-T5',
    robotAvatar: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMTIiIGN5PSIxMiIgcj0iMTIiIGZpbGw9IiNlZjQ0NDQiLz4KPHN2ZyB4PSI2IiB5PSI2IiB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0id2hpdGUiPgo8cGF0aCBkPSJNMTIgMkM2LjQ4IDIgMiA2LjQ4IDIgMTJzNC40OCAxMCAxMCAxMCAxMC00LjQ4IDEwLTEwUzE3LjUyIDIgMTIgMnptLTIgMTVsLTUtNSAxLjQxLTEuNDFMMTAgMTQuMTdsNy41OS03LjU5TDE5IDhsLTkgOXoiLz4KPC9zdmc+Cjwvc3ZnPgo=',
    priority: '高',
    status: '已完成',
    progress: 100,
    startTime: '2023-07-28 16:30',
    estimatedCompletion: '2023-07-28 18:45'
  }
])

// 计算属性 - 过滤后的任务列表
const filteredTaskList = computed(() => {
  let filtered = taskList.value

  // 状态过滤
  if (selectedStatus.value) {
    filtered = filtered.filter(task => task.status === selectedStatus.value)
  }

  // 优先级过滤
  if (selectedPriority.value) {
    filtered = filtered.filter(task => task.priority === selectedPriority.value)
  }

  // 机器人过滤
  if (selectedRobot.value) {
    filtered = filtered.filter(task => task.robotName === selectedRobot.value)
  }

  return filtered
})

// 方法
const getPriorityType = (priority) => {
  switch (priority) {
    case '高': return 'danger'
    case '中': return 'primary'
    case '低': return 'info'
    default: return 'info'
  }
}

const getStatusType = (status) => {
  switch (status) {
    case '进行中': return 'success'
    case '已暂停': return 'warning'
    case '已完成': return 'info'
    default: return 'info'
  }
}

const getProgressColor = (percentage) => {
  if (percentage === 100) return '#10b981'
  if (percentage > 60) return '#10b981'
  if (percentage > 30) return '#f59e0b'
  return '#ef4444'
}

const handleSelectionChange = (selection) => {
  selectedTasks.value = selection
}

const handlePageChange = (page) => {
  currentPage.value = page
}

onMounted(() => {
  // 页面加载时的初始化逻辑
})
</script>

<style scoped>
.task-scheduling {
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

.export-btn {
  display: flex;
  align-items: center;
  gap: 8px;
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

.task-table {
  width: 100%;
}

.task-name-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.task-name {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.task-id {
  font-size: 12px;
  color: #9ca3af;
}

.robot-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.robot-avatar {
  flex-shrink: 0;
}

.robot-name {
  font-size: 14px;
  color: #374151;
}

.progress-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.task-progress {
  flex: 1;
  min-width: 80px;
}

.progress-text {
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
</style>