"""
订单管理 API 路由
"""
from fastapi import APIRouter, Request, Depends, Body
from sqlalchemy.orm import Session
from services import order_service
from utils import format_response
from database import get_db

router = APIRouter(prefix="/orders", tags=["订单管理"])


@router.get("/user/{user_id}", summary="获取用户订单列表")
def get_user_orders(
    user_id: str,
    order_id: str = None,
    order_status: str = None,
    pay_status: str = None,
    logistics_status: str = None,
    start_time: str = None,
    end_time: str = None,
    db: Session = Depends(get_db)
):
    """获取用户的所有订单（支持筛选）"""
    try:
        orders = order_service.get_user_orders(db, user_id, order_id, order_status, pay_status, logistics_status, start_time, end_time)
        return format_response(data=orders, message="获取订单列表成功")
    except Exception as e:
        return format_response(code=500, message=str(e))


@router.post("/create-from-cart", summary="从购物车创建订单")
def create_order_from_cart(
    request: Request,
    address_info: dict = Body(None),
    db: Session = Depends(get_db)
):
    """从购物车选中商品创建订单"""
    # 获取用户 ID（从请求状态中）
    user_info = getattr(request.state, 'user', None)
    if not user_info or not user_info.get('id'):
        return format_response(code=401, message="未登录")
    
    user_id = user_info['id']
    
    try:
        result = order_service.create_order_from_cart(db, user_id, address_info)
        return format_response(data=result, message="订单创建成功")
    except Exception as e:
        # 捕获 HTTPException
        if hasattr(e, 'status_code'):
            return format_response(code=e.status_code, message=str(e.detail))
        return format_response(code=500, message=str(e))


@router.get("/items/{order_id}", summary="获取订单明细")
def get_order_items(order_id: str, db: Session = Depends(get_db)):
    """获取订单的所有明细"""
    try:
        items = order_service.get_order_items(order_id, db)
        return format_response(data=items, message="获取订单明细成功")
    except Exception as e:
        return format_response(code=500, message=str(e))