# -*- coding: utf-8 -*-
"""
用户模型
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, comment="用户名")
    password_hash = Column(String(128), nullable=False, comment="密码哈希值(bcrypt)")
    role = Column(String(20), default="user", comment="角色(admin/user)")
    is_active = Column(Boolean, default=True, comment="是否启用")
    login_attempts = Column(Integer, default=0, comment="登录失败次数")
    locked_until = Column(DateTime, comment="锁定截止时间")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    last_login = Column(DateTime, comment="最后登录时间")
    ai_api_key = Column(String(256), nullable=True, comment="用户专属API密钥")
    
    # 关联
    logs = relationship("UserLog", back_populates="user", cascade="all, delete-orphan")
    parse_results = relationship("ParseResult", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"
    
    def to_dict(self):
        """转换为字典（不包含敏感信息）"""
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }


class UserLog(Base):
    """用户操作日志表"""
    __tablename__ = "user_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    action = Column(String(100), nullable=False, comment="操作类型(LOGIN/LOGOUT/PARSE/EXPORT等)")
    detail = Column(Text, comment="操作详情")
    ip_address = Column(String(50), comment="IP地址")
    created_at = Column(DateTime, default=datetime.now, comment="操作时间")
    
    # 关联
    user = relationship("User", back_populates="logs")
    
    def __repr__(self):
        return f"<UserLog(id={self.id}, user_id={self.user_id}, action='{self.action}')>"
