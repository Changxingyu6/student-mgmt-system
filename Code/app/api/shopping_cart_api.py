"""
购物车 API 路由
提供购物车相关的 RESTful API 接口
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict
from database import get_db
from services import shopping_cart_service as cart_service
from utils import format_response


router = APIRouter(prefix="/shopping-cart", tags=["购物车"])


@router.get("/", response_model=Dict, summary="获取用户购物车信息")
def get_cart(user_id: str, db: Session = Depends(get_db)):
    """获取用户购物车"""
    result = cart_service.get_cart_by_user(db, user_id)
    return format_response(data=result, message="获取购物车成功")


@router.post("/add", response_model=Dict,summary="添加商品到购物车")
def add_to_cart(
    user_id: str,
    goods_id: str,
    spec_id: str = None,
    buy_num: int = 1,
    db: Session = Depends(get_db)
):
    """添加商品到购物车"""
    result = cart_service.add_to_cart(db, user_id, goods_id, spec_id, buy_num)
    return format_response(data=result, message="添加商品到购物车成功")


@router.put("/item/{item_id}", response_model=Dict,summary="更新购物车商品")
def update_cart_item(
    item_id: str,
    user_id: str,
    buy_num: int = None,
    is_checked: bool = None,
    db: Session = Depends(get_db)
):
    """更新购物车商品"""
    result = cart_service.update_cart_item(db, user_id, item_id, buy_num, is_checked)
    return format_response(data=result, message="更新购物车商品成功")


@router.delete("/item/{item_id}", response_model=Dict,summary="删除购物车商品")
def delete_cart_item(item_id: str, user_id: str, db: Session = Depends(get_db)):
    """删除购物车商品"""
    result = cart_service.delete_cart_item(db, user_id, item_id)
    return format_response(data=result, message="删除购物车商品成功")


@router.get("/items", response_model=Dict,summary="获取购物车所有物品")
def get_cart_items(user_id: str, db: Session = Depends(get_db)):
    """获取购物车所有物品"""
    result = cart_service.get_cart_items(db, user_id)
    return format_response(data=result, message="获取购物车物品成功")


@router.get("/total", response_model=Dict,summary="计算购物车选中商品的总金额")
def calculate_selected_total(user_id: str, db: Session = Depends(get_db)):
    """计算购物车选中商品的总金额"""
    result = cart_service.calculate_selected_total(db, user_id)
    return format_response(data=result, message="计算购物车总金额成功")