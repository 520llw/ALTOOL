# -*- coding: utf-8 -*-
"""
用户管理 API 路由
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserLog
from app.schemas.user import (
    UserCreate, UserUpdate, UserResponse, UserListResponse,
    UserStatusUpdate, UserRoleUpdate
)
from app.core.security import hash_password, validate_password_strength
from app.dependencies import get_current_user, get_current_admin

router = APIRouter()


@router.get("", response_model=UserListResponse)
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    获取用户列表（管理员权限）
    
    - **skip**: 跳过的记录数
    - **limit**: 返回的记录数
    - **search**: 搜索关键词（用户名）
    """
    query = db.query(User)
    
    # 搜索
    if search:
        query = query.filter(User.username.contains(search))
    
    total = query.count()
    users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "items": [user.to_dict() for user in users]
    }


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    创建新用户（管理员权限）
    
    - **username**: 用户名（3-50字符）
    - **password**: 密码（6-32字符）
    - **role**: 角色（admin/user，默认user）
    - **is_active**: 是否启用（默认true）
    """
    # 检查用户名是否已存在
    existing = db.query(User).filter(User.username == user_data.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 验证密码强度
    valid, msg = validate_password_strength(user_data.password)
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg
        )
    
    # 创建用户
    user = User(
        username=user_data.username,
        password_hash=hash_password(user_data.password),
        role=user_data.role,
        is_active=user_data.is_active
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user.to_dict()


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    获取用户详情（管理员权限）
    
    - **user_id**: 用户ID
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return user.to_dict()


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    更新用户信息（管理员权限）
    
    - **username**: 用户名（可选）
    - **role**: 角色（可选，admin/user）
    - **is_active**: 是否启用（可选）
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 检查用户名是否冲突
    if user_data.username and user_data.username != user.username:
        existing = db.query(User).filter(User.username == user_data.username).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        user.username = user_data.username
    
    # 更新其他字段
    if user_data.role:
        user.role = user_data.role
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    
    db.commit()
    db.refresh(user)
    
    return user.to_dict()


@router.put("/{user_id}/status")
def update_user_status(
    user_id: int,
    data: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    更新用户状态（启用/禁用）
    
    - **is_active**: 是否启用
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 不能禁用自己
    if user.id == current_user.id and not data.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能禁用当前登录的管理员账号"
        )
    
    user.is_active = data.is_active
    db.commit()
    
    return {
        "message": f"用户已{'启用' if data.is_active else '禁用'}"
    }


@router.put("/{user_id}/role")
def update_user_role(
    user_id: int,
    data: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    更新用户角色
    
    - **role**: 角色（admin/user）
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    user.role = data.role
    db.commit()
    
    return {
        "message": f"用户角色已更新为 {data.role}"
    }


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    删除用户（管理员权限）
    
    - **user_id**: 用户ID
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 不能删除自己
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除当前登录的管理员账号"
        )
    
    db.delete(user)
    db.commit()
    
    return {"message": "用户已删除"}


@router.get("/{user_id}/logs")
def get_user_logs(
    user_id: int,
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    获取用户操作日志（管理员权限）
    
    - **user_id**: 用户ID
    - **limit**: 返回记录数
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    logs = db.query(UserLog).filter(
        UserLog.user_id == user_id
    ).order_by(UserLog.created_at.desc()).limit(limit).all()
    
    return {
        "total": len(logs),
        "items": [
            {
                "id": log.id,
                "action": log.action,
                "detail": log.detail,
                "ip_address": log.ip_address,
                "created_at": log.created_at.isoformat() if log.created_at else None
            }
            for log in logs
        ]
    }
