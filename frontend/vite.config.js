import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  },
  server: {
    proxy: {
      // 代理所有 /api2 请求到Django后端
      '/api2': {
        target: 'http://172.16.160.100:8003',  // Django后端地址
        changeOrigin: true,
        rewrite: (path) => path  // 保持路径不变
      },
      // 代理媒体文件请求
      '/media': {
        target: 'http://172.16.160.100:8003',
        changeOrigin: true,
        rewrite: (path) => path
      }
    }
  }
})
