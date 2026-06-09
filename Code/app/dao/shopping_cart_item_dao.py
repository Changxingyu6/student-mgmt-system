"""
购物车项数据访问层
使用 SQLAlchemy ORM 进行购物车项相关数据库操作
"""
from sqlalchemy.orm import Session
from typing import Optional, List, Dict
from datetime import datetime
from utils.uuid_utils import generate_uuid
from model.shopping_cart_item import ShoppingCartItem


def _item_to_dict(item: ShoppingCartItem) -> Dict:
    """将购物车项对象转换为字典"""
    return {
        "item_id": item.item_id,
        "cart_id": item.cart_id,
        "goods_id": item.goods_id,
        "spec_id": item.spec_id,
        "buy_num": item.buy_num,
        "is_checked": bool(item.is_checked),
        "create_time": item.create_time.strftime("%Y-%m-%d %H:%M:%S") if item.create_time else None,
        "update_time": item.update_time.strftime("%Y-%m-%d %H:%M:%S") if item.update_time else None
    }


def add_cart_item(db: Session, cart_id: str, goods_id: str, spec_id: str = None, buy_num: int = 1) -> Dict:
    """新增购物车项
    如果商品已存在，则更新数量；否则创建新记录
    """
    existing_item = db.query(ShoppingCartItem).filter(
        ShoppingCartItem.cart_id == cart_id,
        ShoppingCartItem.goods_id == goods_id,
        ShoppingCartItem.spec_id == spec_id,
        ShoppingCartItem.is_deleted == False
    ).first()
    
    if existing_item:
        existing_item.buy_num += buy_num
        existing_item.update_time = datetime.now()
        return _item_to_dict(existing_item)
    else:
        new_item = ShoppingCartItem(
            item_id=generate_uuid(),
            cart_id=cart_id,
            goods_id=goods_id,
            spec_id=spec_id,
            buy_num=buy_num,
            is_checked=True,
            is_deleted=False
        )
        db.add(new_item)
        return _item_to_dict(new_item)


def get_cart_items_by_cart_id(db: Session, cart_id: str) -> List[Dict]:
    """获取购物车所有商品项"""
    items = db.query(ShoppingCartItem).filter(
        ShoppingCartItem.cart_id == cart_id,
        ShoppingCartItem.is_deleted == False
    ).order_by(ShoppingCartItem.create_time.desc()).all()
    return [_item_to_dict(item) for item in items]


def update_cart_item(db: Session, item_id: str, cart_id: str, buy_num: int = None, is_checked: bool = None) -> Optional[Dict]:
    """更新购物车项（数量或选中状态）"""
    item = db.query(ShoppingCartItem).filter(
        ShoppingCartItem.item_id == item_id,
        ShoppingCartItem.cart_id == cart_id,
        ShoppingCartItem.is_deleted == False
    ).first()
    
    if not item:
        return None
    
    if buy_num is not None:
        item.buy_num = buy_num
    if is_checked is not None:
        item.is_checked = is_checked
    item.update_time = datetime.now()
    
    return _item_to_dict(item)


def delete_cart_item(db: Session, item_id: str, cart_id: str) -> bool:
    """删除购物车项（逻辑删除）"""
    item = db.query(ShoppingCartItem).filter(
        ShoppingCartItem.item_id == item_id,
        ShoppingCartItem.cart_id == cart_id,
        ShoppingCartItem.is_deleted == False
    ).first()
    
    if not item:
        return False
    
    item.is_deleted = True
    item.update_time = datetime.now()
    return True


def clear_cart_items(db: Session, cart_id: str) -> bool:
    """清空购物车所有商品（逻辑删除）"""
    db.query(ShoppingCartItem).filter(
        ShoppingCartItem.cart_id == cart_id,
        ShoppingCartItem.is_deleted == False
    ).update({
        ShoppingCartItem.is_deleted: True,
        ShoppingCartItem.update_time: datetime.now()
    })
    return True


def get_cart_item_by_id(db: Session, item_id: str, cart_id: str) -> Optional[Dict]:
    """根据ID获取购物车项"""
    item = db.query(ShoppingCartItem).filter(
        ShoppingCartItem.item_id == item_id,
        ShoppingCartItem.cart_id == cart_id,
        ShoppingCartItem.is_deleted == False
    ).first()
    return _item_to_dict(item) if item else None


def get_checked_cart_items(db: Session, cart_id: str) -> List[Dict]:
    """获取已选中的购物车项"""
    items = db.query(ShoppingCartItem).filter(
        ShoppingCartItem.cart_id == cart_id,
        ShoppingCartItem.is_checked == True,
        ShoppingCartItem.is_deleted == False
    ).all()
    return [_item_to_dict(item) for item in items]


def count_cart_items(db: Session, cart_id: str) -> int:
    """统计购物车商品数量"""
    return db.query(ShoppingCartItem).filter(
        ShoppingCartItem.cart_id == cart_id,
        ShoppingCartItem.is_deleted == False
    ).count()