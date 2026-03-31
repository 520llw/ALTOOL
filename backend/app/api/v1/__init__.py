# -*- coding: utf-8 -*-
"""
API v1 模块
"""

from fastapi import APIRouter

from app.api.v1 import auth, users, params

api_router = APIRouter(prefix="/api/v1")

# 注册路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户"])
api_router.include_router(params.router, prefix="/params", tags=["参数管理"])
