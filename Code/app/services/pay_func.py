from dao import pay_dao
from dao import user_dao
from dao import logistics_dao
from dao import order_dao
from dao import goods_dao
from services import user_service
from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy import and_
import logging

logger = logging.getLogger(__name__)


def pay_query_func(order_id, db):
    """查询支付记录（通过订单ID）"""
    return pay_dao.pay_query_dao(order_id, db)


def pay_insert_func(orderdata, db):
    """创建支付记录"""
    data = orderdata.model_dump()
    return pay_dao.pay_insert_dao(data, db)


def pay_update_func(orderdata, db):
    """更新支付记录"""
    data = orderdata.model_dump()
    return pay_dao.pay_update_dao(data, db)


def pay_delete_func(order_id, db):
    """删除支付记录"""
    return pay_dao.pay_delete_dao(order_id, db)


def pay_query_by_user_id_func(user_id, db, order_no=None, pay_status=None, pay_method=None, start_time=None, end_time=None):
    """查询用户的所有支付记录（支持筛选）"""
    return pay_dao.pay_query_by_user_id_dao(user_id, db, order_no, pay_status, pay_method, start_time, end_time)


def verify_pay_password(user_id: str, pay_password: str, db) -> dict:
    """
    验证支付密码
    参数:
        user_id: 用户ID
        pay_password: 支付密码（明文）
        db: 数据库会话

    返回:
        dict: {"success": bool, "message": str}
    """
    # 调用 user_service 验证支付密码
    result = user_service.verify_pay_password(db, user_id, pay_password)
    if not result:
        return {"success": False, "message": "支付密码错误"}

    return {"success": True, "message": "支付密码验证通过"}


def check_payment_expired(payment_data: dict, db) -> dict:
    """
    检查支付是否超过30分钟过期时间，如果过期则自动关闭支付记录

    参数:
        payment_data: 支付记录数据（包含 expire_time 和 pay_id 字段）
        db: 数据库会话

    返回:
        dict: {"success": bool, "message": str, "expired": bool}
    """
    expire_time = payment_data.get("expire_time")
    pay_id = payment_data.get("pay_id")

    if not expire_time:
        return {"success": False, "message": "支付记录缺少过期时间", "expired": False}

    # 获取当前时间（带时区）
    current_time = datetime.now(timezone.utc)

    # 如果 expire_time 不带时区，转换为 UTC
    if expire_time.tzinfo is None:
        expire_time = expire_time.replace(tzinfo=timezone.utc)

    # 检查是否过期
    if current_time > expire_time:
        # 支付已过期，自动更新状态为"已关闭"
        pay_dao.pay_update_dao({
            "pay_id": pay_id,
            "pay_status": "已关闭"
        }, db)
        return {
            "success": False,
            "message": "支付已过期，支付记录已自动关闭",
            "expired": True
        }

    return {
        "success": True,
        "message": "支付在有效期内",
        "expired": False
    }


def close_expired_payments(db) -> dict:
    """
    定时任务：批量关闭所有过期的支付记录
    查询所有状态为"待支付"且过期时间小于当前时间的支付记录，
    将其状态更新为"已关闭"

    参数:
        db: 数据库会话

    返回:
        dict: {"success": bool, "message": str, "closed_count": int}
    """
    from model.payments_logistics import Payments

    try:
        current_time = datetime.now(timezone.utc)

        # 查询所有过期的待支付记录，过期时间小于当前时间说明过期（超过30分钟）
        expired_payments = db.query(Payments).filter(
            and_(
                Payments.pay_status == "待支付",
                Payments.expire_time < current_time
            )
        ).all()

        closed_count = 0
        for payment in expired_payments:
            payment.pay_status = "已关闭"
            closed_count += 1

        if closed_count > 0:
            db.commit()

        return {
            "success": True,
            "message": f"成功关闭 {closed_count} 条过期支付记录",
            "closed_count": closed_count
        }
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "message": f"关闭过期支付记录失败: {str(e)}",
            "closed_count": 0
        }

def process_payment(pay_id: str, user_id: str, pay_password: str, db, coupon_id: str = None) -> dict:
    """
    处理支付流程
    参数:
        pay_id: 支付单ID
        user_id: 用户ID
        pay_password: 支付密码
        db: 数据库会话
        coupon_id: 优惠券ID（可选）
    返回:
        dict: {"success": bool, "message": str, "data": dict}
    """
    # 1. 获取支付记录信息
    payment_data = pay_dao.pay_query_by_pay_id_dao(pay_id, db)
    if not payment_data:
        return {"success": False, "message": "支付记录不存在", "data": None}

    # 检查支付状态
    if payment_data.get("pay_status") != "待支付":
        return {"success": False, "message": "支付状态不是待支付", "data": None}

    # 检查支付是否过期
    expired_result = check_payment_expired(payment_data, db)
    if not expired_result["success"]:
        return {"success": False, "message": expired_result["message"], "data": None}

    # 获取支付金额（订单创建时已扣减会员折扣）
    pay_amount = float(payment_data.get("pay_amount", 0))
    if pay_amount <= 0:
        return {"success": False, "message": "支付金额无效", "data": None}

    # 2. 处理优惠券（如果有）
    coupon_discount = 0
    used_coupon_id = None
    if coupon_id:
        from dao import coupon_dao
        # 获取用户优惠券
        user_coupon = coupon_dao.get_user_coupon_by_id(db, coupon_id)
        if user_coupon and user_coupon.user_id == user_id and user_coupon.status == 1:
            # 获取优惠券模板信息
            coupon = coupon_dao.get_coupon_by_id(db, user_coupon.coupon_id)
            if coupon:
                # 检查是否满足使用门槛
                if pay_amount >= coupon.min_spend:
                    coupon_discount = float(coupon.face_value)
                    used_coupon_id = coupon_id
                    logger.debug(f"使用优惠券: {coupon_id}, 抵扣金额: {coupon_discount}")
                else:
                    return {"success": False, "message": f"优惠券未满足使用门槛，需要满{coupon.min_spend}元", "data": None}
            else:
                return {"success": False, "message": "优惠券模板不存在", "data": None}
        else:
            return {"success": False, "message": "优惠券无效或已使用", "data": None}
    
    # 计算最终支付金额
    final_pay_amount = max(0, pay_amount - coupon_discount)
    logger.debug(f"原始支付金额: {pay_amount}, 优惠券抵扣: {coupon_discount}, 最终支付金额: {final_pay_amount}")

    # 3. 验证支付密码
    pwd_result = verify_pay_password(user_id, pay_password, db)
    if not pwd_result["success"]:
        return {"success": False, "message": pwd_result["message"], "data": None}

    # 4. 获取订单明细并检查库存
    order_id = payment_data.get("order_id")
    order_items = order_dao.get_order_items_by_order_id(db, order_id)
    
    if not order_items:
        return {"success": False, "message": "订单明细为空", "data": None}
    
    # 检查库存是否充足
    for item in order_items:
        goods = goods_dao.get_goods_by_id(db, item["product_id"])
        if not goods:
            # 商品不存在，恢复库存
            for order_item in order_items:
                stocks = goods_dao.get_stock_by_goods_id(db, order_item["product_id"])
                if stocks:
                    first_stock = stocks[0]
                    new_stock_num = first_stock.stock_num + order_item["quantity"]
                    goods_dao.update_stock(db, first_stock, new_stock_num)
            db.commit()
            return {"success": False, "message": f"商品不存在: {item['product_name']}，库存已恢复", "data": None}
        
        # 通过商品ID获取库存
        stocks = goods_dao.get_stock_by_goods_id(db, item["product_id"])
        if not stocks:
            # 没有库存记录，恢复库存
            for order_item in order_items:
                order_stocks = goods_dao.get_stock_by_goods_id(db, order_item["product_id"])
                if order_stocks:
                    first_stock = order_stocks[0]
                    new_stock_num = first_stock.stock_num + order_item["quantity"]
                    goods_dao.update_stock(db, first_stock, new_stock_num)
            db.commit()
            return {"success": False, "message": f"{item['product_name']}没有库存记录，库存已恢复", "data": None}
        
        # 计算该商品所有规格的总库存
        total_stock = sum(stock.stock_num for stock in stocks)
        if total_stock < item["quantity"]:
            # 库存不足，恢复之前扣减的库存（创建订单时已扣减）
            for order_item in order_items:
                order_stocks = goods_dao.get_stock_by_goods_id(db, order_item["product_id"])
                if order_stocks:
                    first_stock = order_stocks[0]
                    new_stock_num = first_stock.stock_num + order_item["quantity"]
                    goods_dao.update_stock(db, first_stock, new_stock_num)
            db.commit()
            return {"success": False, "message": f"{item['product_name']}库存不足，库存已恢复", "data": None}

    # 5. 检查余额并扣减（使用最终支付金额）
    balance_sufficient = user_service.check_balance_sufficient(db, user_id, final_pay_amount)
    if not balance_sufficient:
        # 余额不足，恢复库存
        for item in order_items:
            # 获取该商品所有规格的库存
            stocks = goods_dao.get_stock_by_goods_id(db, item["product_id"])
            if stocks:
                # 将库存恢复（增加购买数量）
                # 简单处理：平均分配到各个规格，或者加到第一个规格
                if stocks:
                    first_stock = stocks[0]
                    new_stock_num = first_stock.stock_num + item["quantity"]
                    goods_dao.update_stock(db, first_stock, new_stock_num)
        
        # 更新支付状态为支付失败
        pay_dao.pay_update_dao({
            "pay_id": pay_id,
            "pay_status": "支付失败"
        }, db)
        db.commit()
        
        return {
            "success": False,
            "message": f"余额不足，需要：{final_pay_amount}元，库存已恢复",
            "data": None
        }

    # 6. 更新支付状态为支付成功（记录实际支付金额）
    update_result = pay_dao.pay_update_dao({
        "pay_id": pay_id,
        "pay_status": "支付成功",
        "pay_time": datetime.now(),
        "pay_amount": final_pay_amount  # 更新为实际支付金额
    }, db)
    if not update_result:
        # 支付状态更新失败，恢复库存
        for item in order_items:
            stocks = goods_dao.get_stock_by_goods_id(db, item["product_id"])
            if stocks:
                first_stock = stocks[0]
                new_stock_num = first_stock.stock_num + item["quantity"]
                goods_dao.update_stock(db, first_stock, new_stock_num)
        
        db.commit()
        return {
            "success": False,
            "message": "支付状态更新失败，库存已恢复",
            "data": None
        }
    
    # 7. 更新订单状态为已支付
    order_update_result = order_dao.update_order_status(db, order_id, {
        "order_status": "paid",
        "pay_status": "paid"
    })
    if not order_update_result:
        # 订单状态更新失败，恢复库存并回滚支付状态
        for item in order_items:
            stocks = goods_dao.get_stock_by_goods_id(db, item["product_id"])
            if stocks:
                first_stock = stocks[0]
                new_stock_num = first_stock.stock_num + item["quantity"]
                goods_dao.update_stock(db, first_stock, new_stock_num)
        
        # 回滚支付状态
        pay_dao.pay_update_dao({
            "pay_id": pay_id,
            "pay_status": "待支付",
            "pay_time": None,
            "pay_amount": pay_amount  # 恢复原始金额
        }, db)
        
        db.commit()
        return {
            "success": False,
            "message": "订单状态更新失败，库存已恢复，支付状态已回滚",
            "data": None
        }
    
    # 8. 自动生成物流信息
    logistics_dao.logistics_insert_dao({
        "order_id": order_id,
        "logistics_status": "待发货",
        "track_info": "等待商家发货"
    }, db)

    # 9. 标记优惠券为已使用（如果使用了优惠券）并写入使用日志
    if used_coupon_id:
        from dao import coupon_dao
        coupon_dao.update_user_coupon_status(db, used_coupon_id, 3)  # 3 = 已使用
        logger.debug(f"优惠券已标记为已使用: {used_coupon_id}")

        # 写入 coupon_use_log 记录
        try:
            coupon_dao.create_use_log(db, {
                "user_coupon_id": used_coupon_id,
                "user_id": user_id,
                "order_id": order_id,
                "status": 1,  # 1 = 使用成功
                "remark": f"支付时使用优惠券，抵扣{coupon_discount}元",
            })
            logger.debug(f"已写入优惠券使用日志: order_id={order_id}")
        except Exception as e:
            logger.error(f"写入优惠券使用日志失败: {e}")

    # 10. 计算积分并升级会员等级（按原价计算，每10元得1积分）
    order = order_dao.get_order_by_id(db, order_id)
    if order:
        original_amount = float(order.get('total_amount', 0))
        points_earned = int(original_amount / 10)
        user_service.update_user_points_and_level(user_id, points_earned, db)

    # 11. 提交事务
    db.commit()

    return {
        "success": True,
        "message": "支付成功，已生成物流信息",
        "data": {
            "pay_id": pay_id,
            "pay_amount": final_pay_amount,
            "coupon_discount": coupon_discount,
            "points_earned": points_earned if order else 0
        }
    }