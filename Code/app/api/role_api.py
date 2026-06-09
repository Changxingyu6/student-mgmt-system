"""
角色管理 API
提供角色的查询接口（角色固定写死，不可增删改）
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import get_db
from utils import format_response
from services import role_service
from utils.decorators import require_roles
from schema.role import *
from schema.base import ApiResponse

router = APIRouter(prefix="/roles", tags=["角色管理"])


@router.get("", response_model=ApiResponse[RoleListResponse], summary="获取角色列表")
@require_roles()  # 只有 admin 能访问
def get_role_list(request: Request, db: Session = Depends(get_db)):
    """获取所有角色列表"""
    result = role_service.get_all_roles(db)
    return format_response(data=result, message="获取成功")


@router.get("/{role_id}", response_model=ApiResponse[RoleResponse], summary="获取角色详情")
@require_roles()  # 只有 admin 能访问
def get_role_detail(role_id: str, request: Request, db: Session = Depends(get_db)):
    """根据ID获取角色详情"""
    result = role_service.get_role_by_id(db, role_id)
    if not result:
        raise HTTPException(status_code=404, detail="角色不存在")
    return format_response(data=result, message="获取成功")
