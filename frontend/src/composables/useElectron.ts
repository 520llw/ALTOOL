import { ref, onMounted } from 'vue'

/**
 * Electron 环境检测与 API 封装
 */
export function useElectron() {
  const isElectron = ref(false)
  const backendPort = ref<number | null>(null)
  const isReady = ref(false)

  onMounted(async () => {
    // 检测是否在 Electron 环境中
    isElectron.value = !!(window.isElectron && window.electronAPI)
    
    if (isElectron.value && window.electronAPI) {
      try {
        backendPort.value = await window.electronAPI.getBackendPort()
      } catch (error) {
        console.error('Failed to get backend port:', error)
      }
    }
    
    isReady.value = true
  })

  /**
   * 打开文件选择对话框
   */
  async function openFileDialog(options?: Record<string, unknown>) {
    if (!window.electronAPI) {
      throw new Error('Not in Electron environment')
    }
    return window.electronAPI.openFileDialog(options)
  }

  /**
   * 打开保存文件对话框
   */
  async function saveFileDialog(options?: Record<string, unknown>) {
    if (!window.electronAPI) {
      throw new Error('Not in Electron environment')
    }
    return window.electronAPI.saveFileDialog(options)
  }

  /**
   * 打开外部链接
   */
  async function openExternal(url: string) {
    if (window.electronAPI?.openExternal) {
      return window.electronAPI.openExternal(url)
    } else {
      // 非 Electron 环境，使用默认行为
      window.open(url, '_blank')
    }
  }

  /**
   * 获取应用版本
   */
  async function getAppVersion() {
    if (!window.electronAPI) {
      return 'web'
    }
    return window.electronAPI.getAppVersion()
  }

  return {
    isElectron,
    backendPort,
    isReady,
    openFileDialog,
    saveFileDialog,
    openExternal,
    getAppVersion
  }
}
