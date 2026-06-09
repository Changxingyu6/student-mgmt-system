from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from schema import UUIDStr
from services import pay_func
from schema import pay_request
from utils import format_response

router = APIRouter(
    prefix="/pay_api",
    tags=["支付模块"])

@router.get('/pay/{pay_id}')
def pay_query_api(pay_id: UUIDStr, db=Depends(get_db)):
    """查询支付记录"""
    result = pay_func.pay_query_func(pay_id, db)
    if not result:
        raise HTTPException(404, 'Not Found')
    return format_response(data=result, message="获取支付记录成功")

@router.post('/pay')
def pay_insert_api(ordersdata: pay_request.PayRequest, db=Depends(get_db)):
    """创建支付记录"""
    result = pay_func.pay_insert_func(ordersdata, db)
    if result:
        return format_response(data=result, message="提交支付记录成功")
    else:
        return format_response(message="提交支付记录失败", code=500)

@router.post('/pay/process')
def pay_process_api(pay_request: pay_request.PaymentRequest, db=Depends(get_db)):
    """
    处理支付流程
    流程:
    1. 验证支付密码
    2. 检查用户余额
    3. 扣减余额
    4. 更新支付状态为支付成功
    5. 自动生成物流信息
    """
    result = pay_func.process_payment(
        pay_id=pay_request.pay_id,
        user_id=pay_request.user_id,
        pay_password=pay_request.pay_password,
        db=db
    )
    if result["success"]:
        return format_response(data=result["data"], message=result["message"])
    else:
        raise HTTPException(400, result["message"])

@router.put('/pay')
def pay_update_api(ordersdata: pay_request.Payupdata, db=Depends(get_db)):
    """更新支付记录"""
    result = pay_func.pay_update_func(ordersdata, db)
    if result:
        return format_response(message="修改支付记录成功")
    else:
        raise HTTPException(404, 'Not Found')

@router.delete('/pay/{pay_id}')
def pay_delete_api(pay_id: UUIDStr, db=Depends(get_db)):
    """删除支付记录"""
    result = pay_func.pay_delete_func(pay_id, db)
    if result:
        return format_response(message="支付记录已删除")
    raise HTTPException(404, 'Not Found')