from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from schema import UUIDStr
from services import logistics_func
from schema import logistics_request
from utils import format_response

router = APIRouter(
    prefix="/logistics_api",
    tags=["物流模块"])

@router.get('/logistics/{logistics_id}')
def logistics_query_api(logistics_id: UUIDStr, db=Depends(get_db)):
    result = logistics_func.logistics_query_func(logistics_id, db)
    if not result:
        raise HTTPException(404, 'Not Found')
    return format_response(data=result, message="获取物流信息成功")

@router.get('/logistics/order/{order_id}')
def logistics_query_by_order_api(order_id: UUIDStr, db=Depends(get_db)):
    result = logistics_func.logistics_query_by_order_func(order_id, db)
    if not result:
        raise HTTPException(404, 'Not Found')
    return format_response(data=result, message="获取物流信息成功")

@router.post('/logistics')
def logistics_insert_api(logisticsdata: logistics_request.LogisticsRequest, db=Depends(get_db)):
    result = logistics_func.logistics_insert_func(logisticsdata, db)
    if result:
        return format_response(data=result, message="创建物流记录成功")
    else:
        return format_response(data=None, message="创建物流记录失败", code=500)

@router.put('/logistics')
def logistics_update_api(logisticsdata: logistics_request.LogisticsUpdate, db=Depends(get_db)):
    result = logistics_func.logistics_update_func(logisticsdata, db)
    if result:
        return format_response(data=result, message="修改物流状态成功")
    else:
        raise HTTPException(404, 'Not Found')

@router.get('/logistics/user/{user_id}')
def logistics_query_by_user_api(user_id: UUIDStr, db=Depends(get_db)):
    """查询用户的所有物流记录"""
    from services import order_service
    result = order_service.get_user_logistics(user_id, db)
    return format_response(data=result, message="获取用户物流记录成功")

@router.put('/logistics/{logistics_id}/confirm')
def logistics_confirm_receipt_api(logistics_id: UUIDStr, db=Depends(get_db)):
    """确认收货"""
    result = logistics_func.logistics_confirm_receipt_func(logistics_id, db)
    if result:
        return format_response(data=result, message="确认收货成功")
    else:
        raise HTTPException(500, '确认收货失败')