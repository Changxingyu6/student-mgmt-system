"""
订单业务逻辑层
"""
from sqlalchemy.orm import Session
from typing import Dict
from fastapi import HTTPException
from dao import order_dao, goods_dao, pay_dao, shopping_cart_item_dao, shopping_cart_dao
from dao import logistics_dao, address_dao, user_dao
from utils.logger import get_logger


logger = get_logger("order")


def create_order_from_cart(db: Session, user_id: str, address_info: Dict = None) -> Dict:
    """从购物车创建订单（包含完整事务）"""
    logger.debug(f"从购物车创建订单 - 用户ID: {user_id}")
    
    # 获取用户收货地址：优先默认地址，其次第一个地址；没有地址则拒绝下单
    if not address_info:
        # 1. 尝试获取默认地址
        default_address = address_dao.get_user_default_address(db, user_id)
        if default_address:
            address_info = {
                "name": default_address.receiver_name,
                "phone": default_address.receiver_phone,
                "address": f"{default_address.province or ''}{default_address.city or ''}{default_address.district or ''}{default_address.detail_address or ''}"
            }
            logger.debug(f"使用默认地址: {address_info}")
        else:
            # 2. 尝试获取第一个地址
            addresses = address_dao.get_user_addresses(db, user_id)
            if addresses and len(addresses) > 0:
                first_address = addresses[0]
                address_info = {
                    "name": first_address.receiver_name,
                    "phone": first_address.receiver_phone,
                    "address": f"{first_address.province or ''}{first_address.city or ''}{first_address.district or ''}{first_address.detail_address or ''}"
                }
                logger.debug(f"使用第一个地址: {address_info}")
            else:
                # 3. 用户没有任何地址，拒绝下单
                raise HTTPException(status_code=400, detail="请先添加收货地址后再下单")
    
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
    original_amount = 0  # 原价
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
        original_amount += price * item["buy_num"]
        
        order_items_data.append({
            "goods_id": item["goods_id"],
            "spec_id": item["spec_id"],
            "buy_num": item["buy_num"],
            "price": price,
            "goods_name": goods.goods_name,
            "spec_info": spec_info
        })
    logger.debug(f"计算完成，原价金额: {original_amount}")
    
    # 3. 获取用户会员折扣
    logger.debug(f"步骤3.5: 计算会员折扣")
    user = user_dao.get_user_by_id(db, user_id)
    discount_rate = float(user.discount_rate) if user and user.discount_rate else 1.0
    logger.debug(f"用户折扣率: {discount_rate}")
    
    # 4. 计算折扣后金额
    discount_amount = original_amount * (1 - discount_rate)
    actual_pay_amount = original_amount * discount_rate
    logger.debug(f"折扣金额: {discount_amount}, 实际支付金额: {actual_pay_amount}")
    
    # 5. 创建订单主表（保存原价和实际支付金额）
    logger.debug(f"步骤4: 创建订单主表")
    order_result = order_dao.create_order(db, user_id, original_amount, address_info, actual_pay_amount)
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
        "pay_amount": actual_pay_amount  # 使用实际支付金额（已扣会员折扣）
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
        "total_amount": original_amount,
        "pay_amount": actual_pay_amount,
        "discount_amount": discount_amount,
        "item_count": len(order_items_data),
        "expire_time": order_result["expire_time"],
        "message": "订单创建成功"
    }


def get_user_logistics(user_id: str, db) -> list:
    """获取用户的所有物流记录"""
    # 1. 获取用户的所有订单
    orders = order_dao.get_orders_by_user_id(db, user_id)
    
    # 2. 对每个订单查询物流信息
    logistics_list = []
    for order in orders:
        logistics = logistics_dao.logistics_query_by_order_dao(order["order_id"], db)
        if logistics:
            logistics_list.append(logistics)
    
    return logistics_list


def get_user_orders(db: Session, user_id: str, order_id=None, order_status=None, pay_status=None, logistics_status=None, start_time=None, end_time=None) -> list:
    """获取用户的所有订单（支持筛选）"""
    return order_dao.get_orders_by_user_id(db, user_id, order_id, order_status, pay_status, logistics_status, start_time, end_time)


def get_order_items(order_id: str, db: Session) -> list:
    """获取订单的所有明细"""
    return order_dao.get_order_items_by_order_id(db, order_id)