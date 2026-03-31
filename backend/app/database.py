# -*- coding: utf-8 -*-
"""
数据库连接模块
SQLAlchemy 异步数据库配置
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.config import settings

# 创建同步引擎（SQLite 在异步模式下有一些限制，这里使用同步模式）
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
    poolclass=StaticPool if settings.database_url.startswith("sqlite") else None,
    echo=settings.debug
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明性基类
Base = declarative_base()


def get_db() -> Session:
    """
    获取数据库会话（同步版本）
    用于 FastAPI 依赖注入
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库，创建所有表"""
    Base.metadata.create_all(bind=engine)
