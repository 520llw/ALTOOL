# -*- coding: utf-8 -*-
"""
安全模块
处理密码加密、JWT Token 生成与验证
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.models.user import User

# 密码上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def hash_password(password: str) -> str:
    """哈希密码"""
    return pwd_context.hash(password)


def create_access_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建访问令牌
    
    Args:
        user_id: 用户ID
        expires_delta: 过期时间
    
    Returns:
        JWT Token 字符串
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access",
        "iat": datetime.utcnow()
    }
    
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def create_refresh_token(user_id: int) -> str:
    """
    创建刷新令牌
    
    Args:
        user_id: 用户ID
    
    Returns:
        JWT Refresh Token 字符串
    """
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh",
        "iat": datetime.utcnow()
    }
    
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """
    解码 JWT Token
    
    Args:
        token: JWT Token 字符串
    
    Returns:
        Token 载荷，如果无效则返回 None
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None


def authenticate_user(db: Session, username: str, password: str) -> Tuple[bool, str, Optional[User]]:
    """
    认证用户
    
    Args:
        db: 数据库会话
        username: 用户名
        password: 密码
    
    Returns:
        (是否成功, 消息, 用户对象)
    """
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        return False, "用户名或密码错误", None
    
    if not user.is_active:
        return False, "账号已被禁用，请联系管理员", None
    
    # 检查是否被锁定
    if user.locked_until and user.locked_until > datetime.now():
        remaining = int((user.locked_until - datetime.now()).total_seconds() // 60)
        return False, f"账号已被锁定，请{remaining + 1}分钟后再试", None
    
    # 验证密码
    if not verify_password(password, user.password_hash):
        # 增加失败次数
        user.login_attempts += 1
        
        # 达到最大失败次数，锁定账号
        if user.login_attempts >= settings.max_login_attempts:
            user.locked_until = datetime.now() + timedelta(minutes=settings.lockout_duration_minutes)
            db.commit()
            return False, f"密码错误次数过多，账号已锁定{settings.lockout_duration_minutes}分钟", None
        
        db.commit()
        remaining = settings.max_login_attempts - user.login_attempts
        return False, f"密码错误，还剩{remaining}次机会", None
    
    # 登录成功，重置失败次数
    user.login_attempts = 0
    user.locked_until = None
    user.last_login = datetime.now()
    db.commit()
    
    return True, "登录成功", user


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    验证密码强度
    
    Args:
        password: 密码
    
    Returns:
        (是否合格, 提示信息)
    """
    if len(password) < 6:
        return False, "密码长度至少6位"
    if len(password) > 32:
        return False, "密码长度不能超过32位"
    return True, "密码强度合格"
