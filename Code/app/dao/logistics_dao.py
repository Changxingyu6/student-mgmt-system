from sqlalchemy.orm import Session
from model.payments_logistics import Logistics
from utils import generate_uuid
from datetime import datetime, timezone
from utils.logger import logger

# 查询数据
def logistics_query_dao(logistics_id, db: Session):
    data = db.query(Logistics).filter(
        Logistics.logistics_id == logistics_id,
        Logistics.is_deleted == "0"
    ).first()
    if not data:
        return False
    return {k: v for k, v in data.__dict__.items() if not k.startswith('_')}

# 按订单ID查询
def logistics_query_by_order_dao(order_id, db: Session):
    data = db.query(Logistics).filter(
        Logistics.order_id == order_id,
        Logistics.is_deleted == "0"
    ).first()
    if not data:
        return False
    return {k: v for k, v in data.__dict__.items() if not k.startswith('_')}

# 新增数据
def logistics_insert_dao(logisticsdata: dict, db: Session):
    logistics_info = {
        **logisticsdata,
        "logistics_id": generate_uuid(),
        "logistics_status": "待发货",
        "is_deleted": "0",
        # create_time / update_time 数据库自动生成
    }
    logistics = Logistics(**logistics_info)
    try:
        db.add(logistics)
        db.commit()
        return True
    except Exception as e:
        logger.error(f"物流记录插入失败: {str(e)}")
        db.rollback()
        return False

# 更新数据
def logistics_update_dao(logisticsdata: dict, db: Session):
    try:
        logistics = db.query(Logistics).filter(
            Logistics.logistics_id == logisticsdata.get("logistics_id"),
            Logistics.is_deleted == "0"
        ).first()
        if not logistics:
            return False
        for key, value in logisticsdata.items():
            if hasattr(logistics, key):
                setattr(logistics, key, value)
        db.commit()
        return True
    except Exception as e:
        logger.error(f"物流记录更新失败: {str(e)}")
        db.rollback()
        return False

# 删除数据
def logistics_delete_dao(logistics_id, db: Session):
    data = db.query(Logistics).filter(
        Logistics.logistics_id == logistics_id,
        Logistics.is_deleted == "0"
    ).first()
    if data:
        data.is_deleted = "1"
        db.commit()
        return True
    return False
