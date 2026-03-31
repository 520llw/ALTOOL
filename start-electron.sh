#!/bin/bash

# AITOOL 参数提取系统 - Electron 启动脚本 (Linux/macOS)

echo "🚀 启动 AITOOL 参数提取系统..."

# 检查 Node.js 是否安装
if ! command -v node &> /dev/null; then
    echo "❌ 错误：未安装 Node.js"
    echo "请先安装 Node.js (https://nodejs.org/)"
    exit 1
fi

# 检查 npm 是否安装
if ! command -v npm &> /dev/null; then
    echo "❌ 错误：未安装 npm"
    exit 1
fi

# 安装依赖（如果需要）
if [ ! -d "node_modules" ] || [ ! -d "frontend/node_modules" ]; then
    echo "📦 正在安装依赖..."
    npm install
fi

# 构建前端
echo "🔨 正在构建前端..."
cd frontend
npm run build
cd ..

# 启动 Electron
echo "🖥️  启动 Electron..."
npm run electron:start
