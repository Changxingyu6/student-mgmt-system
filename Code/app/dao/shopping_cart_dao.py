"""
购物车主表数据访问层
使用 SQLAlchemy ORM 进行购物车相关数据库操作
"""
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from utils.uuid_utils import generate_uuid
from model.shopping_cart import ShoppingCart



def get_cart_by_user_id(db: Session, user_id: str) -> Optional[ShoppingCart]:
    """根据用户ID获取购物车"""
    return db.query(ShoppingCart).filter(
        ShoppingCart.user_id == user_id,
        ShoppingCart.is_active == True
    ).first()


def create_cart(db: Session, user_id: str) -> ShoppingCart:
    """创建购物车（确保一个用户只有一个购物车）"""
    existing_cart = get_cart_by_user_id(db, user_id)
    if existing_cart:
        return existing_cart

    new_cart = ShoppingCart(
        cart_id=generate_uuid(),
        user_id=user_id,
        is_active=True,
        create_time=datetime.now(),
        update_time=datetime.now()
    )
    db.add(new_cart)
    db.commit()
    db.refresh(new_cart)
    return new_cart


def get_cart_by_id(db: Session, cart_id: str) -> Optional[ShoppingCart]:
    """根据购物车ID获取购物车"""
    return db.query(ShoppingCart).filter(
        ShoppingCart.cart_id == cart_id,
        ShoppingCart.is_active == True
    ).first()


def deactivate_cart(db: Session, cart_id: str) -> bool:
    """停用购物车（逻辑删除）"""
    cart = get_cart_by_id(db, cart_id)
    if not cart:
        return False

    cart.is_active = False
    cart.update_time = datetime.now()
    db.commit()
    return True