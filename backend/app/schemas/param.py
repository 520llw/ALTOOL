# -*- coding: utf-8 -*-
"""
参数相关 Schema
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ==================== 参数变体 Schema ====================

class ParamVariantBase(BaseModel):
    """参数变体基础"""
    variant_name: str = Field(..., max_length=200)
    vendor: Optional[str] = Field(None, max_length=100)


class ParamVariantCreate(ParamVariantBase):
    """创建参数变体"""
    pass


class ParamVariantResponse(ParamVariantBase):
    """参数变体响应"""
    id: int
    param_id: int
    create_time: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ==================== 标准参数 Schema ====================

class StandardParamBase(BaseModel):
    """标准参数基础"""
    param_name: str = Field(..., max_length=100)
    param_name_en: Optional[str] = Field(None, max_length=200)
    param_type: Optional[str] = Field(None, max_length=100)
    unit: Optional[str] = Field(None, max_length=50)
    category: Optional[str] = Field(None, max_length=50)


class StandardParamCreate(StandardParamBase):
    """创建标准参数"""
    variants: Optional[List[str]] = Field(default=[], description="变体名称列表")


class StandardParamUpdate(BaseModel):
    """更新标准参数"""
    param_name: Optional[str] = Field(None, max_length=100)
    param_name_en: Optional[str] = Field(None, max_length=200)
    param_type: Optional[str] = Field(None, max_length=100)
    unit: Optional[str] = Field(None, max_length=50)
    category: Optional[str] = Field(None, max_length=50)


class StandardParamResponse(StandardParamBase):
    """标准参数响应"""
    id: int
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ParamWithVariants(StandardParamResponse):
    """带变体的参数响应"""
    variants: List[ParamVariantResponse] = []


class StandardParamListResponse(BaseModel):
    """标准参数列表响应"""
    total: int
    items: List[StandardParamResponse]


# ==================== 参数初始化 Schema ====================

class ParamInitFromExcelRequest(BaseModel):
    """从Excel初始化参数请求"""
    file_path: str = Field(..., description="Excel文件路径")
    device_type: Optional[str] = Field(None, description="器件类型")
    clear_existing: bool = Field(default=False, description="是否清空现有数据")


class ParamInitResponse(BaseModel):
    """参数初始化响应"""
    imported_count: int
    skipped_count: int
    message: str
