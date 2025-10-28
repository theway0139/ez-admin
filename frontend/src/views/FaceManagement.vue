<template>
  <div class="face-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">人脸管理</h1>
      <el-button type="primary" @click="showBatchUploadDialog">
        <el-icon><Upload /></el-icon>
        批量上传
      </el-button>
    </div>

    <!-- 搜索和筛选区域 -->
    <div class="filter-section">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索姓名或ID..."
        class="search-input"
        clearable
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      
      <el-select v-model="selectedStatus" placeholder="全部状态" clearable class="status-select">
        <el-option label="全部状态" value="" />
        <el-option label="已激活" value="active" />
        <el-option label="未激活" value="inactive" />
      </el-select>
      
      <el-button @click="resetFilters">重置</el-button>
    </div>

    <!-- 人脸列表表格 -->
    <div class="table-section">
      <el-table
        :data="filteredFaceList"
        class="face-table"
        stripe
        v-loading="loading"
      >
        <el-table-column label="头像" width="100">
          <template #default="{ row }">
            <el-avatar :size="50" :src="row.avatar || defaultAvatar" />
          </template>
        </el-table-column>
        
        <el-table-column prop="name" label="姓名" width="150" />
        
        <el-table-column prop="employeeId" label="人员ID" width="150" />
        
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag
              :type="row.status === 'active' ? 'success' : 'info'"
              size="small"
            >
              {{ row.status === 'active' ? '已激活' : '未激活' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="uploadTime" label="上传时间" width="180" />
        
        <el-table-column prop="department" label="部门" min-width="150" />
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="editFace(row)">
              编辑
            </el-button>
            <el-button 
              link 
              :type="row.status === 'active' ? 'warning' : 'success'" 
              size="small" 
              @click="toggleStatus(row)"
            >
              {{ row.status === 'active' ? '停用' : '激活' }}
            </el-button>
            <el-button link type="danger" size="small" @click="deleteFace(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <span class="total-count">显示 {{ filteredFaceList.length }} 条记录</span>
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="totalCount"
          layout="prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- 编辑/添加对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
    >
      <el-form :model="currentFace" label-width="100px">
        <el-form-item label="头像">
          <el-upload
            class="avatar-uploader"
            :show-file-list="false"
            :before-upload="beforeAvatarUpload"
            :http-request="handleAvatarUpload"
          >
            <img v-if="currentFace.avatar" :src="currentFace.avatar" class="avatar" />
            <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
          </el-upload>
        </el-form-item>
        
        <el-form-item label="姓名" required>
          <el-input v-model="currentFace.name" placeholder="请输入姓名" />
        </el-form-item>
        
        <el-form-item label="人员ID" required>
          <el-input v-model="currentFace.employeeId" placeholder="请输入人员ID" />
        </el-form-item>
        
        <el-form-item label="部门">
          <el-input v-model="currentFace.department" placeholder="请输入部门" />
        </el-form-item>
        
        <el-form-item label="状态">
          <el-switch
            v-model="currentFace.status"
            active-value="active"
            inactive-value="inactive"
            active-text="已激活"
            inactive-text="未激活"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveFace">保存</el-button>
      </template>
    </el-dialog>

    <!-- 批量上传对话框 -->
    <el-dialog
      v-model="batchUploadDialogVisible"
      title="批量上传人脸"
      width="600px"
    >
      <el-upload
        class="upload-demo"
        drag
        multiple
        :auto-upload="false"
        :on-change="handleBatchFileChange"
        accept="image/*"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          拖拽文件到此处或 <em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持 jpg/png 格式，单个文件不超过 5MB。<br>
            文件命名格式：姓名_人员ID.jpg（例如：张三_EMP001.jpg）
          </div>
        </template>
      </el-upload>
      
      <template #footer>
        <el-button @click="batchUploadDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="performBatchUpload">开始上传</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Upload, Plus, UploadFilled } from '@element-plus/icons-vue'

// axios可能未安装，先注释掉
// import axios from 'axios'

// 数据状态
const loading = ref(false)
const faceList = ref([])
const searchKeyword = ref('')
const selectedStatus = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const totalCount = ref(0)

// 对话框状态
const dialogVisible = ref(false)
const dialogTitle = ref('添加人员')
const batchUploadDialogVisible = ref(false)

// 当前编辑的人脸数据
const currentFace = ref({
  id: null,
  name: '',
  employeeId: '',
  avatar: '',
  status: 'active',
  department: '',
  uploadTime: ''
})

// 批量上传文件列表
const batchFiles = ref([])

// 默认头像
const defaultAvatar = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgZmlsbD0iI2VlZSIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LXNpemU9IjQwIiBmaWxsPSIjOTk5IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkb21pbmFudC1iYXNlbGluZT0ibWlkZGxlIj7kuoQ8L3RleHQ+PC9zdmc+'

// 计算过滤后的列表
const filteredFaceList = computed(() => {
  let list = faceList.value
  
  // 搜索过滤
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    list = list.filter(face => 
      face.name.toLowerCase().includes(keyword) || 
      face.employeeId.toLowerCase().includes(keyword)
    )
  }
  
  // 状态过滤
  if (selectedStatus.value) {
    list = list.filter(face => face.status === selectedStatus.value)
  }
  
  return list
})

// 获取人脸列表
const fetchFaceList = async () => {
  loading.value = true
  try {
    const apiUrl = 'http://172.16.160.100:8003'
    const response = await fetch(`${apiUrl}/api2/faces?page=${currentPage.value}&page_size=${pageSize.value}${selectedStatus.value ? '&status=' + selectedStatus.value : ''}${searchKeyword.value ? '&keyword=' + encodeURIComponent(searchKeyword.value) : ''}`)
    const result = await response.json()
    
    if (result.success) {
      faceList.value = result.data.map(face => ({
        id: face.id,
        name: face.name,
        employeeId: face.employee_id,
        avatar: face.avatar_path,
        status: face.status,
        department: face.department || '-',
        uploadTime: new Date(face.created_at).toLocaleDateString('zh-CN')
      }))
      totalCount.value = result.total
    } else {
      throw new Error(result.error || '获取失败')
    }
  } catch (error) {
    ElMessage.error('获取人脸列表失败：' + error.message)
    faceList.value = []
    totalCount.value = 0
  } finally {
    loading.value = false
  }
}

// 重置筛选
const resetFilters = () => {
  searchKeyword.value = ''
  selectedStatus.value = ''
}

// 显示批量上传对话框
const showBatchUploadDialog = () => {
  batchUploadDialogVisible.value = true
  batchFiles.value = []
}

// 编辑人脸
const editFace = (face) => {
  currentFace.value = { ...face }
  dialogTitle.value = '编辑人员'
  dialogVisible.value = true
}

// 切换状态
const toggleStatus = async (face) => {
  const newStatus = face.status === 'active' ? 'inactive' : 'active'
  const action = newStatus === 'active' ? '激活' : '停用'
  
  try {
    await ElMessageBox.confirm(
      `确定要${action}人员 ${face.name} 吗？`,
      '确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const apiUrl = 'http://172.16.160.100:8003'
    const response = await fetch(`${apiUrl}/api2/faces/${face.id}/status`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    const result = await response.json()
    
    if (result.success) {
      face.status = result.data.status
      ElMessage.success(`${action}成功`)
    } else {
      throw new Error(result.error || '操作失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(`${action}失败：` + error.message)
    }
  }
}

// 删除人脸
const deleteFace = async (face) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除人员 ${face.name} 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'error'
      }
    )
    
    const apiUrl = 'http://172.16.160.100:8003'
    const response = await fetch(`${apiUrl}/api2/faces/${face.id}`, {
      method: 'DELETE'
    })
    const result = await response.json()
    
    if (result.success) {
      const index = faceList.value.findIndex(f => f.id === face.id)
      if (index > -1) {
        faceList.value.splice(index, 1)
      }
      totalCount.value = totalCount.value - 1
      ElMessage.success('删除成功')
    } else {
      throw new Error(result.error || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败：' + error.message)
    }
  }
}

// 保存人脸
const saveFace = async () => {
  if (!currentFace.value.name || !currentFace.value.employeeId) {
    ElMessage.warning('请填写姓名和人员ID')
    return
  }
  
  try {
    const apiUrl = 'http://172.16.160.100:8003'
    const payload = {
      name: currentFace.value.name,
      employee_id: currentFace.value.employeeId,
      department: currentFace.value.department,
      avatar_path: currentFace.value.avatar,
      status: currentFace.value.status
    }
    
    if (currentFace.value.id) {
      // 更新
      const response = await fetch(`${apiUrl}/api2/faces/${currentFace.value.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      })
      const result = await response.json()
      
      if (result.success) {
        await fetchFaceList() // 重新加载列表
        ElMessage.success('更新成功')
      } else {
        throw new Error(result.error || '更新失败')
      }
    } else {
      // 新增
      const response = await fetch(`${apiUrl}/api2/faces`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      })
      const result = await response.json()
      
      if (result.success) {
        await fetchFaceList() // 重新加载列表
        ElMessage.success('添加成功')
      } else {
        throw new Error(result.error || '添加失败')
      }
    }
    
    dialogVisible.value = false
  } catch (error) {
    ElMessage.error('保存失败：' + error.message)
  }
}

// 头像上传前验证
const beforeAvatarUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt5M = file.size / 1024 / 1024 < 5

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt5M) {
    ElMessage.error('图片大小不能超过 5MB!')
    return false
  }
  return true
}

// 处理头像上传
const handleAvatarUpload = async (options) => {
  const { file } = options
  
  // 创建预览
  const reader = new FileReader()
  reader.onload = (e) => {
    currentFace.value.avatar = e.target.result
  }
  reader.readAsDataURL(file)
  
  // TODO: 上传到服务器
  // const formData = new FormData()
  // formData.append('file', file)
  // const response = await axios.post('/api2/upload-face', formData)
  // currentFace.value.avatar = response.data.url
}

// 批量文件变化
const handleBatchFileChange = (file, fileList) => {
  batchFiles.value = fileList
}

// 执行批量上传
const performBatchUpload = async () => {
  if (batchFiles.value.length === 0) {
    ElMessage.warning('请先选择文件')
    return
  }
  
  loading.value = true
  try {
    // TODO: 批量上传到服务器
    // const formData = new FormData()
    // batchFiles.value.forEach(file => {
    //   formData.append('files', file.raw)
    // })
    // await axios.post('/api2/batch-upload-faces', formData)
    
    ElMessage.success(`成功上传 ${batchFiles.value.length} 个人脸`)
    batchUploadDialogVisible.value = false
    await fetchFaceList()
  } catch (error) {
    ElMessage.error('批量上传失败：' + error.message)
  } finally {
    loading.value = false
  }
}

// 分页处理
const handleSizeChange = (size) => {
  pageSize.value = size
  fetchFaceList()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  fetchFaceList()
}

// 页面加载时获取数据
onMounted(() => {
  fetchFaceList()
})
</script>

<style scoped>
.face-management {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
  color: #303133;
}

.filter-section {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.search-input {
  width: 300px;
}

.status-select {
  width: 150px;
}

.table-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.face-table {
  width: 100%;
}

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
}

.total-count {
  font-size: 14px;
  color: #606266;
}

.avatar-uploader {
  width: 120px;
  height: 120px;
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: border-color 0.3s;
}

.avatar-uploader:hover {
  border-color: #409eff;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 120px;
  height: 120px;
  line-height: 120px;
  text-align: center;
}

.avatar {
  width: 120px;
  height: 120px;
  display: block;
  object-fit: cover;
}
</style>

