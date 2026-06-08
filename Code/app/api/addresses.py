"""
用户收货地址API路由
"""
from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session

from database import get_db
from utils import format_response
from services import address as address_service
from schema.address import *

router = APIRouter(prefix="/addresses", tags=["收货地址"])


@router.get("", response_model=AddressListResponse, summary="获取用户地址列表")
def get_address_list(
    request: Request,
    db: Session = Depends(get_db)
):
    """获取当前登录用户的所有收货地址"""
    current_user = request.state.user
    result = address_service.get_user_all_addresses(db, current_user["id"])
    return format_response(data=result, message="获取成功")


@router.get("/default", response_model=AddressResponse, summary="获取默认地址")
def get_default_address(
    request: Request,
    db: Session = Depends(get_db)
):
    """获取当前用户的默认收货地址"""
    current_user = request.state.user
    result = address_service.get_user_default_addr(db, current_user["id"])
    return format_response(data=result, message="获取成功")


@router.post("", response_model=AddressResponse, summary="创建收货地址")
def create_address(
    request: Request,
    address_request: AddressCreateRequest,
    db: Session = Depends(get_db)
):
    """创建新的收货地址"""
    current_user = request.state.user
    result = address_service.create_user_address(
        db, current_user["id"],
        address_request.receiver_name,
        address_request.receiver_phone,
        address_request.detail_address,
        address_request.province,
        address_request.city,
        address_request.district,
        address_request.is_default
    )
    return format_response(data=result, message="创建成功", status_code=status.HTTP_201_CREATED)


@router.put("/{address_id}", response_model=AddressResponse, summary="更新收货地址")
def update_address(
    request: Request,
    address_id: int,
    address_request: AddressUpdateRequest,
    db: Session = Depends(get_db)
):
    """更新收货地址信息"""
    current_user = request.state.user
    result = address_service.update_user_address(db, current_user["id"], address_id, **address_request.dict(exclude_unset=True))
    return format_response(data=result, message="更新成功")


@router.delete("/{address_id}", summary="删除收货地址")
def remove_address(
    request: Request,
    address_id: int,
    db: Session = Depends(get_db)
):
    """删除收货地址"""
    current_user = request.state.user
    result = address_service.delete_user_address(db, current_user["id"], address_id)
    return format_response(data=result, message="删除成功")


@router.post("/{address_id}/default", response_model=AddressResponse, summary="设置默认地址")
def make_default_address(
    request: Request,
    address_id: int,
    db: Session = Depends(get_db)
):
    """将指定地址设为默认地址"""
    current_user = request.state.user
    result = address_service.set_user_default_address(db, current_user["id"], address_id)
    return format_response(data=result, message="设置成功")