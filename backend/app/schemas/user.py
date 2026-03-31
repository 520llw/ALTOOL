# -*- coding: utf-8 -*-
"""
用户相关 Schema
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    """用户基础信息"""
    username: str = Field(..., min_length=3, max_length=50)
    role: str = Field(default="user", pattern="^(admin|user)$")
    is_active: bool = True


class UserCreate(UserBase):
    """创建用户请求"""
    password: str = Field(..., min_length=6, max_length=32)


class UserUpdate(BaseModel):
    """更新用户请求"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    role: Optional[str] = Field(None, pattern="^(admin|user)$")
    is_active: Optional[bool] = None


class UserStatusUpdate(BaseModel):
    """更新用户状态请求"""
    is_active: bool


class UserRoleUpdate(BaseModel):
    """更新用户角色请求"""
    role: str = Field(..., pattern="^(admin|user)$")


class UserResponse(BaseModel):
    """用户响应"""
    id: int
    username: str
    role: str
    is_active: bool
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserInDB(UserBase):
    """数据库中的用户（包含敏感信息）"""
    id: int
    password_hash: str
    login_attempts: int = 0
    locked_until: Optional[datetime] = None
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    ai_api_key: Optional[str] = None
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """用户列表响应"""
    total: int
    items: List[UserResponse]


class UserMeResponse(UserResponse):
    """当前用户信息响应（包含API密钥）"""
    has_api_key: bool = False
