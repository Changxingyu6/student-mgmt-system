"""
用户收货地址数据访问层
使用 SQLAlchemy ORM 进行地址相关数据库操作
"""
from sqlalchemy.orm import Session
from typing import Optional, List
from model.address import UserAddress
from utils.uuid_utils import generate_uuid


def get_address_by_id(db: Session, address_id: str) -> Optional[UserAddress]:
    """根据ID获取地址"""
    return db.query(UserAddress).filter(UserAddress.id == address_id).first()


def get_user_addresses(db: Session, user_id: str) -> List[UserAddress]:
    """获取用户所有地址"""
    return db.query(UserAddress).filter(UserAddress.user_id == user_id).order_by(
        UserAddress.is_default.desc(), UserAddress.created_at.desc()
    ).all()


def get_user_default_address(db: Session, user_id: str) -> Optional[UserAddress]:
    """获取用户默认地址"""
    return db.query(UserAddress).filter(
        UserAddress.user_id == user_id, 
        UserAddress.is_default == True
    ).first()


def create_address(db: Session, user_id: str, receiver_name: str, receiver_phone: str,
                  detail_address: str, province: str = None, city: str = None, 
                  district: str = None, is_default: bool = False) -> UserAddress:
    """创建地址"""
    if is_default:
        db.query(UserAddress).filter(
            UserAddress.user_id == user_id,
            UserAddress.is_default == True
        ).update({"is_default": False})
    
    db_address = UserAddress(
        id=generate_uuid(),
        user_id=user_id,
        receiver_name=receiver_name,
        receiver_phone=receiver_phone,
        province=province,
        city=city,
        district=district,
        detail_address=detail_address,
        is_default=is_default
    )
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address


def update_address(db: Session, address_id: str, **kwargs) -> Optional[UserAddress]:
    """更新地址"""
    db_address = get_address_by_id(db, address_id)
    if not db_address:
        return None
    
    if kwargs.get('is_default'):
        db.query(UserAddress).filter(
            UserAddress.user_id == db_address.user_id,
            UserAddress.is_default == True,
            UserAddress.id != address_id
        ).update({"is_default": False})
    
    for key, value in kwargs.items():
        if value is not None:
            setattr(db_address, key, value)
    
    db.commit()
    db.refresh(db_address)
    return db_address


def delete_address(db: Session, address_id: str) -> bool:
    """删除地址"""
    db_address = get_address_by_id(db, address_id)
    if not db_address:
        return False
    
    db.delete(db_address)
    db.commit()
    return True


def set_default_address(db: Session, address_id: str) -> Optional[UserAddress]:
    """设置默认地址"""
    db_address = get_address_by_id(db, address_id)
    if not db_address:
        return None
    
    db.query(UserAddress).filter(
        UserAddress.user_id == db_address.user_id,
        UserAddress.is_default == True
    ).update({"is_default": False})
    
    db_address.is_default = True
    db.commit()
    db.refresh(db_address)
    return db_address