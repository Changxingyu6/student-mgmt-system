"""
用户收货地址业务逻辑层
负责收货地址的增删改查业务
"""
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from fastapi import HTTPException, status
from dao import address_dao as address_repo
from utils.logger import get_logger
from schema.address import *

logger = get_logger("address")


def _convert_address_to_response(address) -> dict:
    """将地址对象转换为响应字典"""
    return AddressResponse(
        id=address.id,
        receiver_name=address.receiver_name,
        receiver_phone=address.receiver_phone,
        province=address.province,
        city=address.city,
        district=address.district,
        detail_address=address.detail_address,
        is_default=address.is_default,
        create_time=address.create_time
    ).dict()


def get_user_all_addresses(db: Session, user_id: int) -> Dict:
    """获取用户所有地址"""
    logger.info(f"获取用户地址列表 - 用户ID: {user_id}")
    addresses = address_repo.get_user_addresses(db, user_id)
    return {
        "data": [_convert_address_to_response(addr) for addr in addresses],
        "total": len(addresses)
    }


def get_user_default_addr(db: Session, user_id: int) -> Optional[dict]:
    """获取用户默认地址"""
    logger.info(f"获取用户默认地址 - 用户ID: {user_id}")
    address = address_repo.get_user_default_address(db, user_id)
    if not address:
        return None
    return _convert_address_to_response(address)


def create_user_address(db: Session, user_id: int, receiver_name: str, 
                        receiver_phone: str, detail_address: str, 
                        province: str = None, city: str = None, 
                        district: str = None, is_default: bool = False) -> dict:
    """创建收货地址"""
    logger.info(f"创建收货地址 - 用户ID: {user_id}")
    
    address = address_repo.create_address(
        db, user_id, receiver_name, receiver_phone, detail_address,
        province, city, district, is_default
    )
    db.commit()
    db.refresh(address)
    return _convert_address_to_response(address)


def update_user_address(db: Session, user_id: int, address_id: int, **kwargs) -> dict:
    """更新收货地址"""
    logger.info(f"更新收货地址 - 用户ID: {user_id}, 地址ID: {address_id}")
    
    address = address_repo.get_address_by_id(db, address_id)
    if not address:
        raise HTTPException(status_code=404, detail="地址不存在")
    
    if address.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权限操作此地址")
    
    result = address_repo.update_address(db, address_id, **kwargs)
    db.commit()
    db.refresh(result)
    return _convert_address_to_response(result)


def delete_user_address(db: Session, user_id: int, address_id: int) -> dict:
    """删除收货地址"""
    logger.info(f"删除收货地址 - 用户ID: {user_id}, 地址ID: {address_id}")
    
    address = address_repo.get_address_by_id(db, address_id)
    if not address:
        raise HTTPException(status_code=404, detail="地址不存在")
    
    if address.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权限操作此地址")
    
    address_repo.delete_address(db, address_id)
    db.commit()
    return {"message": "删除成功"}


def set_user_default_address(db: Session, user_id: int, address_id: int) -> dict:
    """设置默认地址"""
    logger.info(f"设置默认地址 - 用户ID: {user_id}, 地址ID: {address_id}")
    
    address = address_repo.get_address_by_id(db, address_id)
    if not address:
        raise HTTPException(status_code=404, detail="地址不存在")
    
    if address.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权限操作此地址")
    
    result = address_repo.set_default_address(db, address_id)
    db.commit()
    db.refresh(result)
    return _convert_address_to_response(result)
