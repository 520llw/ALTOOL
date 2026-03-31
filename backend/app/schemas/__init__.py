# -*- coding: utf-8 -*-
"""
Pydantic Schema 模块
"""

from app.schemas.auth import Token, TokenPayload, LoginRequest
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserInDB, UserListResponse
from app.schemas.param import (
    StandardParamCreate, StandardParamUpdate, StandardParamResponse,
    ParamVariantCreate, ParamVariantResponse, ParamWithVariants
)
from app.schemas.common import ResponseModel, PaginatedResponse, MessageResponse

__all__ = [
    # Auth
    "Token",
    "TokenPayload",
    "LoginRequest",
    # User
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserInDB",
    "UserListResponse",
    # Param
    "StandardParamCreate",
    "StandardParamUpdate",
    "StandardParamResponse",
    "ParamVariantCreate",
    "ParamVariantResponse",
    "ParamWithVariants",
    # Common
    "ResponseModel",
    "PaginatedResponse",
    "MessageResponse",
]
