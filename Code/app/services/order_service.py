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
    logger.debug(f"步骤1: 获取购物车")
    cart = shopping_cart_dao.get_cart_by_user_id(db, user_id)
    if not cart:
        raise HTTPException(status_code=404, detail="购物车不存在")
    
    logger.debug(f"步骤2: 获取选中商品")
    selected_items = shopping_cart_item_dao.get_checked_cart_items(db, cart.cart_id)
    if not selected_items:
        raise HTTPException(status_code=400, detail="请先选择商品")
    logger.debug(f"选中商品数量: {len(selected_items)}")
    
    # 2. 验证库存并计算总价，收集商品详情
    total_amount = 0
    order_items_data = []
    
    logger.debug(f"步骤3: 验证库存并计算金额")
    for item in selected_items:
        goods = goods_dao.get_goods_by_id(db, item["goods_id"])
        if not goods:
            raise HTTPException(status_code=404, detail="商品不存在")
        
        spec_info = "默认规格"
        if item.get("spec_id"):
            spec = goods_dao.get_spec_by_id(db, item["spec_id"])
            if spec:
                spec_info = f"{spec.spec_name}: {spec.spec_value}"
        
        stock = goods_dao.get_stock_by_spec_id(db, item["spec_id"])
        if not stock or stock.stock_num < item["buy_num"]:
            raise HTTPException(status_code=400, detail=f"{goods.goods_name}库存不足")
        
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
    logger.debug(f"计算完成，总金额: {total_amount}")
    
    # 3. 创建订单主表
    logger.debug(f"步骤4: 创建订单主表")
    order_result = order_dao.create_order(db, user_id, total_amount, address_info)
    order_id = order_result["order_id"]
    logger.debug(f"订单创建成功，订单ID: {order_id}")
    
    # 4. 创建订单明细
    logger.debug(f"步骤5: 创建订单明细")
    for item_data in order_items_data:
        order_dao.create_order_item(db, order_id, item_data)
    logger.debug(f"订单明细创建完成")
    
    # 5. 创建支付记录
    logger.debug(f"步骤6: 创建支付记录")
    pay_data = {
        "order_id": order_result["id"],  # 使用UUID供外键使用
        "user_id": user_id,
        "pay_amount": total_amount
    }
    pay_success = pay_dao.pay_insert_dao(pay_data, db)
    if not pay_success:
        db.rollback()
        raise HTTPException(status_code=500, detail="创建支付记录失败")
    logger.debug(f"支付记录创建成功")
    
    # 6. 扣减库存
    logger.debug(f"步骤7: 扣减库存")
    for item in selected_items:
        stock = goods_dao.get_stock_by_spec_id(db, item["spec_id"])
        if stock:
            new_stock_num = stock.stock_num - item["buy_num"]
            goods_dao.update_stock(db, stock, new_stock_num)
            logger.debug(f"库存扣减: 商品ID {item['goods_id']}, 扣减数量 {item['buy_num']}, 剩余 {new_stock_num}")
    
    # 7. 删除购物车中选中的商品
    logger.debug(f"步骤8: 删除购物车选中商品")
    for item in selected_items:
        success = shopping_cart_item_dao.delete_cart_item(db, item["item_id"], cart.cart_id)
        logger.debug(f"删除购物车商品: item_id={item['item_id']}, success={success}")
    
    logger.debug(f"步骤9: 提交事务")
    try:
        db.commit()
        logger.debug(f"事务提交成功")
    except Exception as e:
        logger.error(f"事务提交失败: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"事务提交失败: {str(e)}")
    
    logger.debug(f"返回订单信息")
    return {
        "order_id": order_id,
        "total_amount": total_amount,
        "pay_amount": total_amount,
        "item_count": len(order_items_data),
        "expire_time": order_result["expire_time"],
        "message": "订单创建成功"
    }