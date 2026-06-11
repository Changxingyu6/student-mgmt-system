"""
数据分析 API 路由
提供用户统计、商品统计、订单统计和营销统计相关的 RESTful API 接口
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict
from database import get_db
from services import data_analysis_service as analysis_service
from utils import format_response

router = APIRouter(prefix="/data-analysis", tags=["数据分析"])


# ========== 用户统计相关 ==========

@router.get("/users/weekly", response_model=Dict)
def get_weekly_new_users(db: Session = Depends(get_db)):
    """获取当周新增用户数（最近7天）"""
    result = analysis_service.get_weekly_new_users(db)
    return format_response(data=result, message="获取当周新增用户数成功")


@router.get("/users/monthly", response_model=Dict)
def get_monthly_new_users(db: Session = Depends(get_db)):
    """获取当月新增用户数（最近30天）"""
    result = analysis_service.get_monthly_new_users(db)
    return format_response(data=result, message="获取当月新增用户数成功")


@router.get("/users/statistics", response_model=Dict)
def get_user_statistics(db: Session = Depends(get_db)):
    """获取用户综合统计数据（包含周统计和月统计）"""
    result = analysis_service.get_user_statistics(db)
    return format_response(data=result, message="获取用户综合统计数据成功")


@router.get("/users/level-statistics", response_model=Dict)
def get_user_level_statistics(db: Session = Depends(get_db)):
    """获取各用户等级的人数统计"""
    result = analysis_service.get_user_level_statistics(db)
    return format_response(data=result, message="获取用户等级统计成功")


# ========== 商品统计相关 ==========

@router.get("/goods/top-selling", response_model=Dict)
def get_top_selling_goods(limit: int = 20, db: Session = Depends(get_db)):
    """获取销量前N的商品（默认前20）"""
    result = analysis_service.get_top_selling_goods(db, limit)
    message = f"获取销量前{limit}商品成功，共{result['total_count']}件商品"
    return format_response(data=result, message=message)


@router.get("/goods/category-statistics", response_model=Dict)
def get_category_statistics(db: Session = Depends(get_db)):
    """获取各商品分类统计数据（在售商品数量、平均售价）"""
    result = analysis_service.get_category_statistics(db)
    message = f"获取商品分类统计成功，共{result['total_categories']}个分类，{result['total_goods']}件商品"
    return format_response(data=result, message=message)


@router.get("/goods/low-stock", response_model=Dict)
def get_low_stock_goods(db: Session = Depends(get_db)):
    """获取库存低于预警值的商品"""
    result = analysis_service.get_low_stock_goods(db)
    message = f"获取低库存商品成功，共{result['total_low_stock']}件商品，总缺货量{result['total_shortage']}"
    return format_response(data=result, message=message)


# ========== 订单统计相关 ==========

@router.get("/orders/statistics", response_model=Dict)
def get_order_statistics(period: str = 'day', db: Session = Depends(get_db)):
    """按日/周/月统计订单数据
    
    参数说明：
    - period: 统计周期，可选值：day（日）、week（周）、month（月），默认 day
    """
    result = analysis_service.get_order_statistics_by_period(db, period)
    message = f"按{result['period_type']}统计订单成功，共{result['total_orders']}笔订单，成交金额{result['total_amount']}元"
    return format_response(data=result, message=message)


@router.get("/orders/payment-statistics", response_model=Dict)
def get_payment_statistics(db: Session = Depends(get_db)):
    """统计各支付方式的订单数量与交易金额"""
    result = analysis_service.get_payment_method_statistics(db)
    message = f"获取支付方式统计成功，共{result['total_orders']}笔订单，总金额{result['total_amount']}元"
    return format_response(data=result, message=message)


@router.get("/orders/overdue-unpaid", response_model=Dict)
def get_overdue_unpaid_orders(timeout_hours: int = 24, db: Session = Depends(get_db)):
    """查询未付款超时订单
    
    参数说明：
    - timeout_hours: 超时时间（小时），默认24小时
    """
    result = analysis_service.get_overdue_unpaid_orders(db, timeout_hours)
    message = f"获取未付款超时订单成功，共{result['total_overdue']}笔，涉及金额{result['total_amount']}元"
    return format_response(data=result, message=message)


@router.get("/orders/long-time-unshipped", response_model=Dict)
def get_long_time_unshipped_orders(timeout_hours: int = 48, db: Session = Depends(get_db)):
    """查询长时间未发货订单
    
    参数说明：
    - timeout_hours: 超时时间（小时），默认48小时
    """
    result = analysis_service.get_long_time_unshipped_orders(db, timeout_hours)
    message = f"获取长时间未发货订单成功，共{result['total_unshipped']}笔，涉及金额{result['total_amount']}元"
    return format_response(data=result, message=message)


# ========== 营销数据统计相关 ==========

@router.get("/marketing/coupon-statistics", response_model=Dict)
def get_coupon_statistics(db: Session = Depends(get_db)):
    """统计各优惠券领取数量、使用数量、核销率"""
    result = analysis_service.get_coupon_statistics(db)
    message = f"获取优惠券统计成功，共{result['total_coupons']}种优惠券，发放{result['total_sent']}张，使用{result['total_used']}张，核销率{result['overall_use_rate']}%"
    return format_response(data=result, message=message)


@router.get("/marketing/activity-statistics", response_model=Dict)
def get_activity_statistics(db: Session = Depends(get_db)):
    """统计营销活动基本信息"""
    result = analysis_service.get_activity_statistics(db)
    message = f"获取营销活动统计成功，共{result['total_activities']}场活动，进行中{result['ongoing_count']}场，未开始{result['upcoming_count']}场，已结束{result['ended_count']}场"
    return format_response(data=result, message=message)