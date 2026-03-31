/**
 * AITOOL 参数提取系统 - Electron 预加载脚本
 * 在渲染进程中暴露安全的 API
 */

const { contextBridge, ipcRenderer } = require('electron');

// 暴露给渲染进程的 API
contextBridge.exposeInMainWorld('electronAPI', {
    // ==================== 系统信息 ====================
    
    /**
     * 获取操作系统平台
     */
    platform: process.platform,
    
    /**
     * 获取 Node.js 版本
     */
    nodeVersion: process.versions.node,
    
    /**
     * 获取 Electron 版本
     */
    electronVersion: process.versions.electron,
    
    /**
     * 获取应用版本
     */
    getAppVersion: () => ipcRenderer.invoke('get-app-version'),
    
    /**
     * 获取后端服务端口号
     */
    getBackendPort: () => ipcRenderer.invoke('get-backend-port'),
    
    // ==================== 文件操作 ====================
    
    /**
     * 打开文件选择对话框
     * @param {Object} options - 对话框选项
     */
    openFileDialog: (options = {}) => ipcRenderer.invoke('open-file-dialog', options),
    
    /**
     * 打开保存文件对话框
     * @param {Object} options - 对话框选项
     */
    saveFileDialog: (options = {}) => ipcRenderer.invoke('save-file-dialog', options),
    
    /**
     * 检查文件是否存在
     * @param {string} filePath - 文件路径
     */
    checkFileExists: (filePath) => ipcRenderer.invoke('check-file-exists', filePath),
    
    // ==================== 外部链接 ====================
    
    /**
     * 使用系统默认浏览器打开外部链接
     * @param {string} url - 要打开的 URL
     */
    openExternal: (url) => ipcRenderer.invoke('open-external', url),
    
    // ==================== 事件监听 ====================
    
    /**
     * 监听主进程发送的消息
     * @param {string} channel - 消息通道
     * @param {Function} callback - 回调函数
     */
    on: (channel, callback) => {
        const validChannels = ['app-update', 'backend-status', 'download-progress'];
        if (validChannels.includes(channel)) {
            ipcRenderer.on(channel, (event, ...args) => callback(...args));
        }
    },
    
    /**
     * 移除事件监听器
     * @param {string} channel - 消息通道
     * @param {Function} callback - 回调函数
     */
    off: (channel, callback) => {
        ipcRenderer.removeListener(channel, callback);
    },
    
    // ==================== IPC 通信 ====================
    
    /**
     * 发送消息到主进程
     * @param {string} channel - 消息通道
     * @param {*} data - 发送的数据
     */
    send: (channel, data) => {
        const validChannels = ['toMain', 'minimize-window', 'maximize-window', 'close-window'];
        if (validChannels.includes(channel)) {
            ipcRenderer.send(channel, data);
        }
    },
    
    /**
     * 调用主进程处理程序（异步）
     * @param {string} channel - 消息通道
     * @param {*} data - 发送的数据
     */
    invoke: (channel, data) => {
        const validChannels = [];
        if (validChannels.includes(channel)) {
            return ipcRenderer.invoke(channel, data);
        }
    },
    
    /**
     * 接收主进程消息
     * @param {string} channel - 消息通道
     * @param {Function} func - 回调函数
     */
    receive: (channel, func) => {
        const validChannels = ['fromMain'];
        if (validChannels.includes(channel)) {
            ipcRenderer.on(channel, (event, ...args) => func(...args));
        }
    }
});

// ==================== Vue3 环境优化 ====================

// 添加错误处理
try {
    // 禁用网页拖拽默认行为（防止意外打开文件）
    document.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.stopPropagation();
    }, false);
    
    document.addEventListener('drop', (e) => {
        e.preventDefault();
        e.stopPropagation();
        
        // 可以在这里处理文件拖放
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            window.dispatchEvent(new CustomEvent('electron-file-dropped', {
                detail: { files: Array.from(files) }
            }));
        }
    }, false);
} catch (error) {
    console.error('Preload script error:', error);
}

// 标记 Electron 环境
contextBridge.exposeInMainWorld('isElectron', true);

// 暴露 API 基础 URL 构建函数
contextBridge.exposeInMainWorld('getApiBaseUrl', async () => {
    const port = await ipcRenderer.invoke('get-backend-port');
    return `http://127.0.0.1:${port}`;
});
