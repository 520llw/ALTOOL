import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const isElectron = process.env.ELECTRON === 'true'
  
  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': resolve(__dirname, 'src')
      }
    },
    server: {
      port: 5173,
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true
        }
      }
    },
    build: {
      outDir: 'dist',
      sourcemap: true,
      // Electron 环境下禁用代码分割，简化打包
      rollupOptions: isElectron ? {
        output: {
          manualChunks: undefined
        }
      } : undefined
    },
    // 定义全局变量
    define: {
      __IS_ELECTRON__: isElectron
    },
    // 优化依赖
    optimizeDeps: {
      include: ['vue', 'vue-router', 'pinia', 'axios', 'element-plus', '@element-plus/icons-vue']
    }
  }
})
