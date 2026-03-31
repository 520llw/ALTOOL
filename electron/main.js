/**
 * AITOOL 参数提取系统 - Electron 主进程
 * 支持 Vue3 前端 + FastAPI 后端
 */

const { app, BrowserWindow, ipcMain, dialog, shell, Menu } = require('electron');
const { spawn, exec } = require('child_process');
const path = require('path');
const fs = require('fs');
const net = require('net');
const http = require('http');

// 全局变量
let mainWindow = null;
let backendProcess = null;
let backendPort = 8000;
let isQuitting = false;
let isDev = process.env.NODE_ENV === 'development';

// 项目路径配置
const ROOT_DIR = path.join(__dirname, '..');
const FRONTEND_DIST = path.join(ROOT_DIR, 'frontend', 'dist');
const BACKEND_DIR = path.join(ROOT_DIR, 'backend');

/**
 * 日志函数
 */
function log(message, type = 'info') {
    const timestamp = new Date().toISOString();
    const prefix = type === 'error' ? '❌' : type === 'warn' ? '⚠️' : '✅';
    console.log(`[${timestamp}] ${prefix} ${message}`);
}

/**
 * 检查端口是否被占用
 */
function checkPort(port) {
    return new Promise((resolve) => {
        const server = net.createServer();
        server.once('error', (err) => {
            if (err.code === 'EADDRINUSE') {
                resolve(false);
            } else {
                resolve(false);
            }
        });
        server.once('listening', () => {
            server.close();
            resolve(true);
        });
        server.listen(port);
    });
}

/**
 * 查找可用端口
 */
async function findAvailablePort(startPort) {
    let port = startPort;
    while (port < startPort + 100) {
        const available = await checkPort(port);
        if (available) {
            return port;
        }
        port++;
    }
    return startPort;
}

/**
 * 检查后端服务是否就绪
 */
function checkBackendReady(port) {
    return new Promise((resolve) => {
        const req = http.get(`http://localhost:${port}/health`, (res) => {
            if (res.statusCode === 200) {
                resolve(true);
            } else {
                resolve(false);
            }
        });
        req.on('error', () => resolve(false));
        req.setTimeout(1000, () => {
            req.destroy();
            resolve(false);
        });
    });
}

/**
 * 等待后端服务启动
 */
async function waitForBackend(port, maxAttempts = 30) {
    for (let i = 0; i < maxAttempts; i++) {
        const ready = await checkBackendReady(port);
        if (ready) {
            return true;
        }
        await new Promise(r => setTimeout(r, 1000));
    }
    return false;
}

/**
 * 启动 FastAPI 后端服务
 */
async function startBackend() {
    // 查找可用端口
    backendPort = await findAvailablePort(8000);
    log(`Starting FastAPI backend on port ${backendPort}...`);

    // 检测操作系统和环境
    const isWindows = process.platform === 'win32';
    const venvPython = isWindows
        ? path.join(BACKEND_DIR, 'venv', 'Scripts', 'python.exe')
        : path.join(BACKEND_DIR, 'venv', 'bin', 'python');

    // 优先使用虚拟环境的 Python，否则使用系统 Python
    const pythonCmd = fs.existsSync(venvPython) ? venvPython : (isWindows ? 'python' : 'python3');

    log(`Using Python: ${pythonCmd}`);

    // 设置环境变量
    const env = {
        ...process.env,
        PYTHONUNBUFFERED: '1',
        PORT: backendPort.toString(),
        HOST: '127.0.0.1',
        DEBUG: isDev ? 'true' : 'false'
    };

    // 构建启动参数
    const args = [
        '-m', 'uvicorn',
        'app.main:app',
        '--host', '127.0.0.1',
        '--port', backendPort.toString(),
        '--reload', 'false'
    ];

    // 启动后端进程
    backendProcess = spawn(pythonCmd, args, {
        cwd: BACKEND_DIR,
        env,
        shell: isWindows
    });

    // 监听输出
    backendProcess.stdout.on('data', (data) => {
        const output = data.toString().trim();
        if (output) {
            log(`[Backend] ${output}`);
        }
    });

    backendProcess.stderr.on('data', (data) => {
        const output = data.toString().trim();
        if (output) {
            log(`[Backend Error] ${output}`, 'error');
        }
    });

    backendProcess.on('close', (code) => {
        log(`Backend process exited with code ${code}`, code === 0 ? 'info' : 'error');
        if (!isQuitting && code !== 0) {
            log('Backend crashed, attempting to restart in 3 seconds...', 'warn');
            setTimeout(startBackend, 3000);
        }
    });

    backendProcess.on('error', (err) => {
        log(`Failed to start backend: ${err.message}`, 'error');
        dialog.showErrorBox(
            '启动失败',
            `无法启动后端服务: ${err.message}\n\n请确保已安装 Python 和必要的依赖包。`
        );
    });

    // 等待后端就绪
    log('Waiting for backend to be ready...');
    const ready = await waitForBackend(backendPort);
    if (ready) {
        log('Backend is ready!');
    } else {
        log('Backend may not be fully ready yet, continuing...', 'warn');
    }

    return backendPort;
}

/**
 * 停止后端服务
 */
function stopBackend() {
    if (backendProcess) {
        log('Stopping backend service...');

        if (process.platform === 'win32') {
            // Windows 下需要杀死进程树
            exec(`taskkill /pid ${backendProcess.pid} /T /F`, (err) => {
                if (err) {
                    log(`Error killing backend: ${err.message}`, 'error');
                }
            });
        } else {
            backendProcess.kill('SIGTERM');
            // 如果 5 秒后还没退出，强制杀死
            setTimeout(() => {
                if (!backendProcess.killed) {
                    backendProcess.kill('SIGKILL');
                }
            }, 5000);
        }

        backendProcess = null;
    }
}

/**
 * 创建加载窗口
 */
function createSplashWindow() {
    const splash = new BrowserWindow({
        width: 500,
        height: 350,
        frame: false,
        alwaysOnTop: true,
        transparent: true,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true
        }
    });

    splash.loadURL(`data:text/html;charset=utf-8,
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    overflow: hidden;
                }
                .container {
                    text-align: center;
                    padding: 40px;
                }
                .logo {
                    width: 80px;
                    height: 80px;
                    background: rgba(255,255,255,0.2);
                    border-radius: 20px;
                    margin: 0 auto 24px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 40px;
                }
                h1 { font-size: 24px; font-weight: 600; margin-bottom: 12px; }
                p { font-size: 14px; opacity: 0.9; margin-bottom: 24px; }
                .loader {
                    width: 200px;
                    height: 4px;
                    background: rgba(255,255,255,0.3);
                    border-radius: 2px;
                    margin: 0 auto;
                    overflow: hidden;
                }
                .loader-bar {
                    width: 40%;
                    height: 100%;
                    background: white;
                    border-radius: 2px;
                    animation: loading 1.5s ease-in-out infinite;
                }
                @keyframes loading {
                    0% { transform: translateX(-100%); }
                    100% { transform: translateX(250%); }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="logo">⚡</div>
                <h1>AITOOL 参数提取系统</h1>
                <p>正在启动，请稍候...</p>
                <div class="loader">
                    <div class="loader-bar"></div>
                </div>
            </div>
        </body>
        </html>
    `);

    return splash;
}

/**
 * 创建应用菜单
 */
function createMenu() {
    const template = [
        {
            label: '文件',
            submenu: [
                {
                    label: '刷新',
                    accelerator: 'F5',
                    click: () => {
                        if (mainWindow) {
                            mainWindow.webContents.reload();
                        }
                    }
                },
                {
                    label: '开发者工具',
                    accelerator: 'F12',
                    click: () => {
                        if (mainWindow) {
                            mainWindow.webContents.toggleDevTools();
                        }
                    }
                },
                { type: 'separator' },
                {
                    label: '退出',
                    accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
                    click: () => {
                        app.quit();
                    }
                }
            ]
        },
        {
            label: '编辑',
            submenu: [
                { label: '撤销', accelerator: 'CmdOrCtrl+Z', role: 'undo' },
                { label: '重做', accelerator: 'Shift+CmdOrCtrl+Z', role: 'redo' },
                { type: 'separator' },
                { label: '剪切', accelerator: 'CmdOrCtrl+X', role: 'cut' },
                { label: '复制', accelerator: 'CmdOrCtrl+C', role: 'copy' },
                { label: '粘贴', accelerator: 'CmdOrCtrl+V', role: 'paste' },
                { label: '全选', accelerator: 'CmdOrCtrl+A', role: 'selectall' }
            ]
        },
        {
            label: '窗口',
            submenu: [
                { label: '最小化', accelerator: 'CmdOrCtrl+M', role: 'minimize' },
                { label: '关闭', accelerator: 'CmdOrCtrl+W', role: 'close' },
                { type: 'separator' },
                { label: '重新加载', accelerator: 'CmdOrCtrl+R', role: 'reload' }
            ]
        },
        {
            label: '帮助',
            submenu: [
                {
                    label: '关于',
                    click: () => {
                        dialog.showMessageBox(mainWindow, {
                            type: 'info',
                            title: '关于 AITOOL 参数提取系统',
                            message: 'AITOOL 参数提取系统',
                            detail: `版本: ${app.getVersion()}\nElectron: ${process.versions.electron}\nNode.js: ${process.versions.node}\nChrome: ${process.versions.chrome}`
                        });
                    }
                }
            ]
        }
    ];

    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);
}

/**
 * 创建主窗口
 */
async function createMainWindow() {
    // 创建启动画面
    const splash = createSplashWindow();

    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        minWidth: 1000,
        minHeight: 700,
        title: 'AITOOL 参数提取系统',
        icon: path.join(__dirname, 'icons', 'icon.png'),
        show: false,  // 先隐藏，等加载完成再显示
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js'),
            webSecurity: false  // 允许本地文件访问（生产环境）
        },
        backgroundColor: '#f5f7fa'
    });

    // 开发环境加载开发服务器，生产环境加载打包后的文件
    if (isDev) {
        log('Loading development server...');
        mainWindow.loadURL('http://localhost:5173');
        mainWindow.webContents.openDevTools();
    } else {
        // 生产环境：加载打包后的前端文件
        const indexPath = path.join(FRONTEND_DIST, 'index.html');
        if (fs.existsSync(indexPath)) {
            log(`Loading production build from ${FRONTEND_DIST}`);
            mainWindow.loadFile(indexPath);
        } else {
            log('Production build not found!', 'error');
            dialog.showErrorBox(
                '错误',
                '找不到前端构建文件，请先运行 npm run build'
            );
            app.quit();
            return;
        }
    }

    // 等待页面加载完成后显示窗口
    mainWindow.webContents.on('did-finish-load', () => {
        splash.close();
        mainWindow.show();
        mainWindow.focus();
        log('Main window loaded');
    });

    // 处理窗口关闭
    mainWindow.on('closed', () => {
        mainWindow = null;
    });

    // 处理外部链接
    mainWindow.webContents.setWindowOpenHandler(({ url }) => {
        shell.openExternal(url);
        return { action: 'deny' };
    });
}

// ==================== IPC 通信处理 ====================

/**
 * 获取后端端口
 */
ipcMain.handle('get-backend-port', () => {
    return backendPort;
});

/**
 * 获取应用版本
 */
ipcMain.handle('get-app-version', () => {
    return app.getVersion();
});

/**
 * 打开文件对话框
 */
ipcMain.handle('open-file-dialog', async (event, options) => {
    const result = await dialog.showOpenDialog(mainWindow, {
        properties: ['openFile'],
        filters: [
            { name: 'PDF 文件', extensions: ['pdf'] },
            { name: '所有文件', extensions: ['*'] }
        ],
        ...options
    });
    return result;
});

/**
 * 保存文件对话框
 */
ipcMain.handle('save-file-dialog', async (event, options) => {
    const result = await dialog.showSaveDialog(mainWindow, {
        filters: [
            { name: 'Excel 文件', extensions: ['xlsx'] },
            { name: 'JSON 文件', extensions: ['json'] },
            { name: '所有文件', extensions: ['*'] }
        ],
        ...options
    });
    return result;
});

/**
 * 检查文件是否存在
 */
ipcMain.handle('check-file-exists', (event, filePath) => {
    return fs.existsSync(filePath);
});

/**
 * 打开外部链接
 */
ipcMain.handle('open-external', async (event, url) => {
    await shell.openExternal(url);
});

/**
 * 应用就绪
 */
app.whenReady().then(async () => {
    log('Electron app is ready');

    // 创建菜单
    createMenu();

    // 启动后端服务
    await startBackend();

    // 创建主窗口
    await createMainWindow();

    // macOS: 点击 dock 图标重新创建窗口
    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createMainWindow();
        }
    });
});

/**
 * 所有窗口关闭
 */
app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

/**
 * 应用退出前
 */
app.on('before-quit', () => {
    isQuitting = true;
    stopBackend();
});

/**
 * 应用退出
 */
app.on('quit', () => {
    stopBackend();
});

// 处理 Windows 安装/卸载
if (process.platform === 'win32') {
    const gotTheLock = app.requestSingleInstanceLock();
    if (!gotTheLock) {
        app.quit();
    } else {
        app.on('second-instance', () => {
            if (mainWindow) {
                if (mainWindow.isMinimized()) mainWindow.restore();
                mainWindow.focus();
            }
        });
    }
}
