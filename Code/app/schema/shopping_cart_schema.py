"""
购物车 Schema 层
提供购物车 API 的数据校验和依赖注入函数
"""
from pydantic import BaseModel, Field
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from database import get_db
from dao import user_dao
from dao import shopping_cart_dao
from dao import shopping_cart_item_dao
from dao import goods_dao


class GetCartRequest(BaseModel):
    """获取购物车请求参数校验模型"""
    user_id: str = Field(..., min_length=1, max_length=50, description="用户ID")


class AddCartItemRequest(BaseModel):
    """添加购物车项请求参数校验模型"""
    user_id: str = Field(..., min_length=1, max_length=50, description="用户ID")
    goods_id: str = Field(..., min_length=1, max_length=50, description="商品ID")
    spec_id: str = Field(None, max_length=50, description="商品规格ID")
    buy_num: int = Field(1, ge=1, description="购买数量")


class UpdateCartItemRequest(BaseModel):
    """更新购物车项请求参数校验模型（通过商品信息增加数量）"""
    user_id: str = Field(..., min_length=1, max_length=50, description="用户ID")
    cart_id: str = Field(..., min_length=1, max_length=50, description="购物车ID")
    goods_id: str = Field(..., min_length=1, max_length=50, description="商品ID")
    spec_id: str = Field(None, max_length=50, description="商品规格ID")
    add_num: int = Field(..., ge=1, description="增加的数量")


class DeleteCartItemRequest(BaseModel):
    """删除购物车项请求参数校验模型"""
    user_id: str = Field(..., min_length=1, max_length=50, description="用户ID")
    cart_id: str = Field(..., min_length=1, max_length=50, description="购物车ID")
    goods_id: str = Field(..., min_length=1, max_length=50, description="商品ID")
    spec_id: str = Field(None, max_length=50, description="商品规格ID")
    delete_all: bool = Field(False, description="是否全部删除")
    delete_num: int = Field(None, ge=1, description="删除数量")


class CartItemSelect(BaseModel):
    """购物车选中商品项"""
    goods_id: str = Field(..., min_length=1, max_length=50, description="商品ID")
    spec_id: Optional[str] = Field(None, max_length=50, description="商品规格ID")


class CalculateTotalRequest(BaseModel):
    """计算购物车选中商品总金额请求模型"""
    user_id: str = Field(..., min_length=1, max_length=50, description="用户ID")
    items: List[CartItemSelect] = Field([], description="选中的商品列表（可选）")
    select_all: bool = Field(False, description="是否选中全部商品")


def validate_add_cart_item(request: AddCartItemRequest, db: Session = Depends(get_db)) -> AddCartItemRequest:
    """
    校验添加购物车项请求（完整校验）

    :param request: 添加购物车请求体
    :param db: 数据库会话
    :return: 请求体（校验通过）
    :raises HTTPException: 校验失败时抛出相应错误
    """
    # 校验用户是否存在
    user = user_dao.get_user_by_id(db, request.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 检查商品是否存在
    goods = goods_dao.get_goods_by_id(db, request.goods_id)
    if not goods:
        raise HTTPException(status_code=404, detail="商品不存在")

    # 检查商品是否上架
    if goods.sale_status != 1:
        raise HTTPException(status_code=400, detail="商品已下架")

    # 检查库存
    stock = goods_dao.get_stock_by_goods_id(db, request.goods_id)
    if not stock:
        raise HTTPException(status_code=400, detail="商品库存记录不存在")

    # 检查库存数量
    if stock.stock_num < request.buy_num:
        raise HTTPException(
            status_code=400,
            detail=f"库存不足，当前库存: {stock.stock_num}，购买数量: {request.buy_num}"
        )

    return request


def validate_user_exists(user_id: str, db: Session = Depends(get_db)) -> str:
    """
    校验用户是否存在

    :param user_id: 用户ID
    :param db: 数据库会话
    :return: 用户ID（校验通过）
    :raises HTTPException: 用户不存在时抛出404错误
    """
    user = user_dao.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user_id


def validate_cart_exists_or_create(user_id: str, db: Session = Depends(get_db)) -> str:
    """
    校验购物车是否存在，不存在则自动创建

    :param user_id: 用户ID
    :param db: 数据库会话
    :return: 购物车ID
    """
    cart = shopping_cart_dao.get_cart_by_user_id(db, user_id)
    if not cart:
        # 自动创建购物车
        cart = shopping_cart_dao.create_cart(db, user_id)
    return cart.cart_id


def validate_cart_belongs_to_user(user_id: str, db: Session = Depends(get_db)) -> str:
    """
    校验购物车是否属于该用户

    :param user_id: 用户ID
    :param db: 数据库会话
    :return: 购物车ID
    :raises HTTPException: 用户没有购物车时抛出404错误
    """
    cart = shopping_cart_dao.get_cart_by_user_id(db, user_id)
    if not cart:
        raise HTTPException(status_code=404, detail="用户购物车不存在")
    return cart.cart_id


def validate_goods_stock(goods_id: str, buy_num: int):
    """
    校验商品库存是否充足（闭包工厂函数）

    :param goods_id: 商品ID
    :param buy_num: 购买数量
    :return: 依赖注入函数
    :raises HTTPException: 商品不存在抛出404，库存不足抛出400
    """

    def _validate(db: Session = Depends(get_db)) -> str:
        # 检查商品是否存在
        goods = goods_dao.get_goods_by_id(db, goods_id)
        if not goods:
            raise HTTPException(status_code=404, detail="商品不存在")

        # 检查商品是否上架
        if goods.sale_status != 1:
            raise HTTPException(status_code=400, detail="商品已下架")

        # 检查库存
        stock = goods_dao.get_stock_by_goods_id(db, goods_id)
        if not stock:
            raise HTTPException(status_code=400, detail="商品库存记录不存在")

        # 检查库存数量
        if stock.stock_num < buy_num:
            raise HTTPException(
                status_code=400,
                detail=f"库存不足，当前库存: {stock.stock_num}，购买数量: {buy_num}"
            )

        return goods_id

    return _validate


def validate_update_cart_item(request: UpdateCartItemRequest, db: Session = Depends(get_db)) -> UpdateCartItemRequest:
    """
    校验更新购物车项请求（通过商品信息增加数量）

    :param request: 更新购物车请求体
    :param db: 数据库会话
    :return: 请求体（校验通过）
    :raises HTTPException: 校验失败时抛出相应错误
    """
    # 1. 校验用户是否存在
    user = user_dao.get_user_by_id(db, request.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 2. 校验购物车是否存在且属于用户
    cart = shopping_cart_dao.get_cart_by_cart_id(db, request.cart_id)
    if not cart:
        raise HTTPException(status_code=404, detail="购物车不存在")

    # 3. 校验购物车是否属于当前用户
    if cart.user_id != request.user_id:
        raise HTTPException(status_code=403, detail="无权操作该购物车")

    # 4. 校验商品是否存在
    goods = goods_dao.get_goods_by_id(db, request.goods_id)
    if not goods:
        raise HTTPException(status_code=404, detail="商品不存在")

    # 5. 校验商品是否下架
    if goods.sale_status != 1:
        raise HTTPException(status_code=400, detail="商品已下架")

    # 6. 校验库存（增加后的总数量不超过库存）
    stock = goods_dao.get_stock_by_goods_id(db, request.goods_id)
    if not stock:
        raise HTTPException(status_code=400, detail="商品库存记录不存在")

    # 检查购物车中已有数量
    existing_item = shopping_cart_item_dao.get_cart_item_by_goods(db, request.cart_id, request.goods_id,
                                                                  request.spec_id)
    existing_num = existing_item["buy_num"] if existing_item else 0

    # 计算增加后的总数量
    total_num = existing_num + request.add_num
    if stock.stock_num < total_num:
        raise HTTPException(
            status_code=400,
            detail=f"库存不足，当前库存: {stock.stock_num}，当前购物车数量: {existing_num}，增加数量: {request.add_num}，总计: {total_num}"
        )

    return request


def validate_delete_cart_item(request: DeleteCartItemRequest, db: Session = Depends(get_db)) -> DeleteCartItemRequest:
    """
    校验删除购物车项请求（通过商品信息删除）

    :param request: 删除购物车请求体
    :param db: 数据库会话
    :return: 请求体（校验通过）
    :raises HTTPException: 校验失败时抛出相应错误
    """
    # 1. 校验用户是否存在
    user = user_dao.get_user_by_id(db, request.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 2. 校验购物车是否存在
    cart = shopping_cart_dao.get_cart_by_cart_id(db, request.cart_id)
    if not cart:
        raise HTTPException(status_code=404, detail="购物车不存在")

    # 3. 校验购物车是否属于当前用户
    if cart.user_id != request.user_id:
        raise HTTPException(status_code=403, detail="无权操作该购物车")

    # 4. 校验删除参数（delete_all 和 delete_num 必须有一个）
    if not request.delete_all and request.delete_num is None:
        raise HTTPException(status_code=400, detail="必须指定 delete_all 或 delete_num")

    # 5. 校验购物车项是否存在
    item = shopping_cart_item_dao.get_cart_item_by_goods(db, request.cart_id, request.goods_id, request.spec_id)
    if not item:
        raise HTTPException(status_code=404, detail="购物车中不存在该商品")

    # 6. 如果是按数量删除，校验删除数量是否合理
    if request.delete_num is not None:
        if request.delete_num > item["buy_num"]:
            raise HTTPException(
                status_code=400,
                detail=f"删除数量超过购物车中商品数量，当前数量: {item['buy_num']}，删除数量: {request.delete_num}"
            )

    return request


def validate_calculate_total(request: CalculateTotalRequest, db: Session = Depends(get_db)) -> CalculateTotalRequest:
    """
    校验计算购物车选中商品总金额请求

    :param request: 计算总金额请求体
    :param db: 数据库会话
    :return: 请求体（校验通过）
    :raises HTTPException: 校验失败时抛出相应错误
    """
    # 1. 校验用户是否存在
    user = user_dao.get_user_by_id(db, request.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 2. 校验购物车是否存在
    cart = shopping_cart_dao.get_cart_by_user_id(db, request.user_id)
    if not cart:
        raise HTTPException(status_code=404, detail="购物车不存在")

    # 3. 校验请求参数（必须指定 select_all=True 或提供 items 列表）
    if not request.select_all and not request.items:
        raise HTTPException(status_code=400, detail="必须指定 select_all=True 或提供 items 列表")

    # 4. 如果不是全选模式，校验选中的商品是否都存在于购物车中
    if not request.select_all:
        for item in request.items:
            cart_item = shopping_cart_item_dao.get_cart_item_by_goods(db, cart.cart_id, item.goods_id, item.spec_id)
            if not cart_item:
                raise HTTPException(
                    status_code=404,
                    detail=f"购物车中不存在商品: goods_id={item.goods_id}, spec_id={item.spec_id}"
                )

            # 5. 校验商品是否存在且有效
            goods = goods_dao.get_goods_by_id(db, item.goods_id)
            if not goods:
                raise HTTPException(status_code=404, detail=f"商品不存在: {item.goods_id}")

    return request