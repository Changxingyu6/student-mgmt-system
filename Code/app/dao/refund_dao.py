from sqlalchemy.orm import Session
from model.payments_logistics import Refund
from utils import generate_uuid
from datetime import datetime, timedelta, timezone
import uuid
from utils.logger import logger

# 查询数据
def refund_query_dao(refund_id, db: Session):
    data = db.query(Refund).filter(Refund.refund_id == refund_id).first()
    if not data:
        return False
    return {k: v for k, v in data.__dict__.items() if not k.startswith('_')}

# 新增数据
def refund_insert_dao(refunddata: dict, db: Session):
    refund_info = {
        **refunddata,
        "refund_id": generate_uuid(),
        "refund_no": f"R{uuid.uuid4().hex[:24]}",  # 退款流水号
        "refund_status": "待退款",
        "refund_method": "余额",
        "is_abnormal": "0",
        "is_deleted": "0",
        # create_time / update_time 数据库自动生成
    }
    refund = Refund(**refund_info)
    try:
        db.add(refund)
        db.commit()
        return True
    except Exception as e:
        logger.error(f"退款记录插入失败: {str(e)}")
        db.rollback()
        return False

# 更新数据
def refund_update_dao(refunddata: dict, db: Session):
    try:
        refund = db.query(Refund).filter(Refund.refund_id == refunddata.get("refund_id")).first()
        if not refund:
            return False
        for key, value in refunddata.items():
            if hasattr(refund, key):
                setattr(refund, key, value)
        db.commit()
        return True
    except Exception as e:
        logger.error(f"退款记录更新失败: {str(e)}")
        db.rollback()
        return False

# 删除数据
def refund_delete_dao(refund_id, db: Session):
    data = db.query(Refund).filter(Refund.refund_id == refund_id).first()
    if data:
        data.is_deleted = "1"
        db.commit()
        return True
    return False
