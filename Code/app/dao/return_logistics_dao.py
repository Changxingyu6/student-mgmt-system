from sqlalchemy.orm import Session
from model.payments_logistics import Return_Logistics
from utils import generate_uuid
from datetime import datetime, timezone
from utils.logger import logger

# 查询数据
def return_logistics_query_dao(return_logistics_id, db: Session):
    data = db.query(Return_Logistics).filter(
        Return_Logistics.return_logistics_id == return_logistics_id,
        Return_Logistics.is_deleted == "0"
    ).first()
    if not data:
        return False
    return {k: v for k, v in data.__dict__.items() if not k.startswith('_')}

# 按售后单ID查询
def return_logistics_query_by_after_sales_dao(after_sales_id, db: Session):
    data = db.query(Return_Logistics).filter(
        Return_Logistics.after_sales_id == after_sales_id,
        Return_Logistics.is_deleted == "0"
    ).first()
    if not data:
        return False
    return {k: v for k, v in data.__dict__.items() if not k.startswith('_')}

# 新增数据
def return_logistics_insert_dao(returnlogisticsdata: dict, db: Session):
    return_logistics_info = {
        **returnlogisticsdata,
        "return_logistics_id": generate_uuid(),
        "return_logistics_status": "待发货",
        "is_deleted": "0",
        # create_time / update_time 数据库自动生成
    }
    return_logistics = Return_Logistics(**return_logistics_info)
    try:
        db.add(return_logistics)
        db.commit()
        return True
    except Exception as e:
        logger.error(f"退货物流记录插入失败: {str(e)}")
        db.rollback()
        return False

# 更新数据
def return_logistics_update_dao(returnlogisticsdata: dict, db: Session):
    try:
        return_logistics = db.query(Return_Logistics).filter(
            Return_Logistics.return_logistics_id == returnlogisticsdata.get("return_logistics_id"),
            Return_Logistics.is_deleted == "0"
        ).first()
        if not return_logistics:
            return False
        for key, value in returnlogisticsdata.items():
            if hasattr(return_logistics, key):
                setattr(return_logistics, key, value)
        db.commit()
        return True
    except Exception as e:
        logger.error(f"退货物流记录更新失败: {str(e)}")
        db.rollback()
        return False

# 删除数据
def return_logistics_delete_dao(return_logistics_id, db: Session):
    data = db.query(Return_Logistics).filter(
        Return_Logistics.return_logistics_id == return_logistics_id,
        Return_Logistics.is_deleted == "0"
    ).first()
    if data:
        data.is_deleted = "1"
        db.commit()
        return True
    return False
