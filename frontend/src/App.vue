<template>
  <div id="app" :class="{ 'dark-mode': isDarkMode }">
    <!-- 侧边栏 -->
    <aside 
      class="sidebar" 
      :class="{ 
        'collapsed': isCollapsed,
        'mobile-drawer': isMobile && !isCollapsed
      }"
    >
      <div class="sidebar-header">
        <img src="/vite.svg" alt="Logo" class="logo" />
        <span v-show="!isCollapsed" class="title">管理系统</span>
      </div>
      
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapsed"
        :unique-opened="true"
        router
        class="sidebar-menu"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataBoard /></el-icon>
          <template #title>仪表盘</template>
        </el-menu-item>
        
        <el-menu-item index="/users">
          <el-icon><User /></el-icon>
          <template #title>用户管理</template>
        </el-menu-item>
        
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <template #title>系统设置</template>
        </el-menu-item>
      </el-menu>
    </aside>

    <!-- 主内容区域 -->
    <div class="main-container">
      <!-- 顶部导航 -->
      <header class="header">
        <div class="header-left">
          <el-button
            type="text"
            class="hamburger-btn"
            @click="toggleSidebar"
          >
            <el-icon><Expand /></el-icon>
          </el-button>
          
          <el-breadcrumb separator="/">
            <el-breadcrumb-item v-for="item in breadcrumbs" :key="item.path" :to="item.path">
              {{ item.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <div class="header-right">
          <el-button
            type="text"
            class="action-btn"
            @click="toggleFullscreen"
          >
            <el-icon><FullScreen /></el-icon>
          </el-button>
          
          <el-button
            type="text"
            class="action-btn"
            @click="toggleDarkMode"
          >
            <el-icon><Moon v-if="!isDarkMode" /><Sunny v-else /></el-icon>
          </el-button>
          
          <el-badge :value="3" class="notification-badge">
            <el-button
              type="text"
              class="action-btn"
              @click="showNotifications"
            >
              <el-icon><Bell /></el-icon>
            </el-button>
          </el-badge>
          
          <el-dropdown @command="handleUserCommand">
            <div class="user-avatar">
              <el-avatar :size="32" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
              <span class="username">管理员</span>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人资料</el-dropdown-item>
                <el-dropdown-item command="settings">设置</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <!-- 主内容 -->
      <main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>

    <!-- 移动端遮罩 -->
    <div 
      v-if="isMobile && !isCollapsed" 
      class="mobile-overlay"
      @click="closeMobileSidebar"
    ></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  DataBoard,
  User,
  Setting,
  Expand,
  FullScreen,
  Moon,
  Sunny,
  Bell,
  ArrowDown
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// 响应式状态
const isCollapsed = ref(false)
const isDarkMode = ref(false)
const isMobile = ref(false)

// 路由相关
const route = useRoute()
const router = useRouter()

// 计算属性
const activeMenu = computed(() => route.path)

const breadcrumbs = computed(() => {
  const pathMap: Record<string, string> = {
    '/dashboard': '仪表盘',
    '/users': '用户管理',
    '/settings': '系统设置'
  }
  
  const currentPath = route.path
  if (pathMap[currentPath]) {
    return [{ path: currentPath, title: pathMap[currentPath] }]
  }
  return []
})

// 方法
const toggleSidebar = () => {
  if (isMobile.value) {
    isCollapsed.value = !isCollapsed.value
  } else {
    isCollapsed.value = !isCollapsed.value
  }
}

const toggleDarkMode = () => {
  isDarkMode.value = !isDarkMode.value
  document.documentElement.classList.toggle('dark-mode', isDarkMode.value)
  localStorage.setItem('darkMode', isDarkMode.value.toString())
}

const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
  } else {
    document.exitFullscreen()
  }
}

const showNotifications = () => {
  ElMessage.info('通知功能开发中...')
}

const handleUserCommand = (command: string) => {
  switch (command) {
    case 'profile':
      ElMessage.info('个人资料页面开发中...')
      break
    case 'settings':
      router.push('/settings')
      break
    case 'logout':
      ElMessage.success('已退出登录')
      break
  }
}

const closeMobileSidebar = () => {
  if (isMobile.value) {
    isCollapsed.value = true
  }
}

// 响应式处理
const handleResize = () => {
  isMobile.value = window.innerWidth < 768
  if (isMobile.value) {
    isCollapsed.value = true
  }
}

// 生命周期
onMounted(() => {
  // 恢复暗黑模式设置
  const savedDarkMode = localStorage.getItem('darkMode')
  if (savedDarkMode) {
    isDarkMode.value = savedDarkMode === 'true'
    document.documentElement.classList.toggle('dark-mode', isDarkMode.value)
  }
  
  // 初始化响应式
  handleResize()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

// 监听路由变化，移动端自动关闭侧边栏
watch(route, () => {
  if (isMobile.value) {
    isCollapsed.value = true
  }
})
</script>

<style scoped>
/* CSS 变量定义 */
:root {
  --primary-color: #409eff;
  --sidebar-bg: #304156;
  --header-bg: #ffffff;
  --text-color: #303133;
  --border-color: #e4e7ed;
  --hover-bg: #f5f7fa;
}

.dark-mode {
  --primary-color: #409eff;
  --sidebar-bg: #1f2937;
  --header-bg: #374151;
  --text-color: #f9fafb;
  --border-color: #4b5563;
  --hover-bg: #4b5563;
}

#app {
  display: flex;
  height: 100vh;
  width: 100vw;
  background-color: #f0f2f5;
  transition: all 0.3s ease;
  overflow: hidden;
}

.dark-mode #app {
  background-color: #111827;
}

/* 侧边栏样式 */
.sidebar {
  width: 240px;
  height: 100vh;
  background-color: var(--sidebar-bg);
  transition: all 0.3s ease;
  z-index: 1000;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
  overflow-y: auto;
}

.sidebar.collapsed {
  width: 64px;
}

.sidebar-header {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
}

.logo {
  width: 32px;
  height: 32px;
  margin-right: 12px;
}

.title {
  color: var(--text-color);
  font-size: 18px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
}

.sidebar-menu {
  border: none;
  background-color: transparent;
  flex: 1;
}

.sidebar-menu .el-menu-item {
  color: var(--text-color);
  border-bottom: 1px solid var(--border-color);
}

.sidebar-menu .el-menu-item:hover {
  background-color: var(--hover-bg);
}

.sidebar-menu .el-menu-item.is-active {
  background-color: var(--primary-color);
  color: #ffffff;
}

/* 主容器样式 */
.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
  height: 100vh;
}

/* 顶部导航样式 */
.header {
  height: 60px;
  background-color: var(--header-bg);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.hamburger-btn {
  font-size: 18px;
  color: var(--text-color);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.action-btn {
  font-size: 18px;
  color: var(--text-color);
}

.notification-badge {
  margin-right: 8px;
}

.user-avatar {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: background-color 0.3s ease;
}

.user-avatar:hover {
  background-color: var(--hover-bg);
}

.username {
  color: var(--text-color);
  font-size: 14px;
}

/* 主内容样式 */
.main-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  overflow-x: hidden;
  background-color: #f0f2f5;
  min-height: 0;
}

.dark-mode .main-content {
  background-color: #111827;
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    height: 100vh;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }
  
  .sidebar.mobile-drawer {
    transform: translateX(0);
  }
  
  .mobile-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    z-index: 999;
  }
  
  .header {
    padding: 0 16px;
  }
  
  .main-content {
    padding: 16px;
  }
  
  .username {
    display: none;
  }
}

/* 暗黑模式适配 */
.dark-mode .sidebar {
  background-color: var(--sidebar-bg);
}

.dark-mode .header {
  background-color: var(--header-bg);
  border-bottom-color: var(--border-color);
}

.dark-mode .el-menu-item {
  color: var(--text-color);
}

.dark-mode .el-menu-item:hover {
  background-color: var(--hover-bg);
}

.dark-mode .el-menu-item.is-active {
  background-color: var(--primary-color);
  color: #ffffff;
}
</style>
