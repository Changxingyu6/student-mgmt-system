"""
购物车业务逻辑层
负责购物车的业务处理和事务管理
"""
from sqlalchemy.orm import Session
from typing import Dict
from fastapi import HTTPException
from dao import shopping_cart_dao as cart_dao
from dao import shopping_cart_item_dao as item_dao
from dao import user_dao
from model.goods_model import Goods, GoodsSpec
from utils.logger import get_logger


logger = get_logger("shopping_cart")


def _get_item_details(db: Session, item: Dict) -> Dict:
    """获取购物车项的完整信息（包含商品名称、规格名称、价格）"""
    goods = db.query(Goods).filter(Goods.id == item["goods_id"]).first()
    
    spec_name = "默认规格"
    if item.get("spec_id"):
        spec = db.query(GoodsSpec).filter(GoodsSpec.id == item["spec_id"]).first()
        if spec:
            spec_name = f"{spec.spec_name}: {spec.spec_value}"
    
    price = 0.0
    if goods and goods.price:
        price = float(goods.price)
    
    return {
        **item,
        "goods_name": goods.goods_name if goods else "未知商品",
        "spec_name": spec_name,
        "price": price
    }


def get_cart_by_user(db: Session, user_id: str) -> Dict:
    """获取用户购物车"""
    logger.debug(f"获取用户购物车 - 用户ID: {user_id}")

    # 从数据库查询用户是否存在
    user = user_dao.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    cart = cart_dao.get_cart_by_user_id(db, user_id)
    if not cart:
        cart = cart_dao.create_cart(db, user_id)
        db.commit()
        db.refresh(cart)

    items = item_dao.get_cart_items_by_cart_id(db, cart.cart_id)
    items_with_details = [_get_item_details(db, item) for item in items]

    return {
        "cart_id": cart.cart_id,
        "user_id": cart.user_id,
        "is_active": cart.is_active,
        "item_count": len(items_with_details),
        "items": items_with_details,
        "create_time": cart.create_time.strftime("%Y-%m-%d %H:%M:%S") if cart.create_time else None,
        "update_time": cart.update_time.strftime("%Y-%m-%d %H:%M:%S") if cart.update_time else None
    }


def add_to_cart(db: Session, user_id: str, goods_id: str, spec_id: str = None, buy_num: int = 1) -> Dict:
    """添加商品到购物车"""
    logger.debug(f"添加商品到购物车 - 用户ID: {user_id}, 商品ID: {goods_id}")

    if buy_num <= 0:
        raise HTTPException(status_code=400, detail="购买数量必须大于0")

    cart = cart_dao.get_cart_by_user_id(db, user_id)
    if not cart:
        cart = cart_dao.create_cart(db, user_id)

    item = item_dao.add_cart_item(db, cart.cart_id, goods_id, spec_id, buy_num)
    db.commit()

    return {
        "item_id": item["item_id"],
        "cart_id": cart.cart_id,
        "user_id": user_id,
        "goods_id": item["goods_id"],
        "spec_id": item["spec_id"],
        "buy_num": item["buy_num"],
        "is_checked": item["is_checked"],
        "create_time": item["create_time"]
    }


def update_cart_item(db: Session, user_id: str, item_id: str, buy_num: int = None, is_checked: bool = None) -> Dict:
    """更新购物车商品"""
    logger.debug(f"更新购物车商品 - 用户ID: {user_id}, 商品项ID: {item_id}")

    if buy_num is not None and buy_num <= 0:
        raise HTTPException(status_code=400, detail="购买数量必须大于0")

    cart = cart_dao.get_cart_by_user_id(db, user_id)
    if not cart:
        raise HTTPException(status_code=404, detail="购物车不存在")

    item = item_dao.update_cart_item(db, item_id, cart.cart_id, buy_num, is_checked)

    if not item:
        raise HTTPException(status_code=404, detail="购物车商品不存在")

    db.commit()

    return {
        "item_id": item["item_id"],
        "goods_id": item["goods_id"],
        "spec_id": item["spec_id"],
        "buy_num": item["buy_num"],
        "is_checked": item["is_checked"],
        "update_time": item["update_time"]
    }


def delete_cart_item(db: Session, user_id: str, item_id: str) -> Dict:
    """删除购物车商品"""
    logger.debug(f"删除购物车商品 - 用户ID: {user_id}, 商品项ID: {item_id}")

    cart = cart_dao.get_cart_by_user_id(db, user_id)
    if not cart:
        raise HTTPException(status_code=404, detail="购物车不存在")

    success = item_dao.delete_cart_item(db, item_id, cart.cart_id)

    if not success:
        raise HTTPException(status_code=404, detail="购物车商品不存在")

    db.commit()
    return {"message": "删除成功"}


def get_cart_items(db: Session, user_id: str) -> Dict:
    """获取购物车所有物品"""
    logger.debug(f"获取购物车所有物品 - 用户ID: {user_id}")

    cart = cart_dao.get_cart_by_user_id(db, user_id)
    if not cart:
        raise HTTPException(status_code=404, detail="购物车不存在")

    items = item_dao.get_cart_items_by_cart_id(db, cart.cart_id)

    return {
        "user_id": user_id,
        "cart_id": cart.cart_id,
        "item_count": len(items),
        "items": items
    }


def calculate_selected_total(db: Session, user_id: str) -> Dict:
    """计算购物车选中商品的总金额"""
    logger.debug(f"计算选中商品总金额 - 用户ID: {user_id}")

    cart = cart_dao.get_cart_by_user_id(db, user_id)
    if not cart:
        return {"total_amount": 0, "selected_count": 0, "cart_id": None}

    selected_items = item_dao.get_checked_cart_items(db, cart.cart_id)

    total_amount = 0.0
    for item in selected_items:
        # 复用 _get_item_details 获取商品价格
        details = _get_item_details(db, item)
        buy_num = int(item.get("buy_num") or 0)
        price = float(details.get("price") or 0)
        total_amount += buy_num * price

    return {
        "total_amount": round(total_amount, 2),
        "selected_count": len(selected_items),
        "cart_id": cart.cart_id
    }
