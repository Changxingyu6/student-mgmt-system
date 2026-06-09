from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from schema import UUIDStr
from services import refund_func
from schema import refund_request
from utils import format_response

router = APIRouter(
    prefix="/refund_api",
    tags=["退款模块"])

@router.get('/refund/{refund_id}')
def refund_query_api(refund_id: UUIDStr, db=Depends(get_db)):
    result = refund_func.refund_query_func(refund_id, db)
    if not result:
        raise HTTPException(404, 'Not Found')
    return format_response(data=result, message="获取退款记录成功")

@router.post('/refund')
def refund_insert_api(refunddata: refund_request.RefundRequest, db=Depends(get_db)):
    result = refund_func.refund_insert_func(refunddata, db)
    if result:
        return format_response(data=result, message="提交退款申请成功")
    else:
        return format_response(message="提交退款申请失败", code=500)

@router.put('/refund')
def refund_update_api(refunddata: refund_request.RefundUpdate, db=Depends(get_db)):
    result = refund_func.refund_update_func(refunddata, db)
    if result:
        return format_response(message="修改退款状态成功")
    else:
        raise HTTPException(404, 'Not Found')

@router.delete('/refund/{refund_id}')
def refund_delete_api(refund_id: UUIDStr, db=Depends(get_db)):
    result = refund_func.refund_delete_func(refund_id, db)
    if result:
        return format_response(message="退款记录已删除")
    raise HTTPException(404, 'Not Found')