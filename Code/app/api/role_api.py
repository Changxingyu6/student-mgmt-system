"""
角色管理 API
提供角色的增删改查接口
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


@router.post("", response_model=ApiResponse[RoleResponse], summary="创建角色")
@require_roles()  # 只有 admin 能访问
def create_role(request: Request, role_request: RoleCreateRequest, db: Session = Depends(get_db)):
    """创建新角色"""
    try:
        result = role_service.create_role(db, role_request)
        return format_response(data=result, message="创建成功")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{role_id}", response_model=ApiResponse[RoleResponse], summary="更新角色")
@require_roles()  # 只有 admin 能访问
def update_role(role_id: str, request: Request, role_request: RoleUpdateRequest, db: Session = Depends(get_db)):
    """更新角色信息"""
    try:
        result = role_service.update_role(db, role_id, role_request)
        if not result:
            raise HTTPException(status_code=404, detail="角色不存在")
        return format_response(data=result, message="更新成功")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{role_id}", response_model=ApiResponse[dict], summary="删除角色")
@require_roles()  # 只有 admin 能访问
def delete_role(role_id: str, request: Request, db: Session = Depends(get_db)):
    """删除角色（逻辑删除）"""
    try:
        success = role_service.delete_role(db, role_id)
        if not success:
            raise HTTPException(status_code=404, detail="角色不存在")
        return format_response(message="删除成功")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
