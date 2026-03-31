# -*- coding: utf-8 -*-
"""
配置管理模块
使用 Pydantic Settings 管理配置
"""

import os
from pathlib import Path
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field


# 项目根目录
BASE_DIR = Path(__file__).parent.parent.parent
BACKEND_DIR = Path(__file__).parent.parent

# 数据目录
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
OUTPUT_DIR = BASE_DIR / "output"

# 确保目录存在
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用信息
    app_name: str = "AITOOL API"
    app_version: str = "0.1.0"
    debug: bool = Field(default=False, env="DEBUG")
    
    # 服务器配置
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # 数据库配置
    database_url: str = Field(
        default=f"sqlite:///{DATA_DIR / 'params.db'}",
        env="DATABASE_URL"
    )
    
    # JWT 配置
    secret_key: str = Field(
        default="your-super-secret-key-change-this-in-production",
        env="SECRET_KEY"
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # AI 配置
    ai_provider: str = Field(default="deepseek", env="AI_PROVIDER")
    ai_model: str = Field(default="deepseek-chat", env="AI_MODEL")
    ai_api_key: str = Field(default="", env="AI_API_KEY")
    ai_api_base: str = Field(default="https://api.deepseek.com/v1", env="AI_API_BASE")
    ai_timeout: int = Field(default=60, env="AI_TIMEOUT")
    ai_max_retries: int = Field(default=3, env="AI_MAX_RETRIES")
    
    # 解析器配置
    pdf_timeout: int = Field(default=30, env="PDF_TIMEOUT")
    max_workers: int = Field(default=4, env="MAX_WORKERS")
    batch_size: int = Field(default=10, env="BATCH_SIZE")
    
    # CORS 配置
    cors_origins: List[str] = ["*"]
    
    # 安全配置
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 10
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 全局配置实例
settings = Settings()
