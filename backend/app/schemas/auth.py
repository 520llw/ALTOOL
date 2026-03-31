# -*- coding: utf-8 -*-
"""
认证相关 Schema
"""

from typing import Optional
from pydantic import BaseModel, Field


class Token(BaseModel):
    """Token 响应"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(default=1800, description="Access token 过期时间(秒)")


class TokenPayload(BaseModel):
    """Token 载荷"""
    sub: Optional[int] = None  # 用户ID
    exp: Optional[int] = None  # 过期时间
    type: Optional[str] = None  # token 类型: access/refresh


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=32, description="密码")
    remember_me: bool = Field(default=False, description="记住我")


class PasswordChangeRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., min_length=6, max_length=32, description="原密码")
    new_password: str = Field(..., min_length=6, max_length=32, description="新密码")


class ApiKeyUpdateRequest(BaseModel):
    """API密钥更新请求"""
    api_key: str = Field(..., description="API密钥")
