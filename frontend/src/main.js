import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './style.css'
import App from './App.vue'
import router from './router'
import { createI18n } from 'vue-i18n'
import zhCN from './locales/zh-CN.js'
import enUS from './locales/en-US.js'

// 获取本地存储的语言设置，默认中文
const getStoredLanguage = () => {
  return localStorage.getItem('language') || 'zh-CN'
}

// 创建i18n实例
const i18n = createI18n({
  legacy: false, // 使用Composition API模式
  locale: getStoredLanguage(), // 默认语言
  fallbackLocale: 'zh-CN', // 回退语言
  messages: {
    'zh-CN': zhCN,
    'en-US': enUS
  }
})

// 切换语言的函数
export const changeLanguage = async (locale) => {
  i18n.global.locale.value = locale
  localStorage.setItem('language', locale)

  // 同时更新Element Plus的语言
  try {
    if (locale === 'zh-CN') {
      const zhCn = await import('element-plus/es/locale/lang/zh-cn')
      // 这里可以设置Element Plus的中文语言包
    } else if (locale === 'en-US') {
      const en = await import('element-plus/es/locale/lang/en')
      // 这里可以设置Element Plus的英文语言包
    }
  } catch (error) {
    console.warn('Element Plus语言包加载失败:', error)
  }
}

// 获取当前语言
export const getCurrentLanguage = () => {
  return i18n.global.locale.value
}

const app = createApp(App)
app.use(ElementPlus)
app.use(router)
app.use(i18n)

// 全局语言切换函数挂载到window对象，方便调试
window.changeLanguage = changeLanguage
window.getCurrentLanguage = getCurrentLanguage

app.mount('#app')