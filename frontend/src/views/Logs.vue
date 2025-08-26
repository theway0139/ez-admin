<template>
  <div class="logs-container">
    <h1 class="page-title">日志信息</h1>
    
    <div class="filter-bar">
      <el-select v-model="typeFilter" placeholder="全部类型" clearable style="width: 120px;">
        <el-option label="全部类型" value="" />
        <el-option label="报警" value="报警" />
        <el-option label="错误" value="错误" />
        <el-option label="信息" value="信息" />
      </el-select>
      
      <el-select v-model="statusFilter" placeholder="全部状态" clearable style="width: 120px;">
        <el-option label="全部状态" value="" />
        <el-option label="已处理" value="已处理" />
        <el-option label="未处理" value="未处理" />
      </el-select>
      
      <el-date-picker
        v-model="dateFilter"
        type="date"
        placeholder="选择日期"
        format="YYYY/MM/DD"
        value-format="YYYY/MM/DD"
        clearable
      />
      
      <el-input
        v-model="searchQuery"
        placeholder="搜索日志..."
        clearable
        class="search-input"
      />
      
      <el-button type="primary" @click="handleSearch">导出</el-button>
    </div>
    
    <el-table :data="filteredLogs" style="width: 100%" border>
      <el-table-column prop="time" label="时间" width="180" />
      <el-table-column prop="type" label="类型" width="120" />
      <el-table-column prop="content" label="内容">
        <template #default="scope">
          <div>
            <div>{{ scope.row.content }}</div>
            <div class="content-detail">{{ scope.row.detail }}</div>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="level" label="等级" width="100">
        <template #default="scope">
          <el-tag :type="getTagType(scope.row.level)">{{ scope.row.level }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.status === '未处理' ? 'danger' : 'info'">
            {{ scope.row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180">
        <template #default="scope">
          <el-button type="primary" size="small" @click="viewLog(scope.row)">查看</el-button>
          <el-button type="danger" size="small" @click="handleLog(scope.row)">处理</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <div class="pagination-container">
      <span>共 {{ totalLogs }} 条记录</span>
      <el-pagination
        background
        layout="prev, pager, next"
        :total="totalLogs"
        :page-size="pageSize"
        :current-page="currentPage"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 筛选条件
const typeFilter = ref('')
const statusFilter = ref('')
const dateFilter = ref('')
const searchQuery = ref('')

// 分页
const currentPage = ref(1)
const pageSize = ref(10)
const totalLogs = ref(3)

// 模拟日志数据
const logs = ref([
  {
    id: 1,
    time: '8/25/2025, 4:50:02 PM',
    type: '报警',
    content: '发现异常行为',
    detail: '校门口',
    level: '警告',
    status: '未处理'
  },
  {
    id: 2,
    time: '8/25/2025, 4:49:54 PM',
    type: '报警',
    content: '发现异常行为',
    detail: '校门口',
    level: '警告',
    status: '未处理'
  },
  {
    id: 3,
    time: '8/25/2025, 4:47:57 PM',
    type: '报警',
    content: '发现异常行为',
    detail: '校门口',
    level: '警告',
    status: '未处理'
  }
])

// 过滤日志
const filteredLogs = computed(() => {
  let result = logs.value

  if (typeFilter.value) {
    result = result.filter(log => log.type === typeFilter.value)
  }
  
  if (statusFilter.value) {
    result = result.filter(log => log.status === statusFilter.value)
  }
  
  if (dateFilter.value) {
    const filterDate = new Date(dateFilter.value).toLocaleDateString()
    result = result.filter(log => {
      const logDate = new Date(log.time).toLocaleDateString()
      return logDate === filterDate
    })
  }
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(log => 
      log.content.toLowerCase().includes(query) || 
      log.detail.toLowerCase().includes(query)
    )
  }
  
  return result
})

// 获取标签类型
const getTagType = (level) => {
  switch (level) {
    case '警告':
      return 'warning'
    case '错误':
      return 'danger'
    case '信息':
      return 'info'
    default:
      return ''
  }
}

// 处理搜索
const handleSearch = () => {
  ElMessage.success('导出功能开发中...')
}

// 查看日志
const viewLog = (log) => {
  ElMessageBox.alert(`日志ID: ${log.id}\n时间: ${log.time}\n内容: ${log.content}\n位置: ${log.detail}`, '日志详情', {
    confirmButtonText: '确定'
  })
}

// 处理日志
const handleLog = (log) => {
  ElMessageBox.confirm('确定将此日志标记为已处理?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    log.status = '已处理'
    ElMessage.success('日志已处理')
  }).catch(() => {})
}

// 处理分页
const handlePageChange = (page) => {
  currentPage.value = page
}

// 生命周期
onMounted(() => {
  // 这里可以添加从API获取日志数据的逻辑
})
</script>

<style scoped>
.logs-container {
  padding: 20px;
}

.page-title {
  margin-bottom: 20px;
  font-size: 24px;
  color: #333;
}

.filter-bar {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.search-input {
  width: 250px;
}

.content-detail {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.pagination-container span {
  margin-right: 15px;
  color: #606266;
}
</style>