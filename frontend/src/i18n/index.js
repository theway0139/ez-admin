import { createI18n } from 'vue-i18n'
import zhCN from '../locales/zh-CN.js'
import enUS from '../locales/en-US.js'

// 获取本地存储的语言设置
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
export const changeLanguage = (locale) => {
  i18n.global.locale.value = locale
  localStorage.setItem('language', locale)
  
  // 同时更新Element Plus的语言
  import('element-plus/es/locale/lang/zh-cn').then(zhCN => {
    if (locale === 'zh-CN') {
      // 这里可以设置Element Plus的中文语言包
    }
  })
  
  import('element-plus/es/locale/lang/en').then(enUS => {
    if (locale === 'en-US') {
      // 这里可以设置Element Plus的英文语言包
    }
  })
}

// 获取当前语言
export const getCurrentLanguage = () => {
  return i18n.global.locale.value
}

export default i18n
