from sqlalchemy import and_
from sqlalchemy.orm import Session
from model.payments_logistics import Payments
from utils import generate_uuid
from datetime import datetime,timedelta
import uuid
from utils import logger

# 查询数据（通过订单ID）
def pay_query_dao(order_id, db: Session):
    data = db.query(Payments).filter(
        Payments.order_id == order_id,
        Payments.is_deleted == "0"
    ).first()
    if not data:
        return False
    return {k: v for k, v in data.__dict__.items() if not k.startswith('_')}

# 查询数据（通过支付单ID）
def pay_query_by_pay_id_dao(pay_id, db: Session):
    data = db.query(Payments).filter(
        Payments.pay_id == pay_id,
        Payments.is_deleted == "0"
    ).first()
    if not data:
        return False
    return {k: v for k, v in data.__dict__.items() if not k.startswith('_')}

# 新增数据
def pay_insert_dao(orderdata: dict, db: Session) -> bool:
    payment_data = {
        **orderdata,
        "pay_id": generate_uuid(),
        "pay_no": f"P{uuid.uuid4().hex[:24]}",
        "pay_status": "待支付",
        "pay_method": "余额",
        "is_abnormal": "0",
        "is_deleted": "0",
        "expire_time": datetime.now() + timedelta(minutes=30),
    }
    order = Payments(**payment_data)
    db.add(order)
    return True

# 更新数据
def pay_update_dao(orderdata: dict, db: Session) -> bool:
    order = db.query(Payments).filter(
        Payments.pay_id == orderdata.get("pay_id"),
        Payments.is_deleted == "0"
    ).first()
    if not order:
        return False
    for key, value in orderdata.items():
        if hasattr(order, key):
            setattr(order, key, value)
    return True

# 查询用户的所有支付记录
def pay_query_by_user_id_dao(user_id, db: Session):
    data = db.query(Payments).filter(
        Payments.user_id == user_id,
        Payments.is_deleted == "0"
    ).order_by(Payments.create_time.desc()).all()
    if not data:
        return []
    return [{k: v for k, v in item.__dict__.items() if not k.startswith('_')} for item in data]

# 删除数据
def pay_delete_dao(pay_id, db: Session) -> bool:
    data = db.query(Payments).filter(
        Payments.pay_id == pay_id,
        Payments.is_deleted == "0"
    ).first()
    if data:
        data.is_deleted = "1"
        return True
    return False