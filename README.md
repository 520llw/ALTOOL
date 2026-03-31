# ⚡ 功率器件参数提取系统

一款基于 AI 的功率半导体器件（MOSFET / IGBT / SiC MOSFET）PDF 手册参数自动提取工具。

采用 **FastAPI + Vue3 + Electron** 技术栈，支持 Web 端访问和桌面端打包，提供批量处理、智能参数匹配、Excel 导出等能力。

---

## 📋 功能特性

- **智能 PDF 解析**：pdfplumber + PyMuPDF 双引擎，精准提取表格和文本
- **AI 参数提取**：支持 DeepSeek、OpenAI 等大模型 API
- **器件类型自动识别**：自动识别 Si MOSFET、SiC MOSFET、IGBT
- **参数标准化**：内置 62+ 标准参数库，支持自定义参数和变体
- **批量处理**：支持文件夹批量导入，多进程并行解析
- **Excel 分 Sheet 输出**：按器件类型分 Sheet 存储，方便查阅
- **Web + 桌面双端**：Vue3 前端可浏览器访问，Electron 可打包为桌面应用

---

## 🖥️ 系统要求

- **操作系统**：Windows 10/11、Ubuntu 20.04+、macOS 10.15+
- **Python**：3.10 或更高版本
- **Node.js**：18.0.0 或更高版本
- **内存**：建议 8GB 以上
- **网络**：需要访问 AI API（DeepSeek / OpenAI）

---

## 🚀 快速开始

### 1. 克隆项目并进入目录

```bash
cd AITOOL-refactor
```

### 2. 安装 Python 依赖

```bash
pip install -r requirements.txt
pip install -r backend/requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入你的 AI API 密钥等配置
```

> ⚠️ **重要**：生产环境务必修改 `SECRET_KEY`，并妥善保管 API 密钥。系统已移除所有硬编码密钥。

### 4. 安装前端依赖

```bash
cd frontend
npm install
cd ..
```

### 5. 启动方式（三选一）

#### 方式 A：启动 FastAPI 后端 + Vue 前端（开发模式）

**终端 1 - 启动后端：**

```bash
cd backend
python -m app.main
```

后端默认运行在 `http://localhost:8000`，API 文档地址：`http://localhost:8000/docs`

**终端 2 - 启动前端：**

```bash
cd frontend
npm run dev
```

前端默认运行在 `http://localhost:5173`，会自动代理到后端 API。

#### 方式 B：启动 Electron 桌面应用

```bash
# Linux / macOS
./start-electron.sh

# Windows
start-electron.bat
```

该脚本会自动构建前端并启动 Electron 桌面窗口。

#### 方式 C：使用旧版 Streamlit（兼容模式）

```bash
./start.sh        # Linux / macOS
start.bat         # Windows
```

---

## 📁 项目结构

```
AITOOL-refactor/
├── backend/                   # FastAPI 后端
│   ├── app/
│   │   ├── main.py            # FastAPI 入口
│   │   ├── api/v1/            # API 路由
│   │   ├── core/              # 安全、日志等核心模块
│   │   ├── models/            # SQLAlchemy 数据模型
│   │   ├── schemas/           # Pydantic 校验模型
│   │   ├── services/          # 业务逻辑层
│   │   ├── database.py        # 数据库连接与初始化
│   │   └── config.py          # Pydantic Settings 配置
│   ├── pdf_parser.py          # PDF 解析引擎
│   ├── ai_processor.py        # AI 调用与参数提取
│   ├── db_manager.py          # 数据库操作（兼容层）
│   └── requirements.txt       # 后端依赖
├── frontend/                  # Vue3 前端
│   ├── src/
│   │   ├── components/        # 公共组件
│   │   ├── views/             # 页面视图
│   │   ├── router/            # Vue Router
│   │   ├── stores/            # Pinia 状态管理
│   │   └── api/               # Axios 请求封装
│   ├── package.json
│   └── vite.config.ts
├── electron/                  # Electron 桌面端
│   ├── main.js                # 主进程
│   ├── preload.js             # 预加载脚本
│   └── icons/                 # 应用图标
├── tests/                     # 测试用例
│   ├── __init__.py
│   └── test_*.py
├── build/                     # 打包脚本
│   └── build_portable.py      # Windows 便携版打包
├── data/                      # 数据目录（运行时生成）
├── logs/                      # 日志目录
├── output/                    # Excel 输出目录
├── config.yaml                # 全局 YAML 配置
├── .env.example               # 环境变量示例
├── package.json               # 根目录 Node 脚本（Electron）
├── requirements.txt           # Python 根依赖
├── start.sh / start.bat       # Streamlit 启动脚本
├── start-electron.sh / .bat   # Electron 启动脚本
└── README.md                  # 说明文档
```

---

## ⚙️ 配置说明

### 环境变量（`.env`）

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `AI_API_KEY` | AI 服务 API 密钥（必填） | - |
| `AI_PROVIDER` | AI 提供商 | `deepseek` |
| `AI_MODEL` | 模型名称 | `deepseek-chat` |
| `AI_API_BASE` | API 基础地址 | `https://api.deepseek.com/v1` |
| `SECRET_KEY` | JWT 签名密钥（生产必填） | - |
| `DATABASE_URL` | 数据库连接地址 | `sqlite:///./data/params.db` |
| `HOST` / `PORT` | 后端监听地址和端口 | `0.0.0.0` / `8000` |
| `DEBUG` | 调试模式 | `false` |

### `config.yaml` 配置项

```yaml
# 界面配置
ui:
  primary_color: "#1E3A8A"      # 主题色
  default_page_size: 20         # 默认分页条数

# 性能配置
performance:
  parse_workers: 4              # PDF 解析并发进程数
  ai_timeout: 60                # AI 调用超时(秒)
  cache_ttl_hours: 24           # 缓存有效期(小时)
  enable_md5_check: true        # 启用 MD5 校验
  enable_cache: true            # 启用缓存

# 安全配置
security:
  max_login_attempts: 5         # 最大登录失败次数
  lockout_duration_minutes: 10  # 账号锁定时间

# AI 配置
ai:
  default_provider: "deepseek"
  default_model: "deepseek-chat"
  default_api_key: "${AI_API_KEY}"   # 引用环境变量
  temperature: 0
  max_tokens: 8192
```

---

## 🧪 运行测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行单个测试
python -m pytest tests/test_extraction.py
```

---

## 📦 打包构建

### 打包 Electron 桌面应用

```bash
# Windows
npm run electron:build:win

# macOS
npm run electron:build:mac

# Linux
npm run electron:build:linux
```

### 打包 Windows 便携版（Python）

```bash
cd build
python build_portable.py
```

---

## 🔧 常见问题

### Q: PDF 解析失败？

1. 确保 PDF 不是扫描版（文字可选择）
2. 检查 PDF 是否有密码保护
3. 查看 `logs/error.log` 获取详细错误信息

### Q: AI 提取结果不准确？

1. 检查参数库是否包含对应参数
2. 在参数管理中添加更多变体名称
3. 查看「精细化查看」页面的原始文本，确认 PDF 内容是否包含该参数

### Q: 忘记管理员密码？

1. 删除 `data/params.db` 文件
2. 重启系统，将自动创建默认管理员账号
3. 默认账号：`admin` / `admin123`

---

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**技术支持**：如有问题，请提交 GitHub Issue
