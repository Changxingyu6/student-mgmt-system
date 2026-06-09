"""
订单业务逻辑层
"""
from sqlalchemy.orm import Session
from typing import Dict
from fastapi import HTTPException
from dao import order_dao, goods_dao, pay_dao, shopping_cart_item_dao, shopping_cart_dao
from utils.logger import get_logger


logger = get_logger("order")


def create_order_from_cart(db: Session, user_id: str, address_info: Dict = None) -> Dict:
    """从购物车创建订单（包含完整事务）"""
    logger.debug(f"从购物车创建订单 - 用户ID: {user_id}")
    
    # 默认地址
    if not address_info:
        address_info = {
            "name": "默认收货人",
            "phone": "13800138000",
            "address": "默认收货地址"
        }
    
    # 1. 获取用户购物车及选中商品
    cart = shopping_cart_dao.get_cart_by_user_id(db, user_id)
    if not cart:
        raise HTTPException(status_code=404, detail="购物车不存在")
    
    selected_items = shopping_cart_item_dao.get_checked_cart_items(db, cart.cart_id)
    if not selected_items:
        raise HTTPException(status_code=400, detail="请先选择商品")
    
    # 2. 验证库存并计算总价，收集商品详情
    total_amount = 0
    order_items_data = []
    
    for item in selected_items:
        # 获取商品信息
        goods = goods_dao.get_goods_by_id(db, item["goods_id"])
        if not goods:
            raise HTTPException(status_code=404, detail="商品不存在")
        
        # 获取规格信息
        spec_info = "默认规格"
        if item.get("spec_id"):
            spec = goods_dao.get_spec_by_id(db, item["spec_id"])
            if spec:
                spec_info = f"{spec.spec_name}: {spec.spec_value}"
        
        # 获取库存并验证
        stock = goods_dao.get_stock_by_spec_id(db, item["spec_id"])
        if not stock or stock.stock_num < item["buy_num"]:
            raise HTTPException(status_code=400, detail=f"{goods.goods_name}库存不足")
        
        # 计算金额
        price = float(goods.price)
        total_amount += price * item["buy_num"]
        
        order_items_data.append({
            "goods_id": item["goods_id"],
            "spec_id": item["spec_id"],
            "buy_num": item["buy_num"],
            "price": price,
            "goods_name": goods.goods_name,
            "spec_info": spec_info
        })
    
    # 3. 创建订单主表
    order_result = order_dao.create_order(db, user_id, total_amount, address_info)
    order_id = order_result["order_id"]
    
    # 4. 创建订单明细
    for item_data in order_items_data:
        order_dao.create_order_item(db, order_id, item_data)
    
    # 5. 创建支付记录
    pay_data = {
        "order_id": order_id,
        "user_id": user_id,
        "pay_amount": total_amount
    }
    pay_success = pay_dao.pay_insert_dao(pay_data, db)
    if not pay_success:
        db.rollback()
        raise HTTPException(status_code=500, detail="创建支付记录失败")
    
    # 6. 扣减库存
    for item in selected_items:
        stock = goods_dao.get_stock_by_spec_id(db, item["spec_id"])
        if stock:
            new_stock_num = stock.stock_num - item["buy_num"]
            goods_dao.update_stock(db, stock, new_stock_num)
    
    # 7. 删除购物车中选中的商品
    for item in selected_items:
        shopping_cart_item_dao.delete_cart_item(db, item["item_id"], cart.cart_id)
    
    db.commit()
    
    return {
        "order_id": order_id,
        "total_amount": total_amount,
        "pay_amount": total_amount,
        "item_count": len(order_items_data),
        "expire_time": order_result["expire_time"],
        "message": "订单创建成功"
    }