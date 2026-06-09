from sqlalchemy.orm import Session
from model.payments_logistics import Refund
from utils import generate_uuid
from datetime import datetime, timedelta, timezone
import uuid
from utils.logger import logger

# 查询数据
def refund_query_dao(refund_id, db: Session):
    data = db.query(Refund).filter(
        Refund.refund_id == refund_id,
        Refund.is_deleted == "0"
    ).first()
    if not data:
        return False
    return {k: v for k, v in data.__dict__.items() if not k.startswith('_')}

# 新增数据
def refund_insert_dao(refunddata: dict, db: Session) -> bool:
    refund_info = {
        **refunddata,
        "refund_id": generate_uuid(),
        "refund_no": f"R{uuid.uuid4().hex[:24]}",
        "refund_status": "待退款",
        "refund_method": "余额",
        "is_abnormal": "0",
        "is_deleted": "0",
    }
    refund = Refund(**refund_info)
    db.add(refund)
    return True

# 更新数据
def refund_update_dao(refunddata: dict, db: Session) -> bool:
    refund = db.query(Refund).filter(
        Refund.refund_id == refunddata.get("refund_id"),
        Refund.is_deleted == "0"
    ).first()
    if not refund:
        return False
    for key, value in refunddata.items():
        if hasattr(refund, key):
            setattr(refund, key, value)
    return True

# 删除数据
def refund_delete_dao(refund_id, db: Session) -> bool:
    data = db.query(Refund).filter(
        Refund.refund_id == refund_id,
        Refund.is_deleted == "0"
    ).first()
    if data:
        data.is_deleted = "1"
        return True
    return False