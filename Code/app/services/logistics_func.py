from dao import logistics_dao
from dao import order_dao

# 查询方法
def logistics_query_func(logistics_id, db):
    return logistics_dao.logistics_query_dao(logistics_id, db)

# 按订单查询方法
def logistics_query_by_order_func(order_id, db):
    return logistics_dao.logistics_query_by_order_dao(order_id, db)

# 新增方法
def logistics_insert_func(logisticsdata, db):
    data = logisticsdata.model_dump()
    result = logistics_dao.logistics_insert_dao(data, db)
    db.commit()
    return result

# 更新方法
def logistics_update_func(logisticsdata, db):
    data = logisticsdata.model_dump()
    result = logistics_dao.logistics_update_dao(data, db)
    db.commit()
    return result

# 删除方法
def logistics_delete_func(logistics_id, db):
    result = logistics_dao.logistics_delete_dao(logistics_id, db)
    db.commit()
    return result

# 确认收货方法
def logistics_confirm_receipt_func(logistics_id, db):
    """
    确认收货
    - 更新物流状态为"已签收"
    - 更新订单状态为"已完成"
    - 更新订单的物流状态为"已签收"
    """
    # 1. 获取物流记录
    logistics = logistics_dao.logistics_query_dao(logistics_id, db)
    if not logistics:
        return False
    
    # 2. 获取订单ID
    order_id = logistics.get("order_id")
    if not order_id:
        return False
    
    # 3. 更新物流状态为"已签收"
    logistics_dao.logistics_update_dao({
        "logistics_id": logistics_id,
        "logistics_status": "已签收",
        "track_info": "已签收"
    }, db)
    
    # 4. 更新订单状态为"已完成"，物流状态为"已签收"
    order_dao.update_order_status(db, order_id, {
        "order_status": "completed",
        "logistics_status": "已签收"
    })
    
    # 5. 提交事务
    db.commit()
    
    return logistics
