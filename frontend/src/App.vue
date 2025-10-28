<template>
  <div id="app" :class="{ 'login-page': isLoginPage }">
    <!-- 侧边栏 -->
    <aside 
      v-if="!isLoginPage"
      class="sidebar" 
      :class="{ 
        'collapsed': isCollapsed,
        'mobile-drawer': isMobile && !isCollapsed
      }"
    >
      <div class="sidebar-header">
        <img src="./assets/vue.svg" alt="Logo" class="logo" />
        <span v-show="!isCollapsed" class="title">国粒智能边缘控制台</span>
      </div>
      
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapsed"
        :unique-opened="true"
        router
        class="sidebar-menu"
      >
        <!-- 主菜单分组 -->
        <div class="menu-group-title">主菜单</div>
        
        <el-menu-item index="/dashboard">
          <el-icon><DataBoard /></el-icon>
          <template #title>仪表盘</template>
        </el-menu-item>
        
        <el-menu-item index="/robots">
          <el-icon><Avatar /></el-icon>
          <template #title>机器人管理</template>
        </el-menu-item>
        
        <el-menu-item index="/tasks">
          <el-icon><Memo /></el-icon>
          <template #title>任务调度</template>
        </el-menu-item>
        
        <el-menu-item index="/real-time-monitoring">
          <el-icon><Monitor /></el-icon>
          <template #title>实时监控</template>
        </el-menu-item>
        
        <el-menu-item index="/alarm-events">
          <el-icon><Warning /></el-icon>
          <template #title>报警事件</template>
        </el-menu-item>
        
        <el-menu-item index="/video-playback">
          <el-icon><VideoPlay /></el-icon>
          <template #title>录像回放</template>
        </el-menu-item>
        
        <el-menu-item index="/performance-monitoring">
          <el-icon><TrendCharts /></el-icon>
          <template #title>性能监控</template>
        </el-menu-item>
        
        <el-menu-item index="/data-analysis">
          <el-icon><DataLine /></el-icon>
          <template #title>数据分析</template>
        </el-menu-item>
        
        <!-- 系统管理分组 -->
        <div class="menu-group-title">系统管理</div>
        <el-menu-item index="/users">
          <el-icon><User /></el-icon>
          <template #title>用户管理</template>
        </el-menu-item>
        
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <template #title>系统设置</template>
        </el-menu-item>
        
        <el-menu-item index="/logs">
          <el-icon><Document /></el-icon>
          <template #title>操作日志</template>
        </el-menu-item>
        
        <el-menu-item index="/data-backup">
          <el-icon><Document /></el-icon>
          <template #title>数据备份</template>
        </el-menu-item>
        
        <el-menu-item index="/log-audit">
          <el-icon><Document /></el-icon>
          <template #title>日志审计</template>
        </el-menu-item>
      </el-menu>
    </aside>

    <!-- 主内容区域 -->
    <div class="main-container" :class="{ 'fullscreen': isLoginPage }">
      <!-- 顶部导航 -->
      <header v-if="!isLoginPage" class="header">
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
      <main class="main-content" :class="{ 'fullscreen-content': isLoginPage }">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>

    <!-- 移动端遮罩 -->
    <div 
      v-if="isMobile && !isCollapsed && !isLoginPage" 
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
  Bell,
  ArrowDown,
  Document,
  Avatar,
  Memo,
  Monitor,
  Warning,
  VideoPlay,
  TrendCharts,
  DataLine
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// 响应式状态
const isCollapsed = ref(false)
const isMobile = ref(false)

// 路由相关
const route = useRoute()
const router = useRouter()

// 计算属性
const activeMenu = computed(() => route.path)

const isLoginPage = computed(() => route.path === '/login')

const breadcrumbs = computed(() => {
  const pathMap: Record<string, string> = {
    '/dashboard': '仪表盘',
    '/robots': '机器人管理',
    '/tasks': '任务调度',
    '/users': '用户管理',
    '/settings': '系统设置',
    '/logs': '日志信息',
    '/video-playback': '录像回放',
    '/real-time-monitoring': '实时监控',
    '/alarm-events': '报警事件'
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
  --primary-color: #7e57c2;
  --primary-light: #b085f5;
  --primary-dark: #4d2c91;
  --sidebar-bg: #252836;
  --sidebar-item-hover: #2e3347;
  --sidebar-item-active: #7e57c2;
  --sidebar-text: #a0a3bd;
  --sidebar-text-active: #ffffff;
  --header-bg: #ffffff;
  --text-color: #303133;
  --border-color: rgba(228, 231, 237, 0.1);
  --hover-bg: #f5f7fa;
}



#app {
  display: flex;
  height: 100vh;
  width: 100vw;
  background-color: #f0f2f5;
  transition: all 0.3s ease;
  overflow: hidden;
}



/* 登录页面全屏样式 */
.login-page {
  display: block !important;
}

.login-page .main-container.fullscreen {
  width: 100vw;
  height: 100vh;
  padding: 0;
  margin: 0;
}

.login-page .main-content.fullscreen-content {
  padding: 0;
  margin: 0;
  width: 100%;
  height: 100%;
  background: none;
}

/* 侧边栏样式 */
.sidebar {
  width: 250px;
  height: 100vh;
  background-color: var(--sidebar-bg);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 1000;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
  flex-shrink: 0;
  overflow-y: auto;
  position: relative;
}

.sidebar.collapsed {
  width: 70px;
}

.sidebar-header {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 10px;
  border-bottom: 2px solid #e5e7eb;
  flex-shrink: 0;
  background: linear-gradient(to right, var(--primary-dark), var(--primary-color));
}

.logo {
  width: 36px;
  height: 36px;
  margin-right: 12px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
  transition: transform 0.3s ease;
}

.sidebar.collapsed .logo {
  margin-right: 0;
}

.title {
  color: black;
  font-size: 18px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  letter-spacing: 0.5px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.sidebar-menu {
  border: none;
  background-color: transparent;
  flex: 1;
  padding: 10px 0;
}

.sidebar-menu .el-menu-item {
  height: 40px;
  line-height: 56px;
  color: var(--sidebar-text);
  border-bottom: none;
  margin: 4px 10px;
  border-radius: 8px;
  transition: all 0.3s ease;
  position: relative;
}

.sidebar-menu .el-menu-item:hover {
  background-color: var(--sidebar-item-hover);
  color: var(--sidebar-text-active);
}

.sidebar-menu .el-menu-item.is-active {
  background-color:#3c97f4; /* 浅蓝色底色 */
  color: var(--sidebar-text-active);
  font-weight: 500;
  box-shadow: 0 4px 10px rgba(126, 87, 194, 0.3);
}

.sidebar-menu .el-menu-item .el-icon {
  margin-right: 12px;
  font-size: 18px;
  transition: transform 0.2s ease;
}

.sidebar-menu .el-menu-item:hover .el-icon {
  transform: translateX(2px);
}

.menu-group-title {
  padding: 10px 20px;
  color: #909399;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-top: 10px;
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
  border-bottom: 2px solid #e5e7eb;
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


</style>
