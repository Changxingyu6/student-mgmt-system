from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from schema import UUIDStr
from services import logistics_func
from schema import logistics_request

router = APIRouter(
    prefix="/logistics_api",
    tags=["物流模块"])

@router.get('/logistics/{logistics_id}')
def logistics_query_api(logistics_id: UUIDStr, db=Depends(get_db)):
    result = logistics_func.logistics_query_func(logistics_id, db)
    if not result:
        raise HTTPException(404, 'Not Found')
    return result

@router.get('/logistics/order/{order_id}')
def logistics_query_by_order_api(order_id: UUIDStr, db=Depends(get_db)):
    result = logistics_func.logistics_query_by_order_func(order_id, db)
    if not result:
        raise HTTPException(404, 'Not Found')
    return result

@router.post('/logistics')
def logistics_insert_api(logisticsdata: logistics_request.LogisticsRequest, db=Depends(get_db)):
    result = logistics_func.logistics_insert_func(logisticsdata, db)
    if result:
        return {
            'status': 'success',
            'logistics_status': '创建物流记录成功'
        }
    else:
        return {
            'status': 'failed',
            'logistics_status': '创建物流记录失败',
        }

@router.put('/logistics')
def logistics_update_api(logisticsdata: logistics_request.LogisticsUpdate, db=Depends(get_db)):
    result = logistics_func.logistics_update_func(logisticsdata, db)
    if result:
        return {
            'status': 'success',
            'logistics_status': '修改物流状态成功'
        }
    else:
        raise HTTPException(404, 'Not Found')

@router.delete('/logistics/{logistics_id}')
def logistics_delete_api(logistics_id: UUIDStr, db=Depends(get_db)):
    result = logistics_func.logistics_delete_func(logistics_id, db)
    if result:
        return {
            'status': 'success',
            'logistics_status': '物流记录已删除'
        }
    raise HTTPException(404, 'Not Found')
