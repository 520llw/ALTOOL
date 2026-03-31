# -*- coding: utf-8 -*-
"""
参数管理 API 路由
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.param import StandardParam, ParamVariant
from app.schemas.param import (
    StandardParamCreate, StandardParamUpdate, StandardParamResponse,
    ParamVariantCreate, ParamVariantResponse, ParamWithVariants,
    StandardParamListResponse
)
from app.dependencies import get_current_user, get_current_active_user

router = APIRouter()


@router.get("", response_model=StandardParamListResponse)
def list_params(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    category: Optional[str] = None,
    param_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取标准参数列表
    
    - **skip**: 跳过的记录数
    - **limit**: 返回的记录数
    - **search**: 搜索关键词（参数名）
    - **category**: 参数分类筛选
    - **param_type**: 器件类型筛选
    """
    query = db.query(StandardParam)
    
    # 搜索
    if search:
        query = query.filter(
            (StandardParam.param_name.contains(search)) |
            (StandardParam.param_name_en.contains(search))
        )
    
    # 分类筛选
    if category:
        query = query.filter(StandardParam.category == category)
    
    # 器件类型筛选
    if param_type:
        query = query.filter(StandardParam.param_type.contains(param_type))
    
    total = query.count()
    params = query.order_by(StandardParam.id).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "items": [param.to_dict() for param in params]
    }


@router.post("", response_model=StandardParamResponse, status_code=status.HTTP_201_CREATED)
def create_param(
    param_data: StandardParamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    创建新标准参数
    
    - **param_name**: 参数名（必填，唯一）
    - **param_name_en**: 英文参数名（可选）
    - **param_type**: 器件类型（可选）
    - **unit**: 单位（可选）
    - **category**: 分类（可选）
    - **variants**: 变体名称列表（可选）
    """
    # 检查参数名是否已存在
    existing = db.query(StandardParam).filter(
        StandardParam.param_name == param_data.param_name
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"参数 '{param_data.param_name}' 已存在"
        )
    
    # 创建参数
    param = StandardParam(
        param_name=param_data.param_name,
        param_name_en=param_data.param_name_en,
        param_type=param_data.param_type,
        unit=param_data.unit,
        category=param_data.category
    )
    
    db.add(param)
    db.flush()  # 获取ID
    
    # 添加变体
    if param_data.variants:
        for variant_name in param_data.variants:
            if variant_name and variant_name.strip():
                variant = ParamVariant(
                    param_id=param.id,
                    variant_name=variant_name.strip()
                )
                db.add(variant)
    
    db.commit()
    db.refresh(param)
    
    return param.to_dict()


@router.get("/{param_id}", response_model=ParamWithVariants)
def get_param(
    param_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取参数详情（包含变体）
    
    - **param_id**: 参数ID
    """
    param = db.query(StandardParam).filter(StandardParam.id == param_id).first()
    if not param:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="参数不存在"
        )
    
    # 获取变体
    variants = db.query(ParamVariant).filter(
        ParamVariant.param_id == param_id
    ).all()
    
    result = param.to_dict()
    result["variants"] = [v.to_dict() for v in variants]
    
    return result


@router.put("/{param_id}", response_model=StandardParamResponse)
def update_param(
    param_id: int,
    param_data: StandardParamUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    更新标准参数
    
    - **param_name**: 参数名（可选）
    - **param_name_en**: 英文参数名（可选）
    - **param_type**: 器件类型（可选）
    - **unit**: 单位（可选）
    - **category**: 分类（可选）
    """
    param = db.query(StandardParam).filter(StandardParam.id == param_id).first()
    if not param:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="参数不存在"
        )
    
    # 检查参数名是否冲突
    if param_data.param_name and param_data.param_name != param.param_name:
        existing = db.query(StandardParam).filter(
            StandardParam.param_name == param_data.param_name
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"参数名 '{param_data.param_name}' 已存在"
            )
        param.param_name = param_data.param_name
    
    # 更新其他字段
    if param_data.param_name_en is not None:
        param.param_name_en = param_data.param_name_en
    if param_data.param_type is not None:
        param.param_type = param_data.param_type
    if param_data.unit is not None:
        param.unit = param_data.unit
    if param_data.category is not None:
        param.category = param_data.category
    
    db.commit()
    db.refresh(param)
    
    return param.to_dict()


@router.delete("/{param_id}")
def delete_param(
    param_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    删除标准参数（同时删除关联的变体）
    
    - **param_id**: 参数ID
    """
    param = db.query(StandardParam).filter(StandardParam.id == param_id).first()
    if not param:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="参数不存在"
        )
    
    db.delete(param)
    db.commit()
    
    return {"message": "参数已删除"}


# ==================== 变体管理 API ====================

@router.get("/{param_id}/variants")
def list_variants(
    param_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取参数的所有变体
    
    - **param_id**: 参数ID
    """
    param = db.query(StandardParam).filter(StandardParam.id == param_id).first()
    if not param:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="参数不存在"
        )
    
    variants = db.query(ParamVariant).filter(
        ParamVariant.param_id == param_id
    ).all()
    
    return {
        "total": len(variants),
        "items": [v.to_dict() for v in variants]
    }


@router.post("/{param_id}/variants", response_model=ParamVariantResponse, status_code=status.HTTP_201_CREATED)
def create_variant(
    param_id: int,
    variant_data: ParamVariantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    为参数添加变体
    
    - **param_id**: 参数ID
    - **variant_name**: 变体名称（必填）
    - **vendor**: 厂家（可选）
    """
    param = db.query(StandardParam).filter(StandardParam.id == param_id).first()
    if not param:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="参数不存在"
        )
    
    variant = ParamVariant(
        param_id=param_id,
        variant_name=variant_data.variant_name,
        vendor=variant_data.vendor
    )
    
    db.add(variant)
    db.commit()
    db.refresh(variant)
    
    return variant.to_dict()


@router.delete("/{param_id}/variants/{variant_id}")
def delete_variant(
    param_id: int,
    variant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    删除参数变体
    
    - **param_id**: 参数ID
    - **variant_id**: 变体ID
    """
    variant = db.query(ParamVariant).filter(
        ParamVariant.id == variant_id,
        ParamVariant.param_id == param_id
    ).first()
    
    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="变体不存在"
        )
    
    db.delete(variant)
    db.commit()
    
    return {"message": "变体已删除"}


# ==================== 批量操作 API ====================

@router.get("/categories/list")
def list_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取所有参数分类"""
    categories = db.query(StandardParam.category).distinct().all()
    return {
        "items": [c[0] for c in categories if c[0]]
    }


@router.get("/device-types/list")
def list_device_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取所有器件类型"""
    types = db.query(StandardParam.param_type).distinct().all()
    result = []
    for t in types:
        if t[0]:
            # 处理逗号分隔的多个类型
            for type_str in t[0].split(","):
                type_str = type_str.strip()
                if type_str and type_str not in result:
                    result.append(type_str)
    return {"items": result}


@router.get("/all/with-variants")
def get_all_params_with_variants(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取所有参数及其变体
    用于AI提示词生成
    """
    params = db.query(StandardParam).all()
    result = []
    
    for param in params:
        variants = db.query(ParamVariant).filter(
            ParamVariant.param_id == param.id
        ).all()
        
        param_dict = param.to_dict()
        param_dict["variants"] = [v.variant_name for v in variants]
        result.append(param_dict)
    
    return {
        "total": len(result),
        "items": result
    }
