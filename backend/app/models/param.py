# -*- coding: utf-8 -*-
"""
参数模型
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class StandardParam(Base):
    """标准化参数表"""
    __tablename__ = "standard_params"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    param_name = Column(String(100), unique=True, nullable=False, comment="标准参数名")
    param_name_en = Column(String(200), comment="英文参数名/描述")
    param_type = Column(String(100), comment="器件类型(Si MOSFET/SiC MOSFET/IGBT)")
    unit = Column(String(50), comment="参数单位")
    category = Column(String(50), comment="参数分类(基本信息/电压/电流/电阻/电容/电荷/时间/热特性/其他)")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关联
    variants = relationship("ParamVariant", back_populates="standard_param", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<StandardParam(id={self.id}, name='{self.param_name}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "param_name": self.param_name,
            "param_name_en": self.param_name_en,
            "param_type": self.param_type,
            "unit": self.unit,
            "category": self.category,
            "create_time": self.create_time.isoformat() if self.create_time else None,
            "update_time": self.update_time.isoformat() if self.update_time else None,
        }


class ParamVariant(Base):
    """参数变体表"""
    __tablename__ = "param_variants"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    param_id = Column(Integer, ForeignKey("standard_params.id", ondelete="CASCADE"), nullable=False)
    variant_name = Column(String(200), nullable=False, comment="变体名称")
    vendor = Column(String(100), comment="对应厂家")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 关联
    standard_param = relationship("StandardParam", back_populates="variants")
    
    def __repr__(self):
        return f"<ParamVariant(id={self.id}, name='{self.variant_name}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "param_id": self.param_id,
            "variant_name": self.variant_name,
            "vendor": self.vendor,
            "create_time": self.create_time.isoformat() if self.create_time else None,
        }
