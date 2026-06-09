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
def pay_insert_dao(orderdata: dict, db: Session):
    payment_data = {
        **orderdata,
        "pay_id": generate_uuid(),
        "pay_no": f"P{uuid.uuid4().hex[:24]}",  # 支付流水号
        "pay_status": "待支付",
        "pay_method": "余额",
        "is_abnormal": "0",
        "is_deleted": "0",
        "expire_time": datetime.now() + timedelta(minutes=30),  # 30分钟过期
        # create_time / update_time 数据库自动生成
    }
    order = Payments(**payment_data)
    try:
        db.add(order)
        db.commit()
        return True
    except Exception as e:
        logger.error(f"支付记录插入失败: {str(e)}")
        db.rollback()
        return False

# 更新数据
def pay_update_dao(orderdata: dict, db: Session):
    try:
        order = db.query(Payments).filter(
            Payments.pay_id == orderdata.get("pay_id"),
            Payments.is_deleted == "0"
        ).first()
        if not order:
            return False
        for key, value in orderdata.items():
            if hasattr(order, key):
                setattr(order, key, value)
        db.commit()
        return True
    except Exception as e:
        logger.error(f"支付记录更新失败: {str(e)}")
        db.rollback()
        return False

# 删除数据
def pay_delete_dao(pay_id, db: Session):
    data = db.query(Payments).filter(
        Payments.pay_id == pay_id,
        Payments.is_deleted == "0"
    ).first()
    if data:
        data.is_deleted = "1"
        db.commit()
        return True
    return False
