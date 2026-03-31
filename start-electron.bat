@echo off
chcp 65001 >nul

:: AITOOL 参数提取系统 - Electron 启动脚本 (Windows)

echo 🚀 启动 AITOOL 参数提取系统...

:: 检查 Node.js 是否安装
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未安装 Node.js
    echo 请先安装 Node.js ^(https://nodejs.org/^)
    pause
    exit /b 1
)

:: 检查 npm 是否安装
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未安装 npm
    pause
    exit /b 1
)

:: 安装依赖（如果需要）
if not exist "node_modules" (
    echo 📦 正在安装依赖...
    call npm install
    if errorlevel 1 (
        echo ❌ 安装依赖失败
        pause
        exit /b 1
    )
)

if not exist "frontend\node_modules" (
    echo 📦 正在安装前端依赖...
    cd frontend
    call npm install
    if errorlevel 1 (
        echo ❌ 安装前端依赖失败
        pause
        exit /b 1
    )
    cd ..
)

:: 构建前端
echo 🔨 正在构建前端...
cd frontend
call npm run build
if errorlevel 1 (
    echo ❌ 构建前端失败
    pause
    exit /b 1
)
cd ..

:: 启动 Electron
echo 🖥️ 启动 Electron...
npm run electron:start
if errorlevel 1 (
    echo ❌ 启动 Electron 失败
    pause
    exit /b 1
)

pause
