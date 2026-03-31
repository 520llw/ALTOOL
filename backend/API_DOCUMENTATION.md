# AITOOL Backend API 文档

## 概述

AITOOL 后端采用 FastAPI 框架构建，提供 RESTful API 接口供前端调用。

## 快速开始

### 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 启动服务

```bash
# 开发模式（热重载）
python -m app.main

# 或使用 uvicorn
uvicorn app.main:app --reload --port 8000
```

### 访问 API 文档

启动后访问:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 路由

### 1. 认证 API (`/api/v1/auth`)

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| POST | `/login` | 用户登录 | 否 |
| POST | `/refresh` | 刷新 Token | 否 |
| POST | `/logout` | 用户登出 | 是 |
| GET | `/me` | 获取当前用户信息 | 是 |
| PUT | `/me` | 更新当前用户信息 | 是 |
| PUT | `/me/password` | 修改密码 | 是 |
| PUT | `/me/api-key` | 设置 API 密钥 | 是 |
| GET | `/me/api-key` | 获取 API 密钥状态 | 是 |

#### 登录示例

**请求:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123",
    "remember_me": false
  }'
```

**响应:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### 使用 Token

在请求头中添加:
```
Authorization: Bearer <access_token>
```

### 2. 用户管理 API (`/api/v1/users`)

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | `/` | 获取用户列表 | Admin |
| POST | `/` | 创建用户 | Admin |
| GET | `/{user_id}` | 获取用户详情 | Admin |
| PUT | `/{user_id}` | 更新用户 | Admin |
| PUT | `/{user_id}/status` | 更新用户状态 | Admin |
| PUT | `/{user_id}/role` | 更新用户角色 | Admin |
| DELETE | `/{user_id}` | 删除用户 | Admin |
| GET | `/{user_id}/logs` | 获取用户日志 | Admin |

#### 创建用户示例

**请求:**
```bash
curl -X POST "http://localhost:8000/api/v1/users/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "username": "newuser",
    "password": "password123",
    "role": "user",
    "is_active": true
  }'
```

### 3. 参数管理 API (`/api/v1/params`)

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| GET | `/` | 获取参数列表 | 是 |
| POST | `/` | 创建参数 | 是 |
| GET | `/{param_id}` | 获取参数详情 | 是 |
| PUT | `/{param_id}` | 更新参数 | 是 |
| DELETE | `/{param_id}` | 删除参数 | 是 |
| GET | `/{param_id}/variants` | 获取变体列表 | 是 |
| POST | `/{param_id}/variants` | 添加变体 | 是 |
| DELETE | `/{param_id}/variants/{variant_id}` | 删除变体 | 是 |
| GET | `/categories/list` | 获取分类列表 | 是 |
| GET | `/device-types/list` | 获取器件类型列表 | 是 |
| GET | `/all/with-variants` | 获取所有参数及变体 | 是 |

#### 创建参数示例

**请求:**
```bash
curl -X POST "http://localhost:8000/api/v1/params/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "param_name": "VDS",
    "param_name_en": "Drain-Source Voltage",
    "param_type": "Si MOSFET",
    "unit": "V",
    "category": "电压",
    "variants": ["VDSS", "Drain-Source Breakdown Voltage"]
  }'
```

## 数据模型

### User (用户)

```json
{
  "id": 1,
  "username": "admin",
  "role": "admin",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00",
  "last_login": "2024-01-01T00:00:00"
}
```

### StandardParam (标准参数)

```json
{
  "id": 1,
  "param_name": "VDS",
  "param_name_en": "Drain-Source Voltage",
  "param_type": "Si MOSFET",
  "unit": "V",
  "category": "电压",
  "create_time": "2024-01-01T00:00:00",
  "update_time": "2024-01-01T00:00:00"
}
```

### ParamVariant (参数变体)

```json
{
  "id": 1,
  "param_id": 1,
  "variant_name": "VDSS",
  "vendor": null,
  "create_time": "2024-01-01T00:00:00"
}
```

## 错误码

| 状态码 | 描述 | 场景 |
|--------|------|------|
| 200 | 成功 | 请求成功 |
| 201 | 创建成功 | 资源创建成功 |
| 400 | 请求参数错误 | 参数验证失败 |
| 401 | 未认证 | Token 无效或缺失 |
| 403 | 权限不足 | 需要更高权限 |
| 404 | 资源不存在 | 请求的资源不存在 |
| 422 | 验证错误 | 请求体验证失败 |
| 500 | 服务器错误 | 内部服务器错误 |

## 配置说明

### 环境变量

| 变量名 | 默认值 | 描述 |
|--------|--------|------|
| `DEBUG` | `false` | 调试模式 |
| `HOST` | `0.0.0.0` | 服务监听地址 |
| `PORT` | `8000` | 服务端口 |
| `DATABASE_URL` | `sqlite:///./data/params.db` | 数据库连接 URL |
| `SECRET_KEY` | - | JWT 密钥（生产环境必须修改） |
| `AI_PROVIDER` | `deepseek` | AI 提供商 |
| `AI_API_KEY` | - | AI API 密钥 |

### 配置文件

复制 `.env.example` 为 `.env` 并修改配置:

```bash
cp .env.example .env
```

## 默认账号

系统启动时会自动创建默认管理员账号:

- **用户名**: `admin`
- **密码**: `admin123`

**生产环境请务必修改默认密码！**

## 数据库迁移

使用 Alembic 进行数据库迁移:

```bash
# 创建迁移
cd backend
alembic revision --autogenerate -m "description"

# 执行迁移
alembic upgrade head

# 回滚
alembic downgrade -1
```
