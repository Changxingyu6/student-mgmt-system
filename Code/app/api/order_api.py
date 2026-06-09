"""
订单管理 API 路由
包含订单创建、查询、状态修改、售后管理等接口
"""
from fastapi import APIRouter, Request, Depends, Body, Query, Path
from sqlalchemy.orm import Session
from services import order_service, order_item_service, after_sale_service
from utils import format_response, require_roles
from database import get_db
from schema.order import *

router = APIRouter(prefix="/orders", tags=["订单管理"])


# ========== 订单主表接口 ==========

@router.get("/", summary="获取订单列表（多条件筛选）")
def get_order_list(
    request: Request,
    order_id: Optional[str] = Query(None, description="订单编号"),
    user_id: Optional[str] = Query(None, description="用户ID"),
    order_status: Optional[str] = Query(None, description="订单状态"),
    pay_status: Optional[str] = Query(None, description="支付状态"),
    logistics_status: Optional[str] = Query(None, description="物流状态"),
    start_time: Optional[str] = Query(None, description="开始时间（ISO格式）"),
    end_time: Optional[str] = Query(None, description="结束时间（ISO格式）"),
    page: int = Query(1, description="页码"),
    size: int = Query(10, description="每页数量"),
    db: Session = Depends(get_db)
):
    """
    获取订单列表（多条件筛选）
    
    支持的筛选条件：
    - 订单编号、用户ID
    - 订单状态、支付状态、物流状态
    - 时间范围
    """
    # 临时模拟用户信息
    current_user = {"id": "U123456", "username": "test_user"}
    result = order_service.get_order_list(
        db, current_user, order_id, user_id, order_status, pay_status,
        logistics_status, start_time, end_time, page, size
    )
    return format_response(data=result, message="获取成功")


@router.get("/{order_id}", summary="获取订单详情")
def get_order_detail(
    order_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """获取订单详情（含商品明细）"""
    # 临时模拟用户信息
    current_user = {"id": "U123456", "username": "test_user"}
    result = order_service.get_order_detail(db, current_user, order_id)
    return format_response(data=result, message="获取成功")


@router.post("/", summary="创建订单")
def create_order(
    request: Request,
    order_request: OrderCreateRequest = Body(...),
    db: Session = Depends(get_db)
):
    # 临时模拟用户信息
    current_user = {"id": "U123456", "username": "test_user"}
    result = order_service.create_order(db, current_user, order_request)
    return format_response(data=result, message="订单创建成功")


@router.put("/{order_id}/status", summary="修改订单状态")
def update_order_status(
    request: Request,
    order_id: str = Path(... , description="订单编号"),
    status_request: OrderStatusUpdateRequest = Body(...),
    db: Session = Depends(get_db)
):
    """修改订单状态（管理员操作）"""
    # 临时模拟用户信息
    current_user = {"id": "U123456", "username": "test_user"}
    result = order_service.update_order_status(db, order_id, status_request)
    return format_response(data=result, message="修改成功")


# ========== 订单明细表接口 ==========

@router.get("/{order_id}/items", summary="获取订单明细列表")
def get_order_items(
    order_id: str,
    request: Request,
    page: int = Query(1, description="页码"),
    size: int = Query(10, description="每页数量"),
    db: Session = Depends(get_db)
):
    """获取订单明细列表"""
    # 临时模拟用户信息
    current_user = {"id": "U123456", "username": "test_user"}
    result = order_item_service.get_order_items(db, order_id, current_user, page, size)
    return format_response(data=result, message="获取成功")


@router.get("/items/{item_id}", summary="获取订单明细详情")
def get_order_item_detail(
    item_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """获取订单明细详情"""
    # 临时模拟用户信息
    current_user = {"id": "U123456", "username": "test_user"}
    result = order_item_service.get_order_item_detail(db, item_id, current_user)
    return format_response(data=result, message="获取成功")


# ========== 售后订单接口 ==========

@router.get("/aftersale", summary="查询售后订单")
def get_after_sale_list(
    request: Request,
    order_id: Optional[str] = Query(None, description="订单编号"),
    user_id: Optional[str] = Query(None, description="用户ID"),
    audit_status: Optional[str] = Query(None, description="审核状态"),
    after_sale_type: Optional[str] = Query(None, description="售后类型"),
    page: int = Query(1, description="页码"),
    size: int = Query(10, description="每页数量"),
    db: Session = Depends(get_db)
):
    """查询售后订单列表"""
    # 临时模拟用户信息
    current_user = {"id": "U123456", "username": "test_user"}
    result = after_sale_service.get_after_sale_list(
        db, current_user, order_id, user_id, audit_status, after_sale_type, page, size
    )
    return format_response(data=result, message="获取成功")


@router.get("/aftersale/{id}", summary="查询售后订单详情")
def get_after_sale_detail(
    id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """查询售后订单详情"""
    # 临时模拟用户信息
    current_user = {"id": "U123456", "username": "test_user"}
    result = after_sale_service.get_after_sale_detail(db, id, current_user)
    return format_response(data=result, message="获取成功")


@router.post("/aftersale", summary="提交售后申请")
def create_after_sale(
    request: Request,
    after_sale_request: AfterSaleCreateRequest = Body(...),
    db: Session = Depends(get_db)
):
    """提交售后申请"""
    # 临时模拟用户信息
    current_user = {"id": "U123456", "username": "test_user"}
    result = after_sale_service.create_after_sale(db, current_user, after_sale_request)
    return format_response(data=result, message="售后申请提交成功")


@router.put("/aftersale/{id}", summary="审核售后订单")
def audit_after_sale(
    id: str,
    audit_request: AfterSaleAuditRequest = Body(...),
    db: Session = Depends(get_db)
):
    """审核售后订单（管理员操作）"""
    # 临时模拟用户信息
    current_user = {"id": "U123456", "username": "test_user", "roles": ["admin"]}
    result = after_sale_service.audit_after_sale(db, id, audit_request)
    return format_response(data=result, message="审核完成")
