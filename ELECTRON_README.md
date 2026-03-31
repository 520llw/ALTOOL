# AITOOL 参数提取系统 - Electron 桌面版

## 简介

AITOOL 参数提取系统的 Electron 桌面版，提供原生的桌面应用体验，支持 Windows、macOS 和 Linux 平台。

## 特性

- 🖥️ **原生桌面体验** - 独立的窗口应用，无需浏览器
- ⚡ **自动启动后端** - 自动启动 FastAPI 后端服务
- 🔒 **数据安全** - 本地运行，数据不上传云端
- 📦 **离线可用** - 无需网络连接即可使用（AI 功能除外）
- 🎨 **统一界面** - 与 Web 版一致的用户界面

## 系统要求

### Windows
- Windows 10 或更高版本
- Node.js 18+ (开发/构建时需要)
- Python 3.10+ (运行时需要)

### macOS
- macOS 11 (Big Sur) 或更高版本
- Node.js 18+ (开发/构建时需要)
- Python 3.10+ (运行时需要)

### Linux
- Ubuntu 20.04+ / Debian 10+ / Fedora 35+
- Node.js 18+ (开发/构建时需要)
- Python 3.10+ (运行时需要)

## 快速开始

### 1. 安装依赖

```bash
# 安装 Node.js 依赖
npm install

# 安装前端依赖
cd frontend && npm install && cd ..

# 安装 Python 依赖（如果没有虚拟环境）
cd backend
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows
pip install -r requirements.txt
cd ..
```

### 2. 启动应用

#### 方式一：使用启动脚本

```bash
# Linux/macOS
./start-electron.sh

# Windows
start-electron.bat
```

#### 方式二：使用 npm 命令

```bash
# 开发模式（自动加载前端开发服务器）
npm run electron:dev

# 生产模式（使用构建后的前端文件）
npm run electron:start
```

### 3. 打包应用

```bash
# 打包当前平台
npm run electron:build

# 打包指定平台
npm run electron:build:win    # Windows
npm run electron:build:mac    # macOS
npm run electron:build:linux  # Linux
```

打包后的文件位于 `release/` 目录：
- **Windows**: `release/AITOOL-Setup-x.x.x.exe` (安装程序) + `release/AITOOL-Portable-x.x.x.exe` (便携版)
- **macOS**: `release/AITOOL-x.x.x.dmg` (磁盘镜像)
- **Linux**: `release/AITOOL-x.x.x.AppImage` (AppImage) + `release/aitool-param-extractor_x.x.x_amd64.deb` (Debian 包)

## 项目结构

```
.
├── electron/                   # Electron 主进程代码
│   ├── main.js                # 主进程入口
│   ├── preload.js             # 预加载脚本（安全 Bridge）
│   ├── icons/                 # 应用图标
│   │   ├── icon.ico           # Windows 图标
│   │   ├── icon.icns          # macOS 图标
│   │   └── icon.png           # Linux 图标
│   └── package.json           # Electron 专用配置
├── frontend/                   # Vue3 前端代码
│   ├── src/
│   │   └── api/
│   │       └── index.ts       # API 请求封装（支持 Electron）
│   └── dist/                  # 构建后的前端文件
├── backend/                    # FastAPI 后端代码
│   ├── app/
│   │   └── main.py            # FastAPI 入口
│   └── venv/                  # Python 虚拟环境
├── package.json               # 根目录配置（包含 Electron Builder）
├── start-electron.sh          # Linux/macOS 启动脚本
├── start-electron.bat         # Windows 启动脚本
└── ELECTRON_README.md         # 本文档
```

## 开发指南

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `NODE_ENV` | 运行环境 | `production` |
| `ELECTRON` | Electron 标记 | `false` |
| `PORT` | 后端端口 | `8000` |
| `DEBUG` | 调试模式 | `false` |

### 开发模式

```bash
# 终端 1：启动前端开发服务器
cd frontend
npm run dev

# 终端 2：启动 Electron（开发模式）
npm run electron:dev
```

### 调试

- 按 `F12` 打开开发者工具
- 主进程日志输出在终端
- 渲染进程日志在开发者工具 Console 中

## 常见问题

### Q: 启动时提示 "找不到 Python"
A: 确保系统已安装 Python 3.10+，并且 `python` 或 `python3` 命令可用。

### Q: 后端启动失败
A: 检查：
1. 后端虚拟环境是否正确创建
2. Python 依赖是否安装完整
3. 端口 8000 是否被占用

### Q: 前端页面显示空白
A: 检查：
1. 前端是否已构建 (`cd frontend && npm run build`)
2. `frontend/dist/index.html` 是否存在
3. 开发者工具 Console 中的错误信息

### Q: API 请求失败
A: 检查：
1. 后端服务是否正常运行（访问 http://localhost:8000/health）
2. 防火墙是否阻止了本地连接
3. CORS 配置是否正确

### Q: 打包后的应用无法运行
A: 检查：
1. 是否包含了后端代码（`extraResources` 配置）
2. Python 环境是否正确打包
3. 图标文件是否存在

## 更新日志

### v1.0.0
- ✨ 初始版本发布
- 🖥️ 支持 Windows/macOS/Linux
- ⚡ 自动启动 FastAPI 后端
- 🔧 支持开发/生产模式

## 技术支持

如有问题，请通过以下方式联系：

- 邮箱：support@gjw.com
- GitHub Issues：[项目地址]/issues

## 许可证

MIT License
