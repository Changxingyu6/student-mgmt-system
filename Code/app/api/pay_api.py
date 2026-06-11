from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from schema import UUIDStr
from services import pay_func
from schema import pay_request
from utils import format_response

router = APIRouter(
    prefix="/pay_api",
    tags=["支付模块"])

@router.get('/pay/{order_id}')
def pay_query_api(order_id: UUIDStr, db=Depends(get_db)):
    """查询支付记录（通过订单ID）"""
    result = pay_func.pay_query_func(order_id, db)
    if not result:
        raise HTTPException(404, 'Not Found')
    return result

@router.get('/pay/user/{user_id}')
def pay_query_by_user_id_api(
    user_id: UUIDStr, 
    order_no: str = None,
    pay_status: str = None,
    pay_method: str = None,
    start_time: str = None,
    end_time: str = None,
    db=Depends(get_db)
):
    """查询用户的所有支付记录（支持筛选）"""
    result = pay_func.pay_query_by_user_id_func(
        user_id, db, order_no, pay_status, pay_method, start_time, end_time
    )
    return format_response(data=result, message="获取用户支付记录成功")


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
    6. 计算积分并升级会员等级
    """
    result = pay_func.process_payment(
        pay_id=pay_request.pay_id,
        user_id=pay_request.user_id,
        pay_password=pay_request.pay_password,
        db=db,
        coupon_id=pay_request.coupon_id
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

@router.delete('/pay/{order_id}')
def pay_delete_api(order_id: UUIDStr, db=Depends(get_db)):
    """删除支付记录"""
    result = pay_func.pay_delete_func(order_id, db)
    if result:
        return format_response(message="支付记录已删除")
    raise HTTPException(404, 'Not Found')