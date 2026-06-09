from dao import refund_dao

# 查询方法
def refund_query_func(refund_id, db):
    return refund_dao.refund_query_dao(refund_id, db)

# 新增方法
def refund_insert_func(refunddata, db):
    data = refunddata.model_dump()
    result = refund_dao.refund_insert_dao(data, db)
    db.commit()
    return result

# 更新方法
def refund_update_func(refunddata, db):
    data = refunddata.model_dump()
    result = refund_dao.refund_update_dao(data, db)
    db.commit()
    return result

# 删除方法
def refund_delete_func(refund_id, db):
    result = refund_dao.refund_delete_dao(refund_id, db)
    db.commit()
    return result
