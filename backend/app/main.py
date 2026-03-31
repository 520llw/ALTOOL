# -*- coding: utf-8 -*-
"""
FastAPI 应用入口
"""

import sys
from pathlib import Path

# 确保可以导入 backend 模块
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db
from app.api.v1 import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    """
    # 启动时执行
    print("🚀 正在初始化数据库...")
    init_db()
    print("✅ 数据库初始化完成")
    
    yield
    
    # 关闭时执行
    print("👋 正在关闭应用...")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AITOOL API - PDF参数提取与管理",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["根路径"])
def root():
    """根路径 - 服务健康检查"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health", tags=["健康检查"])
def health_check():
    """健康检查端点"""
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "healthy",
            "version": settings.app_version
        }
    )


# 注册 API 路由
app.include_router(api_router)


# 初始化默认管理员
@app.on_event("startup")
def init_default_admin():
    """初始化默认管理员账号"""
    from sqlalchemy.orm import Session
    from app.database import SessionLocal
    from app.models.user import User
    from app.core.security import hash_password
    
    db = SessionLocal()
    try:
        # 检查是否已存在 admin 用户
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            # 创建默认管理员
            admin = User(
                username="admin",
                password_hash=hash_password("admin123"),
                role="admin",
                is_active=True
            )
            db.add(admin)
            db.commit()
            print("✅ 已创建默认管理员账号: admin / admin123")
        else:
            print("ℹ️ 管理员账号已存在")
    except Exception as e:
        print(f"❌ 初始化管理员失败: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
