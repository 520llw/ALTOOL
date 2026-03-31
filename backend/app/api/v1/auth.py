# -*- coding: utf-8 -*-
"""
认证 API 路由
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from jose import JWTError

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.schemas.auth import Token, LoginRequest, PasswordChangeRequest, ApiKeyUpdateRequest
from app.schemas.user import UserMeResponse
from app.core.security import (
    authenticate_user, create_access_token, create_refresh_token,
    decode_token, hash_password, verify_password, validate_password_strength
)
from app.dependencies import get_current_user

router = APIRouter()
security = HTTPBearer()


@router.post("/login", response_model=Token)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    用户登录
    
    - **username**: 用户名
    - **password**: 密码
    - **remember_me**: 是否记住我（延长token有效期）
    """
    success, message, user = authenticate_user(
        db, login_data.username, login_data.password
    )
    
    if not success or not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message,
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 根据 remember_me 设置 token 过期时间
    if login_data.remember_me:
        access_token_expires = timedelta(days=7)
    else:
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    
    access_token = create_access_token(user.id, expires_delta=access_token_expires)
    refresh_token = create_refresh_token(user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": int(access_token_expires.total_seconds())
    }


@router.post("/refresh", response_model=Token)
def refresh_token(
    credentials: str,
    db: Session = Depends(get_db)
):
    """
    刷新访问令牌
    
    - **credentials**: Refresh Token
    """
    payload = decode_token(credentials)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = int(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被禁用",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 生成新的 token
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60
    }


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """
    用户登出
    
    前端应清除本地存储的 token
    """
    # 这里可以添加 token 黑名单逻辑
    return {"message": "登出成功"}


@router.get("/me", response_model=UserMeResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
        "last_login": current_user.last_login,
        "has_api_key": bool(current_user.ai_api_key)
    }


@router.put("/me")
def update_me(
    user_update: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新当前用户信息"""
    # 只允许更新特定字段
    allowed_fields = ["username"]
    
    for field, value in user_update.items():
        if field in allowed_fields and hasattr(current_user, field):
            setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return {"message": "更新成功"}


@router.put("/me/password")
def change_password(
    data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    修改当前用户密码
    
    - **old_password**: 原密码
    - **new_password**: 新密码
    """
    # 验证原密码
    if not verify_password(data.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="原密码错误"
        )
    
    # 验证新密码强度
    valid, msg = validate_password_strength(data.new_password)
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg
        )
    
    # 更新密码
    current_user.password_hash = hash_password(data.new_password)
    db.commit()
    
    return {"message": "密码修改成功"}


@router.put("/me/api-key")
def update_api_key(
    data: ApiKeyUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    设置/更新用户专属 API 密钥
    
    - **api_key**: API 密钥（传空字符串则清除）
    """
    current_user.ai_api_key = data.api_key if data.api_key else None
    db.commit()
    
    return {
        "message": "API密钥已更新" if data.api_key else "API密钥已清除",
        "has_api_key": bool(data.api_key)
    }


@router.get("/me/api-key")
def get_api_key(
    current_user: User = Depends(get_current_user)
):
    """获取当前用户 API 密钥（仅显示是否存在，不返回实际密钥）"""
    return {
        "has_api_key": bool(current_user.ai_api_key)
    }
