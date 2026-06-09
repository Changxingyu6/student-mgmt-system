from dao import return_logistics_dao

# 查询方法
def return_logistics_query_func(return_logistics_id, db):
    return return_logistics_dao.return_logistics_query_dao(return_logistics_id, db)

# 按售后单查询方法
def return_logistics_query_by_after_sales_func(after_sales_id, db):
    return return_logistics_dao.return_logistics_query_by_after_sales_dao(after_sales_id, db)

# 新增方法
def return_logistics_insert_func(returnlogisticsdata, db):
    data = returnlogisticsdata.model_dump()
    result = return_logistics_dao.return_logistics_insert_dao(data, db)
    db.commit()
    return result

# 更新方法
def return_logistics_update_func(returnlogisticsdata, db):
    data = returnlogisticsdata.model_dump()
    result = return_logistics_dao.return_logistics_update_dao(data, db)
    db.commit()
    return result

# 删除方法
def return_logistics_delete_func(return_logistics_id, db):
    result = return_logistics_dao.return_logistics_delete_dao(return_logistics_id, db)
    db.commit()
    return result
