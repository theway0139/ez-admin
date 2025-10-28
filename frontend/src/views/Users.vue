<template>
  <div class="users-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">{{ $t('users.title') }}</h1>
      </div>
      <div class="header-right">
        <el-input
          v-model="searchText"
          :placeholder="$t('common.search') + $t('users.title') + '...'"
          class="search-input"
          clearable
          @change="loadUsers"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
    </div>

    <!-- 统计卡片区域 -->
    <div class="stats-section">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon total-users">
            <el-icon><User /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ userStats.total_users }}</div>
            <div class="stat-label">{{ $t('users.totalUsers') }}</div>
            <div class="stat-trend">{{ $t('users.growthRate') }} {{ userStats.growth_rate }}%</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon active-users">
            <el-icon><UserFilled /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ userStats.active_users }}</div>
            <div class="stat-label">{{ $t('users.activeUsers') }}</div>
            <div class="stat-trend">{{ Math.round((userStats.active_users / Math.max(userStats.total_users, 1)) * 100) }}% {{ $t('users.activeRate') }}</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon admin-users">
            <el-icon><User /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ userStats.admin_users }}</div>
            <div class="stat-label">{{ $t('users.adminUsers') }}</div>
            <div class="stat-trend">{{ Math.round((userStats.admin_users / Math.max(userStats.total_users, 1)) * 100) }}% {{ $t('users.adminRate') }}</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon locked-users">
            <el-icon><Lock /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ userStats.locked_users }}</div>
            <div class="stat-label">{{ $t('users.lockedUsers') }}</div>
            <div class="stat-trend">{{ $t('users.needAttention') }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 筛选器区域 -->
    <div class="filter-section">
      <div class="filter-row">
        <div class="filter-item">
          <label class="filter-label">{{ $t('users.userRole') }}</label>
          <el-select
            v-model="filters.role"
            :placeholder="$t('users.allRoles')"
            class="filter-input"
            clearable
            @change="loadUsers"
          >
            <el-option :label="$t('users.allRoles')" value="" />
            <el-option 
              v-for="role in roles" 
              :key="role.name" 
              :label="role.display_name" 
              :value="role.name" 
            />
          </el-select>
        </div>
        
        <div class="filter-item">
          <label class="filter-label">{{ $t('users.status') }}</label>
          <el-select
            v-model="filters.status"
            :placeholder="$t('users.allStatus')"
            class="filter-input"
            clearable
            @change="loadUsers"
          >
            <el-option :label="$t('users.allStatus')" value="" />
            <el-option :label="$t('users.active')" value="active" />
            <el-option :label="$t('users.inactive')" value="inactive" />
            <el-option :label="$t('users.locked')" value="locked" />
          </el-select>
        </div>
        
        <div class="filter-item">
          <label class="filter-label">{{ $t('users.department') }}</label>
          <el-select
            v-model="filters.department"
            :placeholder="$t('users.allDepartments')"
            class="filter-input"
            clearable
            @change="loadUsers"
          >
            <el-option :label="$t('users.allDepartments')" value="" />
            <el-option 
              v-for="dept in departments" 
              :key="dept.id" 
              :label="dept.name" 
              :value="dept.name" 
            />
          </el-select>
        </div>
      </div>
    </div>

    <!-- 用户信息表格 -->
    <div class="table-container">
      <el-table
        :data="users"
        stripe
        class="user-table"
        v-loading="loading"
      >
        <el-table-column prop="real_name" :label="$t('users.userInfo')" min-width="200">
          <template #default="{ row }">
            <div class="user-info">
              <div class="avatar-container">
                <el-avatar :size="40" :src="row.avatar">
                  <el-icon><User /></el-icon>
                </el-avatar>
              </div>
              <div class="user-details">
                <div class="user-name">{{ row.real_name }}</div>
                <div class="user-email">{{ row.email }}</div>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="role_display" :label="$t('users.role')" width="120">
          <template #default="{ row }">
            <el-tag 
              :type="getRoleTagType(row.role_display)"
              size="small"
            >
              {{ row.role_display }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="department_display" :label="$t('users.department')" width="150" />
        
        <el-table-column prop="status" :label="$t('users.status')" width="100">
          <template #default="{ row }">
            <el-tag 
              :type="getStatusTagType(row.status)"
              size="small"
            >
              {{ row.status_display }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="last_login" :label="$t('users.lastLogin')" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.last_login) }}
          </template>
        </el-table-column>

        <el-table-column :label="$t('users.actions')" width="320" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons-inline">
              <button
                class="modern-btn edit-btn"
                @click="editUser(row)"
                :title="$t('common.edit')"
              >
              <el-icon><Edit /></el-icon>
                <span>{{ $t('common.edit') }}</span>
              </button>
              
              <button
                class="modern-btn password-btn"
                @click="resetPassword(row)"
                :title="$t('users.resetPassword')"
              >
                <el-icon><Key /></el-icon>
                <span>{{ $t('users.resetPassword') }}</span>
              </button>
              
              <button
                :class="['modern-btn', row.is_active ? 'disable-btn' : 'enable-btn']"
                @click="toggleUserStatus(row)"
                :title="row.is_active ? $t('users.disable') : $t('users.enable')"
              >
                <el-icon v-if="row.is_active"><Lock /></el-icon>
                <el-icon v-else><Unlock /></el-icon>
                <span>{{ row.is_active ? $t('users.disable') : $t('users.enable') }}</span>
              </button>
              
              <button
                class="modern-btn delete-btn"
                @click="deleteUser(row)"
                :title="$t('common.delete')"
              >
              <el-icon><Delete /></el-icon>
                <span>{{ $t('common.delete') }}</span>
              </button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

      <!-- 分页 -->
    <div class="pagination-container">
      <div class="pagination-info">
        {{ $t('common.showing') }} {{ Math.min((currentPage - 1) * pageSize + 1, totalUsers) }} {{ $t('common.to') }} {{ Math.min(currentPage * pageSize, totalUsers) }} {{ $t('common.of') }} {{ totalUsers }} {{ $t('common.records') }}
      </div>
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
        :page-sizes="[6, 10, 20, 50]"
          :total="totalUsers"
        layout="sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>

    <!-- 编辑用户对话框 -->
    <el-dialog
      v-model="showEditDialog"
      :title="editingUser ? $t('common.edit') + $t('users.title') : $t('common.add') + $t('users.title')"
      width="600px"
      center
    >
      <el-form :model="userForm" label-width="120px">
        <el-form-item :label="$t('users.username')">
          <el-input v-model="userForm.username" :disabled="!!editingUser" />
        </el-form-item>
        
        <el-form-item :label="$t('users.realName')">
          <el-input v-model="userForm.real_name" />
        </el-form-item>
        
        <el-form-item :label="$t('users.email')">
          <el-input v-model="userForm.email" type="email" />
        </el-form-item>
        
        <el-form-item :label="$t('users.phone')">
          <el-input v-model="userForm.phone" />
        </el-form-item>
        
        <el-form-item :label="$t('users.role')">
          <el-select v-model="userForm.role_id" :placeholder="$t('common.select') + $t('users.role')" class="w-full">
            <el-option 
              v-for="role in roles" 
              :key="role.id" 
              :label="role.display_name" 
              :value="role.id" 
            />
          </el-select>
        </el-form-item>
        
        <el-form-item :label="$t('users.department')">
          <el-select v-model="userForm.department_id" :placeholder="$t('common.select') + $t('users.department')" class="w-full">
            <el-option 
              v-for="dept in departments" 
              :key="dept.id" 
              :label="dept.name" 
              :value="dept.id" 
            />
          </el-select>
        </el-form-item>
        
        <el-form-item :label="$t('users.status')">
          <el-select v-model="userForm.status" class="w-full">
            <el-option :label="$t('users.active')" value="active" />
            <el-option :label="$t('users.inactive')" value="inactive" />
            <el-option :label="$t('users.locked')" value="locked" />
          </el-select>
        </el-form-item>
        
        <el-form-item v-if="!editingUser" :label="$t('users.password')">
          <el-input v-model="userForm.password" type="password" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showEditDialog = false">{{ $t('common.cancel') }}</el-button>
        <el-button 
          type="primary" 
          @click="saveUser"
          :loading="saving"
        >
          {{ $t('common.save') }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 重置密码对话框 -->
    <el-dialog
      v-model="showPasswordDialog"
      :title="$t('users.resetPassword')"
      width="400px"
      center
    >
      <el-form :model="passwordForm" label-width="100px">
        <el-form-item :label="$t('users.newPassword')">
          <el-input v-model="passwordForm.new_password" type="password" />
        </el-form-item>
        
        <el-form-item :label="$t('users.confirmPassword')">
          <el-input v-model="passwordForm.confirm_password" type="password" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showPasswordDialog = false">{{ $t('common.cancel') }}</el-button>
        <el-button 
          type="primary" 
          @click="confirmResetPassword"
          :loading="resettingPassword"
        >
          {{ $t('common.confirm') + $t('common.reset') }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useI18n } from 'vue-i18n'
import {
  Search,
  User,
  UserFilled,
  Lock,
  Unlock,
  Edit,
  Key,
  Delete
} from '@element-plus/icons-vue'
import axios from 'axios'

// API基础URL
const API_BASE = 'http://172.16.160.100:8003/api2'

// 国际化
const { t } = useI18n()

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const resettingPassword = ref(false)
const searchText = ref('')
const currentPage = ref(1)
const pageSize = ref(6)
const totalUsers = ref(0)

// 数据列表
const users = ref([])
const roles = ref([])
const departments = ref([])

// 统计数据
const userStats = ref({
  total_users: 0,
  active_users: 0,
  admin_users: 0,
  locked_users: 0,
  growth_rate: 0
})

// 筛选器
const filters = reactive({
  role: '',
  status: '',
  department: ''
})

// 对话框控制
const showEditDialog = ref(false)
const showPasswordDialog = ref(false)
const editingUser = ref(null)
const resetPasswordUser = ref(null)

// 表单数据
const userForm = reactive({
  username: '',
  real_name: '',
  email: '',
  phone: '',
  role_id: null,
  department_id: null,
  status: 'active',
  password: ''
})

const passwordForm = reactive({
  new_password: '',
  confirm_password: ''
})

// 模拟用户数据
const mockUsers = [
  {
    id: 1,
    real_name: '张三',
    email: 'zhangsan@example.com',
    username: 'zhangsan',
    phone: '13800138001',
    role_display: '管理员',
    department_display: '管理部',
    status: 'active',
    status_display: '活跃',
    last_login: '2024-01-15T14:30:00',
    is_active: true,
    avatar: null
  },
  {
    id: 2,
    real_name: '李四',
    email: 'lisi@example.com',
    username: 'lisi',
    phone: '13800138002',
    role_display: '编辑员',
    department_display: '运维部',
    status: 'active',
    status_display: '活跃',
    last_login: '2024-01-15T13:45:00',
    is_active: true,
    avatar: null
  },
  {
    id: 3,
    real_name: '王五',
    email: 'wangwu@example.com',
    username: 'wangwu',
    phone: '13800138003',
    role_display: '观察者',
    department_display: '开发部',
    status: 'active',
    status_display: '活跃',
    last_login: '2024-01-15T11:20:00',
    is_active: true,
    avatar: null
  },
  {
    id: 4,
    real_name: '赵六',
    email: 'zhaoliu@example.com',
    username: 'zhaoliu',
    phone: '13800138004',
    role_display: '审计员',
    department_display: '安全部',
    status: 'inactive',
    status_display: '未激活',
    last_login: '2024-01-14T16:15:00',
    is_active: false,
    avatar: null
  },
  {
    id: 5,
    real_name: '钱七',
    email: 'qianqi@example.com',
    username: 'qianqi',
    phone: '13800138005',
    role_display: '编辑员',
    department_display: '运维部',
    status: 'locked',
    status_display: '已锁定',
    last_login: '2024-01-13T09:30:00',
    is_active: false,
    avatar: null
  },
  {
    id: 6,
    real_name: '孙八',
    email: 'sunba@example.com',
    username: 'sunba',
    phone: '13800138006',
    role_display: '观察者',
    department_display: '开发部',
    status: 'locked',
    status_display: '已禁用',
    last_login: '2024-01-10T15:40:00',
    is_active: false,
    avatar: null
  }
]

// 方法
const formatDateTime = (dateTimeStr) => {
  if (!dateTimeStr) return '-'
  const date = new Date(dateTimeStr)
  return date.toLocaleString('zh-CN')
}

const getRoleTagType = (role) => {
  const roleMap = {
    '管理员': 'danger',
    '编辑员': 'warning',
    '观察者': 'info',
    '审计员': 'success'
  }
  return roleMap[role] || ''
}

const getStatusTagType = (status) => {
  const statusMap = {
    'active': 'success',
    'inactive': 'warning',
    'locked': 'danger'
  }
  return statusMap[status] || ''
}

// 加载用户统计
const loadUserStats = async () => {
  try {
    const response = await axios.get(`${API_BASE}/users/stats`)
    userStats.value = response.data
    console.log('用户统计数据:', response.data)
  } catch (error) {
    console.error('加载用户统计失败:', error)
    ElMessage.error('加载用户统计失败')
  }
}

// 加载用户列表
const loadUsers = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    if (filters.role) params.role = filters.role
    if (filters.status) params.status = filters.status
    if (filters.department) params.department = filters.department
    if (searchText.value) params.search = searchText.value
    
    const response = await axios.get(`${API_BASE}/users`, { params })
    
    if (response.data.data) {
      // 新的分页响应格式
      users.value = response.data.data
      totalUsers.value = response.data.total
      console.log('用户列表数据:', response.data)
    } else {
      // 旧的响应格式（兼容性）
      users.value = response.data
      totalUsers.value = response.data.length
    }
  } catch (error) {
    console.error('加载用户列表失败:', error)
    ElMessage.error('加载用户列表失败')
    // 如果API失败，使用模拟数据作为后备
    users.value = mockUsers
    totalUsers.value = mockUsers.length
  } finally {
    loading.value = false
  }
}

// 加载角色列表
const loadRoles = async () => {
  try {
    const response = await axios.get(`${API_BASE}/roles`)
    roles.value = response.data
    console.log('角色列表数据:', response.data)
  } catch (error) {
    console.error('加载角色列表失败:', error)
    // 使用后备数据
    roles.value = [
      { id: 1, name: 'admin', display_name: '管理员' },
      { id: 2, name: 'editor', display_name: '编辑员' },
      { id: 3, name: 'viewer', display_name: '观察者' },
      { id: 4, name: 'auditor', display_name: '审计员' }
    ]
  }
}

// 加载部门列表
const loadDepartments = async () => {
  try {
    const response = await axios.get(`${API_BASE}/departments`)
    departments.value = response.data
    console.log('部门列表数据:', response.data)
  } catch (error) {
    console.error('加载部门列表失败:', error)
    // 使用后备数据
    departments.value = [
      { id: 1, name: '管理部' },
      { id: 2, name: '运维部' },
      { id: 3, name: '开发部' },
      { id: 4, name: '安全部' }
    ]
  }
}

// 编辑用户
const editUser = (user) => {
  editingUser.value = user
  Object.assign(userForm, {
    username: user.username,
    real_name: user.real_name,
    email: user.email,
    phone: user.phone,
    role_id: null,
    department_id: null,
    status: user.status,
    password: ''
  })
  showEditDialog.value = true
}

// 保存用户
const saveUser = async () => {
  saving.value = true
  try {
    if (editingUser.value) {
      // 更新用户
      await axios.put(`${API_BASE}/users/${editingUser.value.id}`, userForm)
      ElMessage.success('用户更新成功')
    } else {
      // 创建用户
      await axios.post(`${API_BASE}/users`, userForm)
      ElMessage.success('用户创建成功')
    }
    
    showEditDialog.value = false
    loadUsers()
    loadUserStats()
  } catch (error) {
    console.error('保存用户失败:', error)
    ElMessage.error('保存用户失败')
  } finally {
    saving.value = false
  }
}

// 重置密码
const resetPassword = (user) => {
  resetPasswordUser.value = user
  passwordForm.new_password = ''
  passwordForm.confirm_password = ''
  showPasswordDialog.value = true
}

// 确认重置密码
const confirmResetPassword = async () => {
  if (passwordForm.new_password !== passwordForm.confirm_password) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }
  
  if (passwordForm.new_password.length < 6) {
    ElMessage.warning('密码长度不能少于6位')
    return
  }
  
  resettingPassword.value = true
  try {
    await axios.post(`${API_BASE}/users/${resetPasswordUser.value.id}/reset-password`, {
      new_password: passwordForm.new_password
    })
    ElMessage.success('密码重置成功')
    showPasswordDialog.value = false
  } catch (error) {
    console.error('重置密码失败:', error)
    ElMessage.error('重置密码失败')
  } finally {
    resettingPassword.value = false
  }
}

// 切换用户状态
const toggleUserStatus = async (user) => {
  try {
    const action = user.is_active ? '禁用' : '启用'
    await ElMessageBox.confirm(
      `确定要${action}用户 "${user.real_name}" 吗？`,
      `确认${action}`,
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await axios.post(`${API_BASE}/users/${user.id}/toggle-status`)
    ElMessage.success(`${action}成功`)
    loadUsers()
    loadUserStats()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('切换用户状态失败:', error)
      ElMessage.error('操作失败')
    }
  }
}

// 删除用户
const deleteUser = async (user) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${user.real_name}" 吗？此操作不可恢复！`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await axios.delete(`${API_BASE}/users/${user.id}`)
    ElMessage.success('删除成功')
    loadUsers()
    loadUserStats()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除用户失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  loadUsers()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  loadUsers()
}

// 生命周期
onMounted(() => {
  loadUserStats()
  loadUsers()
  loadRoles()
  loadDepartments()
})
</script>

<style scoped>
.users-container {
  padding: 24px;
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

/* 统计卡片区域 */
.stats-section {
  margin-bottom: 24px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.stat-icon.total-users {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.active-users {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.admin-users {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon.locked-users {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin: 4px 0;
}

.stat-trend {
  font-size: 12px;
  color: #67c23a;
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

.user-table {
  width: 100%;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar-container {
  flex-shrink: 0;
}

.user-details {
  flex: 1;
}

.user-name {
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.user-email {
  font-size: 12px;
  color: #909399;
}

/* 旧版操作按钮样式 */
.action-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.action-buttons .el-button {
  padding: 4px 8px;
  font-size: 12px;
}

/* 现代化内联操作按钮样式 - 完全匹配设计图 */
.action-buttons-inline {
  display: flex;
  gap: 6px;
  align-items: center;
  justify-content: flex-start;
  flex-wrap: nowrap;
  overflow: hidden;
}

.modern-btn {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  padding: 3px 6px;
  border: none;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  min-height: 26px;
  line-height: 1;
  background: transparent;
  flex-shrink: 0;
}

.modern-btn:hover {
  opacity: 0.7;
}

.modern-btn:active {
  opacity: 0.9;
}

.modern-btn .el-icon {
  font-size: 12px;
}

.modern-btn span {
  font-size: 11px;
  font-weight: 500;
}

/* 编辑按钮 - 蓝色图标和文字 */
.edit-btn {
  color: #409eff;
}

.edit-btn .el-icon {
  color: #409eff;
}

/* 重置密码按钮 - 绿色图标和文字 */
.password-btn {
  color: #67c23a;
}

.password-btn .el-icon {
  color: #67c23a;
}

/* 禁用按钮 - 橙色图标和文字 */
.disable-btn {
  color: #e6a23c;
}

.disable-btn .el-icon {
  color: #e6a23c;
}

/* 启用按钮 - 绿色图标和文字 */
.enable-btn {
  color: #67c23a;
}

.enable-btn .el-icon {
  color: #67c23a;
}

/* 删除按钮 - 红色图标和文字 */
.delete-btn {
  color: #f56c6c;
}

.delete-btn .el-icon {
  color: #f56c6c;
}

/* 分页 */
.pagination-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.pagination-info {
  font-size: 14px;
  color: #606266;
}

.pagination-controls {
  display: flex;
  gap: 8px;
}

/* 工具栏样式 */
.w-full {
  width: 100%;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .users-container {
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
  
  .stats-grid {
    grid-template-columns: 1fr;
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
  
  .action-buttons-inline {
    flex-direction: column;
    gap: 3px;
    align-items: stretch;
  }
  
  .modern-btn {
    justify-content: center;
    min-width: 70px;
    padding: 6px 8px;
  }
  
  .pagination-container {
    flex-direction: column;
    gap: 16px;
  }
}
</style>