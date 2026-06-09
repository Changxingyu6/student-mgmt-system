from dao import logistics_dao

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
