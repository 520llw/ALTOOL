# -*- coding: utf-8 -*-
"""
通用 Schema
"""

from typing import Optional, Generic, TypeVar, List
from pydantic import BaseModel

T = TypeVar("T")


class MessageResponse(BaseModel):
    """消息响应"""
    message: str


class ResponseModel(BaseModel, Generic[T]):
    """通用响应模型"""
    code: int = 200
    message: str = "success"
    data: Optional[T] = None


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应模型"""
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool
    items: List[T]
