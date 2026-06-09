from dao import pay_dao
from dao import user_dao
from dao import logistics_dao
from services import user_service
from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy import and_


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


def pay_query_by_user_id_func(user_id, db):
    """查询用户的所有支付记录"""
    return pay_dao.pay_query_by_user_id_dao(user_id, db)


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

def process_payment(pay_id: str, user_id: str, pay_password: str, db) -> dict:
    """
    处理支付流程
    参数:
        pay_id: 支付单ID
        user_id: 用户ID
        pay_password: 支付密码
        db: 数据库会话
    返回:
        dict: {"success": bool, "message": str, "data": dict}
    """
    # 1. 获取支付记录信息
    payment_data = pay_dao.pay_query_dao(pay_id, db)
    if not payment_data:
        return {"success": False, "message": "支付记录不存在", "data": None}

    # 检查支付状态
    if payment_data.get("pay_status") != "待支付":
        return {"success": False, "message": "支付状态不是待支付", "data": None}

    # 检查支付是否过期
    expired_result = check_payment_expired(payment_data, db)
    if not expired_result["success"]:
        return {"success": False, "message": expired_result["message"], "data": None}

    # 获取支付金额
    pay_amount = float(payment_data.get("pay_amount", 0))
    if pay_amount <= 0:
        return {"success": False, "message": "支付金额无效", "data": None}

    # 2. 验证支付密码
    pwd_result = verify_pay_password(user_id, pay_password, db)
    if not pwd_result["success"]:
        return {"success": False, "message": pwd_result["message"], "data": None}

    # 3. 检查余额并扣减（user_service.check_balance_sufficient 会直接扣减余额）
    balance_sufficient = user_service.check_balance_sufficient(db, user_id, pay_amount)
    if not balance_sufficient:
        # 余额不足，更新支付状态为支付失败
        pay_dao.pay_update_dao({
            "pay_id": pay_id,
            "pay_status": "支付失败"
        }, db)
        return {
            "success": False,
            "message": f"余额不足，需要：{pay_amount}元",
            "data": None
        }

    # 4. 更新支付状态为支付成功
    update_result = pay_dao.pay_update_dao({
        "pay_id": pay_id,
        "pay_status": "支付成功",
        "pay_time": datetime.now()  # 记录支付时间
    }, db)
    if not update_result:
        return {
            "success": False,
            "message": "支付状态更新失败",
            "data": None
        }
    
    # 5. 自动生成物流信息
    logistics_dao.logistics_insert_dao({
        "order_id": payment_data.get("order_id"),  # 使用支付记录中的订单ID
        "logistics_status": "待发货",
        "track_info": "等待商家发货"
    }, db)

    # 6. 提交事务
    db.commit()

    return {
        "success": True,
        "message": "支付成功，已生成物流信息",
        "data": {
            "pay_id": pay_id,
            "pay_amount": pay_amount,
        }
    }