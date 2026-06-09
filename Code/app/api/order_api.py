"""
订单管理 API 路由
"""
from fastapi import APIRouter, Request, Depends, Body
from sqlalchemy.orm import Session
from services import order_service
from utils import format_response
from database import get_db

router = APIRouter(prefix="/orders", tags=["订单管理"])


@router.post("/create-from-cart", summary="从购物车创建订单")
def create_order_from_cart(
    request: Request,
    address_info: dict = Body(None),
    db: Session = Depends(get_db)
):
    """从购物车选中商品创建订单"""
    # 获取用户ID（从请求状态中）
    user_info = getattr(request.state, 'user', None)
    if not user_info or not user_info.get('id'):
        return format_response(code=401, message="未登录")
    
    user_id = user_info['id']
    
    try:
        result = order_service.create_order_from_cart(db, user_id, address_info)
        return format_response(data=result, message="订单创建成功")
    except Exception as e:
        # 捕获HTTPException
        if hasattr(e, 'status_code'):
            return format_response(code=e.status_code, message=str(e.detail))
        return format_response(code=500, message=str(e))