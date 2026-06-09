from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from database import get_db
from utils import format_response, require_roles
from schema.coupon_request import (
    CouponCreate, CouponUpdate, CouponQuery,
    UserCouponCreate, UserCouponUpdate, UserCouponQuery,
    CouponUseLogCreate, CouponUseLogUpdate, CouponUseLogQuery,
    ActivitiesCreate, ActivitiesUpdate, ActivitiesQuery,
    ActivityGoodsCreate, ActivityGoodsQuery,
    ActivityOrdersCreate, ActivityOrdersQuery
)
from services import coupon_service

router1 = APIRouter(prefix="/coupons", tags=["优惠券管理"])
router2 = APIRouter(prefix="/usercoupons",tags=['用户优惠券管理'])
router3 = APIRouter(prefix="/activities",tags=['营销活动管理'])
router4 = APIRouter(prefix="/activitiesgoods",tags=['营销商品管理'])
router5 = APIRouter(prefix="/activitiesorders",tags=['营销订单管理'])


# ==================== 优惠券 Coupon API ====================

@router1.post("")
@require_roles(["admin"])
def create_coupon(coupon: CouponCreate, db: Session = Depends(get_db)):
    data = coupon_service.create_coupon(db, coupon)
    return format_response(data=data, message="优惠券创建成功")


@router1.get("")
def get_coupons(
    coupons_no: Optional[str] = Query(None),
    coupons_name: Optional[str] = Query(None),
    type: Optional[int] = Query(None),
    status: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * page_size
    data = coupon_service.get_coupons(db, coupons_no, coupons_name, type, status, skip, page_size)
    return format_response(data=data)


@router1.get("/{coupon_id}")
def get_coupon(coupon_id: str, db: Session = Depends(get_db)):
    data = coupon_service.get_coupon(db, coupon_id)
    if not data:
        return format_response(code=404, message="优惠券不存在")
    return format_response(data=data)


@router1.put("/{coupon_id}")
@require_roles(["admin"])
def update_coupon(coupon_id: str, coupon_update: CouponUpdate, db: Session = Depends(get_db)):
    data = coupon_service.update_coupon(db, coupon_id, coupon_update)
    if not data:
        return format_response(code=404, message="优惠券不存在")
    return format_response(data=data, message="优惠券更新成功")


@router1.delete("/{coupon_id}")
@require_roles(["admin"])
def delete_coupon(coupon_id: str, db: Session = Depends(get_db)):
    success = coupon_service.delete_coupon(db, coupon_id)
    if not success:
        return format_response(code=404, message="优惠券不存在")
    return format_response(message="优惠券已下架")


# ==================== 用户优惠券 UserCoupon API ====================

@router2.post("/user-coupons")
def create_user_coupon(uc: UserCouponCreate, db: Session = Depends(get_db)):
    data = coupon_service.create_user_coupon(db, uc)
    return format_response(data=data, message="用户优惠券创建成功")


@router2.get("/user-coupons")
def get_user_coupons(
    user_id: Optional[str] = Query(None),
    coupon_id: Optional[str] = Query(None),
    status: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * page_size
    data = coupon_service.get_user_coupons(db, user_id, coupon_id, status, skip, page_size)
    return format_response(data=data)


@router2.get("/user-coupons/{uc_id}")
def get_user_coupon(uc_id: str, db: Session = Depends(get_db)):
    data = coupon_service.get_user_coupon(db, uc_id)
    if not data:
        return format_response(code=404, message="用户优惠券不存在")
    return format_response(data=data)


@router2.put("/user-coupons/{uc_id}")
def update_user_coupon(uc_id: str, uc_update: UserCouponUpdate, db: Session = Depends(get_db)):
    data = coupon_service.update_user_coupon(db, uc_id, uc_update)
    if not data:
        return format_response(code=404, message="用户优惠券不存在")
    return format_response(data=data, message="用户优惠券更新成功")


@router2.delete("/user-coupons/{uc_id}")
def delete_user_coupon(uc_id: str, db: Session = Depends(get_db)):
    success = coupon_service.delete_user_coupon(db, uc_id)
    if not success:
        return format_response(code=404, message="用户优惠券不存在")
    return format_response(message="用户优惠券已删除")


# ==================== 优惠券使用日志 CouponUseLog API ====================

@router1.post("/use-logs")
def create_use_log(log: CouponUseLogCreate, db: Session = Depends(get_db)):
    data = coupon_service.create_use_log(db, log)
    return format_response(data=data, message="使用日志创建成功")


@router1.get("/use-logs")
def get_use_logs(
    user_id: Optional[str] = Query(None),
    user_coupon_id: Optional[str] = Query(None),
    status: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * page_size
    data = coupon_service.get_use_logs(db, user_id, user_coupon_id, status, skip, page_size)
    return format_response(data=data)


@router1.get("/use-logs/{log_id}")
def get_use_log(log_id: str, db: Session = Depends(get_db)):
    data = coupon_service.get_use_log(db, log_id)
    if not data:
        return format_response(code=404, message="使用日志不存在")
    return format_response(data=data)


@router1.put("/use-logs/{log_id}")
def update_use_log(log_id: str, log_update: CouponUseLogUpdate, db: Session = Depends(get_db)):
    data = coupon_service.update_use_log(db, log_id, log_update)
    if not data:
        return format_response(code=404, message="使用日志不存在")
    return format_response(data=data, message="使用日志更新成功")


@router1.delete("/use-logs/{log_id}")
def delete_use_log(log_id: str, db: Session = Depends(get_db)):
    success = coupon_service.delete_use_log(db, log_id)
    if not success:
        return format_response(code=404, message="使用日志不存在")
    return format_response(message="使用日志已删除")


# ==================== 营销活动 Activities API ====================

@router3.post("/activities")
@require_roles(["admin"])
def create_activity(activity: ActivitiesCreate, db: Session = Depends(get_db)):
    data = coupon_service.create_activity(db, activity)
    return format_response(data=data, message="营销活动创建成功")


@router3.get("/activities")
def get_activities(
    activities_name: Optional[str] = Query(None),
    activities_type: Optional[str] = Query(None),
    status: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * page_size
    data = coupon_service.get_activities(db, activities_name, activities_type, status, skip, page_size)
    return format_response(data=data)


@router3.get("/activities/{activity_id}")
def get_activity(activity_id: str, db: Session = Depends(get_db)):
    data = coupon_service.get_activity(db, activity_id)
    if not data:
        return format_response(code=404, message="营销活动不存在")
    return format_response(data=data)


@router3.put("/activities/{activity_id}")
@require_roles(["admin"])
def update_activity(activity_id: str, activity_update: ActivitiesUpdate, db: Session = Depends(get_db)):
    data = coupon_service.update_activity(db, activity_id, activity_update)
    if not data:
        return format_response(code=404, message="营销活动不存在")
    return format_response(data=data, message="营销活动更新成功")


@router3.delete("/activities/{activity_id}")
@require_roles(["admin"])
def delete_activity(activity_id: str, db: Session = Depends(get_db)):
    success = coupon_service.delete_activity(db, activity_id)
    if not success:
        return format_response(code=404, message="营销活动不存在")
    return format_response(message="营销活动已删除")


# ==================== 活动商品关联 Activity Goods API ====================

@router4.post("/activities/{activities_id}/goods")
@require_roles(["admin"])
def add_activity_goods(activities_id: str, product_id: str, db: Session = Depends(get_db)):
    coupon_service.create_activity_goods(db, activities_id, product_id)
    return format_response(message="活动商品关联成功")


@router4.get("/activities/{activities_id}/goods")
def get_activity_goods(
    activities_id: str,
    product_id: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * page_size
    data = coupon_service.get_activity_goods_list(db, activities_id, product_id, skip, page_size)
    return format_response(data=data)


@router4.delete("/activities/{activities_id}/goods")
@require_roles(["admin"])
def remove_activity_goods(
    activities_id: str,
    product_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    coupon_service.delete_activity_goods(db, activities_id, product_id)
    return format_response(message="活动商品关联已删除")


# ==================== 活动订单关联 Activity Orders API ====================

@router5.post("/activities/{activities_id}/orders")
@require_roles(["admin"])
def add_activity_orders(activities_id: str, orders_id: str, db: Session = Depends(get_db)):
    coupon_service.create_activity_orders(db, activities_id, orders_id)
    return format_response(message="活动订单关联成功")


@router5.get("/activities/{activities_id}/orders")
def get_activity_orders(
    activities_id: str,
    orders_id: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * page_size
    data = coupon_service.get_activity_orders_list(db, activities_id, orders_id, skip, page_size)
    return format_response(data=data)


@router5.delete("/activities/{activities_id}/orders")
@require_roles(["admin"])
def remove_activity_orders(
    activities_id: str,
    orders_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    coupon_service.delete_activity_orders(db, activities_id, orders_id)
    return format_response(message="活动订单关联已删除")
