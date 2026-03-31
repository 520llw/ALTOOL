export interface UserInfo {
  id: number
  username: string
  role: 'admin' | 'user'
  is_active: boolean
  created_at: string
  last_login: string | null
  has_api_key?: boolean
}

export interface LoginForm {
  username: string
  password: string
  remember_me?: boolean
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface StandardParam {
  id: number
  param_name: string
  param_name_en: string | null
  param_type: string | null
  unit: string | null
  category: string | null
  create_time: string
  update_time: string
}

export interface ParamVariant {
  id: number
  param_id: number
  variant_name: string
  vendor: string | null
  create_time: string
}

export interface ParamWithVariants extends StandardParam {
  variants: ParamVariant[]
}

export interface ParamCreateForm {
  param_name: string
  param_name_en?: string
  param_type?: string
  unit?: string
  category?: string
  variants?: string[]
}

export interface ParamUpdateForm {
  param_name?: string
  param_name_en?: string
  param_type?: string
  unit?: string
  category?: string
}

export interface VariantCreateForm {
  variant_name: string
  vendor?: string
}

export interface UserCreateForm {
  username: string
  password: string
  role?: 'admin' | 'user'
  is_active?: boolean
}

export interface UserUpdateForm {
  username?: string
  role?: 'admin' | 'user'
  is_active?: boolean
}

export interface PasswordChangeForm {
  old_password: string
  new_password: string
}

export interface ApiKeyForm {
  api_key: string
}

export interface PaginatedResponse<T> {
  total: number
  items: T[]
}

export interface ListResponse<T> {
  items: T[]
}

// ==================== Electron API 类型 ====================

/**
 * Electron API 接口
 */
export interface ElectronAPI {
  /** 操作系统平台 */
  platform: string
  /** Node.js 版本 */
  nodeVersion: string
  /** Electron 版本 */
  electronVersion: string
  
  /**
   * 获取应用版本
   */
  getAppVersion: () => Promise<string>
  
  /**
   * 获取后端服务端口号
   */
  getBackendPort: () => Promise<number>
  
  /**
   * 打开文件选择对话框
   * @param options - 对话框选项
   */
  openFileDialog: (options?: Record<string, unknown>) => Promise<{ canceled: boolean; filePaths: string[] }>
  
  /**
   * 打开保存文件对话框
   * @param options - 对话框选项
   */
  saveFileDialog: (options?: Record<string, unknown>) => Promise<{ canceled: boolean; filePath?: string }>
  
  /**
   * 检查文件是否存在
   * @param filePath - 文件路径
   */
  checkFileExists: (filePath: string) => Promise<boolean>
  
  /**
   * 使用系统默认浏览器打开外部链接
   * @param url - 要打开的 URL
   */
  openExternal: (url: string) => Promise<void>
  
  /**
   * 监听事件
   * @param channel - 消息通道
   * @param callback - 回调函数
   */
  on: (channel: string, callback: (...args: unknown[]) => void) => void
  
  /**
   * 移除事件监听器
   * @param channel - 消息通道
   * @param callback - 回调函数
   */
  off: (channel: string, callback: (...args: unknown[]) => void) => void
  
  /**
   * 发送消息到主进程
   * @param channel - 消息通道
   * @param data - 发送的数据
   */
  send: (channel: string, data?: unknown) => void
  
  /**
   * 调用主进程处理程序（异步）
   * @param channel - 消息通道
   * @param data - 发送的数据
   */
  invoke: (channel: string, data?: unknown) => Promise<unknown>
  
  /**
   * 接收主进程消息
   * @param channel - 消息通道
   * @param func - 回调函数
   */
  receive: (channel: string, func: (...args: unknown[]) => void) => void
}

/**
 * 扩展 Window 接口以支持 Electron API
 */
declare global {
  interface Window {
    /** Electron API */
    electronAPI?: ElectronAPI
    /** 是否为 Electron 环境 */
    isElectron?: boolean
    /** 获取 API 基础 URL */
    getApiBaseUrl?: () => Promise<string>
  }
}
