# AITOOL 项目技术栈重构方案

## 一、当前项目分析

### 1.1 现状问题

| 问题 | 现状 | 影响 |
|------|------|------|
| **前端臃肿** | main.py 2713行，包含所有页面逻辑 | 难以维护，协作困难 |
| **前后端耦合** | Streamlit 混合UI和业务逻辑 | 无法分离部署，扩展性差 |
| **测试文件混乱** | 12个test_*.py散落在根目录 | 项目结构不清晰 |
| **前端组件缺失** | frontend/ 仅有一个__init__.py | 前端未真正组件化 |
| **数据库限制** | SQLite单文件 | 并发性能受限 |
| **Electron未完成** | 有electron目录但整合度低 | 桌面版体验不佳 |

### 1.2 功能模块梳理

```
系统功能 (6大模块):
├── 📋 解析任务 - PDF批量上传、解析、进度显示
├── 📊 数据中心 - 解析结果查看、搜索、详情
├── 📦 参数管理 - 标准参数库、变体管理
├── 📤 生成表格 - Excel导出、分Sheet
├── ⚙️ 系统设置 - AI配置、备份、日志
└── 👤 个人中心 - 用户信息、密码修改、用户管理(管理员)

核心业务流程:
PDF上传 → 文本提取 → AI参数提取 → 数据存储 → Excel导出
```

---

## 二、技术选型建议

### 2.1 方案对比

| 方案 | 架构 | 优点 | 缺点 | 推荐度 |
|------|------|------|------|--------|
| **A. 保留Streamlit** | 单体 | 开发快，无需前端 | 扩展性差，UI受限 | ⭐⭐ |
| **B. Vue3+FastAPI** | 前后端分离 | 灵活，可扩展 | 开发成本较高 | ⭐⭐⭐⭐ |
| **C. React+FastAPI** | 前后端分离 | 生态丰富 | 学习曲线陡 | ⭐⭐⭐⭐ |
| **D. Tauri桌面应用** | 桌面优先 | 体积小，性能好 | 生态较新 | ⭐⭐⭐ |

### 2.2 推荐方案: Vue3 + FastAPI + Electron

**选型理由:**
1. **Vue3**: 中文文档友好，适合国内团队，Element Plus组件库丰富
2. **FastAPI**: 异步高性能，自动API文档，类型提示友好
3. **SQLAlchemy**: 保持ORM，支持SQLite/PostgreSQL切换
4. **Electron**: 已有基础，可打包桌面应用

---

## 三、重构后的架构设计

### 3.1 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                     客户端层 (Client)                        │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Web浏览器   │  │ Electron桌面  │  │   移动端(未来) │      │
│  │   (Vue3 SPA) │  │   应用        │  │              │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼─────────────────┼─────────────────┼──────────────┘
          │                 │                 │
          └─────────────────┴─────────────────┘
                            │
                    HTTP/WebSocket
                            │
┌───────────────────────────┼─────────────────────────────────┐
│                      API 层 (FastAPI)                        │
├───────────────────────────┼─────────────────────────────────┤
│                           │                                 │
│   ┌───────────────┐  ┌────┴────┐  ┌───────────────┐        │
│   │   认证模块     │  │  路由层  │  │   权限控制     │        │
│   │   (JWT)       │  │(REST API)│  │   (RBAC)      │        │
│   └───────────────┘  └────┬────┘  └───────────────┘        │
│                           │                                 │
│   ┌───────────────────────┼───────────────────────────┐    │
│   │                   业务逻辑层 (Service)              │    │
│   │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │    │
│   │  │PDF解析   │ │AI处理    │ │数据导出  │ │用户管理│ │    │
│   │  │Service   │ │Service   │ │Service   │ │Service │ │    │
│   │  └──────────┘ └──────────┘ └──────────┘ └────────┘ │    │
│   └───────────────────────┬───────────────────────────┘    │
│                           │                                 │
│   ┌───────────────────────┼───────────────────────────┐    │
│   │                   数据访问层 (Repository)           │    │
│   │  ┌──────────┐ ┌──────────┐ ┌──────────┐          │    │
│   │  │ParamRepo │ │UserRepo  │ │ParseRepo │ ...      │    │
│   │  └──────────┘ └──────────┘ └──────────┘          │    │
│   └───────────────────────┬───────────────────────────┘    │
│                           │                                 │
└───────────────────────────┼─────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────┐
│                      数据层 (Data)                           │
│   ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│   │ SQLite   │ │PostgreSQL│ │  Redis   │ │本地文件  │      │
│   │(桌面版)  │ │(Web版)   │ │(缓存)    │ │(PDF/Excel)│     │
│   └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 核心API设计

```yaml
# API 路由结构
/api/v1/
├── /auth
│   ├── POST /login              # 登录
│   ├── POST /register           # 注册
│   ├── POST /refresh            # 刷新token
│   └── POST /logout             # 登出
│
├── /users
│   ├── GET /me                  # 当前用户信息
│   ├── PUT /me                  # 更新信息
│   ├── PUT /me/password         # 修改密码
│   ├── PUT /me/api-key          # 设置AI API密钥
│   ├── GET /                    # 用户列表(管理员)
│   ├── POST /                   # 创建用户(管理员)
│   └── PUT /{id}/status         # 禁用/启用(管理员)
│
├── /params
│   ├── GET /                    # 参数列表
│   ├── POST /                   # 新增参数
│   ├── PUT /{id}                # 更新参数
│   ├── DELETE /{id}             # 删除参数
│   ├── GET /variants            # 参数变体列表
│   └── POST /init-from-excel    # 从Excel初始化
│
├── /parse
│   ├── POST /upload             # 上传PDF
│   ├── POST /start              # 开始解析
│   ├── GET /progress/{task_id}  # 获取进度(WebSocket)
│   ├── POST /cancel/{task_id}   # 取消解析
│   └── GET /results             # 解析结果列表
│
├── /data
│   ├── GET /pdfs                # PDF列表
│   ├── GET /pdfs/{name}/params  # PDF参数详情
│   ├── GET /search              # 搜索参数
│   └── DELETE /pdfs/{name}      # 删除解析记录
│
├── /export
│   ├── POST /excel              # 导出Excel
│   └── GET /download/{file_id}  # 下载文件
│
└── /system
    ├── GET /settings            # 系统设置
    ├── PUT /settings            # 更新设置
    ├── POST /backup             # 手动备份
    ├── GET /logs                # 日志列表
    └── GET /stats               # 统计数据
```

---

## 四、重构后目录结构

```
AITOOL/
├── README.md                           # 项目说明
├── docker-compose.yml                  # Docker部署配置
├── .env.example                        # 环境变量示例
├── .gitignore
│
├── backend/                            # 后端代码 (FastAPI)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                     # FastAPI入口
│   │   ├── config.py                   # 配置管理
│   │   ├── dependencies.py             # 依赖注入
│   │   ├── database.py                 # 数据库连接
│   │   │
│   │   ├── api/                        # API路由层
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py             # 认证API
│   │   │   │   ├── users.py            # 用户API
│   │   │   │   ├── params.py           # 参数管理API
│   │   │   │   ├── parse.py            # 解析任务API
│   │   │   │   ├── data.py             # 数据查询API
│   │   │   │   ├── export.py           # 导出API
│   │   │   │   └── system.py           # 系统API
│   │   │   └── deps.py                 # 通用依赖
│   │   │
│   │   ├── services/                   # 业务逻辑层
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py         # 认证服务
│   │   │   ├── user_service.py         # 用户服务
│   │   │   ├── param_service.py        # 参数服务
│   │   │   ├── pdf_service.py          # PDF解析服务
│   │   │   ├── ai_service.py           # AI处理服务
│   │   │   ├── export_service.py       # 导出服务
│   │   │   └── cache_service.py        # 缓存服务
│   │   │
│   │   ├── repositories/               # 数据访问层
│   │   │   ├── __init__.py
│   │   │   ├── base.py                 # 基础Repository
│   │   │   ├── user_repo.py
│   │   │   ├── param_repo.py
│   │   │   ├── parse_repo.py
│   │   │   └── log_repo.py
│   │   │
│   │   ├── models/                     # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── user.py                 # 用户模型
│   │   │   ├── param.py                # 参数模型
│   │   │   ├── parse.py                # 解析结果模型
│   │   │   └── system.py               # 系统配置模型
│   │   │
│   │   ├── schemas/                    # Pydantic模型
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                 # 认证Schema
│   │   │   ├── user.py                 # 用户Schema
│   │   │   ├── param.py                # 参数Schema
│   │   │   ├── parse.py                # 解析Schema
│   │   │   └── common.py               # 通用Schema
│   │   │
│   │   ├── core/                       # 核心组件
│   │   │   ├── __init__.py
│   │   │   ├── security.py             # JWT/密码处理
│   │   │   ├── exceptions.py           # 自定义异常
│   │   │   ├── middleware.py           # 中间件
│   │   │   └── logging.py              # 日志配置
│   │   │
│   │   └── utils/                      # 工具函数
│   │       ├── __init__.py
│   │       ├── pdf_parser.py           # PDF解析
│   │       ├── ai_processor.py         # AI调用
│   │       ├── excel_writer.py         # Excel写入
│   │       └── helpers.py              # 辅助函数
│   │
│   ├── alembic/                        # 数据库迁移
│   │   ├── versions/
│   │   ├── env.py
│   │   └── alembic.ini
│   │
│   ├── device_configs/                 # 器件配置
│   │   ├── si_mosfet.yaml
│   │   ├── sic_mosfet.yaml
│   │   └── igbt.yaml
│   │
│   ├── requirements.txt                # Python依赖
│   ├── pyproject.toml                  # Poetry配置
│   └── Dockerfile                      # 后端Docker镜像
│
├── frontend/                           # 前端代码 (Vue3)
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── index.html
│   │
│   ├── src/
│   │   ├── main.ts                     # 入口文件
│   │   ├── App.vue                     # 根组件
│   │   ├── env.d.ts
│   │   │
│   │   ├── api/                        # API客户端
│   │   │   ├── index.ts                # axios实例
│   │   │   ├── auth.ts                 # 认证API
│   │   │   ├── user.ts                 # 用户API
│   │   │   ├── param.ts                # 参数API
│   │   │   ├── parse.ts                # 解析API
│   │   │   ├── data.ts                 # 数据API
│   │   │   └── system.ts               # 系统API
│   │   │
│   │   ├── components/                 # 公共组件
│   │   │   ├── common/                 # 通用组件
│   │   │   │   ├── AppHeader.vue
│   │   │   │   ├── AppSidebar.vue
│   │   │   │   ├── DataTable.vue
│   │   │   │   ├── SearchForm.vue
│   │   │   │   └── Pagination.vue
│   │   │   │
│   │   │   ├── parse/                  # 解析相关组件
│   │   │   │   ├── UploadArea.vue
│   │   │   │   ├── ProgressBar.vue
│   │   │   │   ├── ParseResultCard.vue
│   │   │   │   └── DeviceTypeSelect.vue
│   │   │   │
│   │   │   ├── params/                 # 参数管理组件
│   │   │   │   ├── ParamForm.vue
│   │   │   │   ├── VariantList.vue
│   │   │   │   └── ParamImport.vue
│   │   │   │
│   │   │   └── data/                   # 数据展示组件
│   │   │       ├── PDFCard.vue
│   │   │       ├── ParamTable.vue
│   │   │       └── CompletenessChart.vue
│   │   │
│   │   ├── views/                      # 页面视图
│   │   │   ├── LoginView.vue           # 登录页
│   │   │   ├── Layout.vue              # 布局框架
│   │   │   ├── DashboardView.vue       # 仪表盘
│   │   │   ├── ParseTaskView.vue       # 解析任务
│   │   │   ├── DataCenterView.vue      # 数据中心
│   │   │   ├── ParamManageView.vue     # 参数管理
│   │   │   ├── ExportView.vue          # 生成表格
│   │   │   ├── SettingsView.vue        # 系统设置
│   │   │   └── ProfileView.vue         # 个人中心
│   │   │
│   │   ├── stores/                     # Pinia状态管理
│   │   │   ├── index.ts
│   │   │   ├── auth.ts                 # 认证状态
│   │   │   ├── user.ts                 # 用户状态
│   │   │   ├── parse.ts                # 解析任务状态
│   │   │   └── settings.ts             # 设置状态
│   │   │
│   │   ├── router/                     # Vue Router
│   │   │   └── index.ts
│   │   │
│   │   ├── composables/                # 组合式函数
│   │   │   ├── useAuth.ts
│   │   │   ├── useParse.ts
│   │   │   ├── useWebSocket.ts
│   │   │   └── useTable.ts
│   │   │
│   │   ├── utils/                      # 工具函数
│   │   │   ├── format.ts               # 格式化
│   │   │   ├── validate.ts             # 验证
│   │   │   └── storage.ts              # 本地存储
│   │   │
│   │   ├── styles/                     # 样式文件
│   │   │   ├── variables.scss          # SCSS变量
│   │   │   ├── mixins.scss             # 混入
│   │   │   └── global.scss             # 全局样式
│   │   │
│   │   └── types/                      # TypeScript类型
│   │       ├── auth.ts
│   │       ├── user.ts
│   │       ├── param.ts
│   │       └── common.ts
│   │
│   ├── public/                         # 静态资源
│   └── Dockerfile                      # 前端Docker镜像
│
├── electron/                           # 桌面应用
│   ├── package.json
│   ├── main.js                         # 主进程
│   ├── preload.js                      # 预加载脚本
│   ├── renderer/                       # 渲染进程(引入frontend构建产物)
│   ├── build/                          # 构建配置
│   └── resources/                      # 应用资源
│
├── tests/                              # 测试代码
│   ├── unit/                           # 单元测试
│   │   ├── backend/                    # 后端单元测试
│   │   └── frontend/                   # 前端单元测试
│   ├── integration/                    # 集成测试
│   └── e2e/                            # 端到端测试
│
├── scripts/                            # 脚本工具
│   ├── setup.sh                        # 环境初始化
│   ├── dev.sh                          # 开发启动
│   ├── build.sh                        # 构建脚本
│   └── deploy.sh                       # 部署脚本
│
└── docs/                               # 文档
    ├── api.md                          # API文档
    ├── development.md                  # 开发指南
    └── deployment.md                   # 部署文档
```

---

## 五、迁移策略

### 5.1 阶段划分

```
Phase 1: 后端重构 (2-3周)
├── 搭建FastAPI框架
├── 迁移数据模型(SQLAlchemy)
├── 实现核心业务逻辑
├── API接口开发
└── 单元测试

Phase 2: 前端重构 (2-3周)
├── 搭建Vue3项目
├── 实现基础组件
├── 页面开发
├── API对接
└── 单元测试

Phase 3: 整合测试 (1周)
├── 集成测试
├── 性能优化
├── Bug修复
└── 文档更新

Phase 4: Electron打包 (1周)
├── 整合前后端
├── 桌面功能适配
├── 打包测试
└── 发布准备
```

### 5.2 风险缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| AI提取逻辑迁移 | 高 | 保留原有prompt，渐进式优化 |
| 数据库迁移 | 中 | 保持SQLite兼容，提供迁移脚本 |
| 用户体验变化 | 中 | 保留原有UI布局，逐步优化 |
| 性能回归 | 中 | 建立性能基准，对比测试 |

---

## 六、依赖清单

### 6.1 后端依赖 (requirements.txt)

```
# Web框架
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
python-multipart>=0.0.6

# 数据库
sqlalchemy>=2.0.0
alembic>=1.13.0
aiosqlite>=0.19.0  # SQLite异步
# asyncpg>=0.29.0  # PostgreSQL异步(可选)

# 认证安全
pyjwt>=2.8.0
passlib[bcrypt]>=1.7.4
python-jose[cryptography]>=3.3.0

# AI调用
openai>=1.0.0
dashscope>=1.14.0
aiohttp>=3.9.0

# PDF解析
pdfplumber>=0.10.0
pymupdf>=1.23.0

# 数据处理
pandas>=2.0.0
openpyxl>=3.1.0

# 配置/工具
pydantic>=2.5.0
pydantic-settings>=2.1.0
pyyaml>=6.0.0
python-dotenv>=1.0.0

# 日志/监控
loguru>=0.7.0
prometheus-client>=0.19.0  # 可选

# 缓存(可选)
# redis>=5.0.0
# aioredis>=2.9.0

# 测试
pytest>=7.4.0
pytest-asyncio>=0.21.0
httpx>=0.26.0  # 测试客户端
```

### 6.2 前端依赖 (package.json)

```json
{
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.0",
    "pinia": "^2.1.0",
    "axios": "^1.6.0",
    "element-plus": "^2.5.0",
    "@element-plus/icons-vue": "^2.3.0",
    "echarts": "^5.4.0",
    "vue-echarts": "^6.6.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "typescript": "^5.3.0",
    "vue-tsc": "^1.8.0",
    "vite": "^5.0.0",
    "sass": "^1.69.0",
    "@types/node": "^20.10.0",
    "vitest": "^1.1.0",
    "@vue/test-utils": "^2.4.0"
  }
}
```

---

## 七、快速开始指南

### 7.1 开发环境启动

```bash
# 1. 克隆项目
git clone <repo>
cd AITOOL

# 2. 启动后端
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 3. 启动前端(新终端)
cd frontend
npm install
npm run dev

# 4. 访问
# Web: http://localhost:5173
# API文档: http://localhost:8000/docs
```

### 7.2 Electron桌面版启动

```bash
cd electron
npm install
npm run start
```

---

## 八、性能优化建议

### 8.1 后端优化

1. **异步处理**: PDF解析和AI调用使用异步IO
2. **连接池**: 数据库连接池配置
3. **缓存策略**: Redis缓存热点数据
4. **分页优化**: 大数据集分页查询
5. **WebSocket**: 实时进度推送

### 8.2 前端优化

1. **懒加载**: 路由懒加载，组件按需加载
2. **虚拟列表**: 大数据表格虚拟滚动
3. **防抖节流**: 搜索输入防抖
4. **状态管理**: Pinia模块化，避免不必要的响应
5. **CDN**: 生产环境静态资源CDN

---

## 九、总结

本次重构将项目从Streamlit单体架构演进为Vue3+FastAPI前后端分离架构，主要收益:

| 维度 | 改进 |
|------|------|
| **可维护性** | 前后端分离，代码职责清晰 |
| **可扩展性** | 模块化设计，易于添加新功能 |
| **用户体验** | Vue3响应式，交互更流畅 |
| **部署灵活** | 支持Web、桌面多种部署方式 |
| **团队协作** | 前后端可并行开发 |

**建议优先级**:
1. 🔴 高: 后端FastAPI重构 + 数据库迁移
2. 🟡 中: 前端Vue3重构
3. 🟢 低: Electron桌面版整合
