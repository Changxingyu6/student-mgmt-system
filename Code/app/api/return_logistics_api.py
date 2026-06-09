from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from schema import UUIDStr
from services import return_logistics_func
from schema import return_logistics_request

router = APIRouter(
    prefix="/return_logistics_api",
    tags=["退货物流模块"])

@router.get('/return_logistics/{return_logistics_id}')
def return_logistics_query_api(return_logistics_id: UUIDStr, db=Depends(get_db)):
    result = return_logistics_func.return_logistics_query_func(return_logistics_id, db)
    if not result:
        raise HTTPException(404, 'Not Found')
    return result

@router.get('/return_logistics/after_sales/{after_sales_id}')
def return_logistics_query_by_after_sales_api(after_sales_id: UUIDStr, db=Depends(get_db)):
    result = return_logistics_func.return_logistics_query_by_after_sales_func(after_sales_id, db)
    if not result:
        raise HTTPException(404, 'Not Found')
    return result

@router.post('/return_logistics')
def return_logistics_insert_api(returnlogisticsdata: return_logistics_request.Return_LogisticsRequest, db=Depends(get_db)):
    result = return_logistics_func.return_logistics_insert_func(returnlogisticsdata, db)
    if result:
        return {
            'status': 'success',
            'return_logistics_status': '创建退货物流记录成功'
        }
    else:
        return {
            'status': 'failed',
            'return_logistics_status': '创建退货物流记录失败',
        }

@router.put('/return_logistics')
def return_logistics_update_api(returnlogisticsdata: return_logistics_request.Return_LogisticsUpdate, db=Depends(get_db)):
    result = return_logistics_func.return_logistics_update_func(returnlogisticsdata, db)
    if result:
        return {
            'status': 'success',
            'return_logistics_status': '修改退货物流状态成功'
        }
    else:
        raise HTTPException(404, 'Not Found')

@router.delete('/return_logistics/{return_logistics_id}')
def return_logistics_delete_api(return_logistics_id: UUIDStr, db=Depends(get_db)):
    result = return_logistics_func.return_logistics_delete_func(return_logistics_id, db)
    if result:
        return {
            'status': 'success',
            'return_logistics_status': '退货物流记录已删除'
        }
    raise HTTPException(404, 'Not Found')
