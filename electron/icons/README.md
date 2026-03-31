# Electron 图标

此目录用于存放 Electron 应用程序的图标文件。

## 需要的图标文件

### Windows
- `icon.ico` - 主图标 (256x256 或更大，支持多尺寸)

### macOS
- `icon.icns` - 主图标 (1024x1024)

### Linux
- `icon.png` - 主图标 (512x512 或 256x256)

## 图标生成工具

可以使用以下工具生成图标：

1. **在线工具**：
   - [ICO Convert](https://icoconvert.com/)
   - [App Icon Generator](https://appicon.co/)

2. **命令行工具**：
   - `electron-icon-builder` - npm 包
   - ImageMagick 脚本

## 快速生成示例

```bash
# 安装 electron-icon-builder
npm install -g electron-icon-builder

# 生成图标（从 1024x1024 源图）
electron-icon-builder --input=./source-icon.png --output=./electron/icons
```

## 注意事项

- Windows 图标需要包含多种尺寸（16, 32, 48, 64, 128, 256）
- macOS 图标需要是 .icns 格式
- Linux 图标通常使用 PNG 格式
