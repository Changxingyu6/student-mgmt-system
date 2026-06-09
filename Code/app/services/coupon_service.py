from sqlalchemy.orm import Session
from uuid import uuid4
from typing import Optional
from schema.coupon_request import (
    CouponCreate, CouponUpdate, UserCouponCreate, UserCouponUpdate,
    CouponUseLogCreate, CouponUseLogUpdate, ActivitiesCreate, ActivitiesUpdate
)
from dao import coupon_dao


def generate_id() -> str:
    return str(uuid4())


# ==================== Coupon Service ====================

def get_coupon(db: Session, coupon_id: str):
    return coupon_dao.get_coupon_by_id(db, coupon_id)


def get_coupons(
    db: Session,
    coupons_no: Optional[str] = None,
    coupons_name: Optional[str] = None,
    type: Optional[int] = None,
    status: Optional[int] = None,
    skip: int = 0,
    limit: int = 20
) -> dict:
    filters = {
        "coupons_no": coupons_no,
        "coupons_name": coupons_name,
        "type": type,
        "status": status
    }
    items, total = coupon_dao.get_coupon_list(db, filters, skip, limit)
    return {"total": total, "items": items}


def create_coupon(db: Session, coupon: CouponCreate):
    return coupon_dao.create_coupon(db, coupon.model_dump())


def update_coupon(db: Session, coupon_id: str, coupon_update: CouponUpdate):
    update_data = coupon_update.model_dump(exclude_unset=True)
    return coupon_dao.update_coupon(db, coupon_id, update_data)


def delete_coupon(db: Session, coupon_id: str) -> bool:
    return coupon_dao.delete_coupon(db, coupon_id)


# ==================== UserCoupon Service ====================

def get_user_coupon(db: Session, uc_id: str):
    return coupon_dao.get_user_coupon_by_id(db, uc_id)


def get_user_coupons(
    db: Session,
    user_id: Optional[str] = None,
    coupon_id: Optional[str] = None,
    status: Optional[int] = None,
    skip: int = 0,
    limit: int = 20
) -> dict:
    filters = {"user_id": user_id, "coupon_id": coupon_id, "status": status}
    items, total = coupon_dao.get_user_coupon_list(db, filters, skip, limit)
    return {"total": total, "items": items}


def create_user_coupon(db: Session, uc: UserCouponCreate):
    return coupon_dao.create_user_coupon(db, uc.model_dump())


def update_user_coupon(db: Session, uc_id: str, uc_update: UserCouponUpdate):
    update_data = uc_update.model_dump(exclude_unset=True)
    return coupon_dao.update_user_coupon(db, uc_id, update_data)


def delete_user_coupon(db: Session, uc_id: str) -> bool:
    return coupon_dao.delete_user_coupon(db, uc_id)


# ==================== CouponUseLog Service ====================

def get_use_log(db: Session, log_id: str):
    return coupon_dao.get_use_log_by_id(db, log_id)


def get_use_logs(
    db: Session,
    user_id: Optional[str] = None,
    user_coupon_id: Optional[str] = None,
    status: Optional[int] = None,
    skip: int = 0,
    limit: int = 20
) -> dict:
    filters = {"user_id": user_id, "user_coupon_id": user_coupon_id, "status": status}
    items, total = coupon_dao.get_use_log_list(db, filters, skip, limit)
    return {"total": total, "items": items}


def create_use_log(db: Session, log: CouponUseLogCreate):
    return coupon_dao.create_use_log(db, log.model_dump())


def update_use_log(db: Session, log_id: str, log_update: CouponUseLogUpdate):
    update_data = log_update.model_dump(exclude_unset=True)
    return coupon_dao.update_use_log(db, log_id, update_data)


def delete_use_log(db: Session, log_id: str) -> bool:
    return coupon_dao.delete_use_log(db, log_id)


# ==================== Activities Service ====================

def get_activity(db: Session, activity_id: str):
    return coupon_dao.get_activity_by_id(db, activity_id)


def get_activities(
    db: Session,
    activities_name: Optional[str] = None,
    activities_type: Optional[str] = None,
    status: Optional[int] = None,
    skip: int = 0,
    limit: int = 20
) -> dict:
    filters = {
        "activities_name": activities_name,
        "activities_type": activities_type,
        "status": status
    }
    items, total = coupon_dao.get_activity_list(db, filters, skip, limit)
    return {"total": total, "items": items}


def create_activity(db: Session, activity: ActivitiesCreate):
    activity_data = activity.model_dump(exclude={"goods_ids", "order_ids"})
    db_activity = coupon_dao.create_activity(db, activity_data)

    if activity.goods_ids:
        for gid in set(activity.goods_ids):
            coupon_dao.create_activity_goods(db, db_activity.id, gid)

    if activity.order_ids:
        for oid in set(activity.order_ids):
            coupon_dao.create_activity_orders(db, db_activity.id, oid)

    return db_activity


def update_activity(db: Session, activity_id: str, activity_update: ActivitiesUpdate):
    update_data = activity_update.model_dump(exclude_unset=True, exclude={"goods_ids", "order_ids"})
    db_activity = coupon_dao.update_activity(db, activity_id, update_data)
    if not db_activity:
        return None

    if activity_update.goods_ids is not None:
        coupon_dao.soft_delete_activity_goods(db, activity_id)
        for gid in set(activity_update.goods_ids):
            coupon_dao.create_activity_goods(db, activity_id, gid)

    if activity_update.order_ids is not None:
        coupon_dao.soft_delete_activity_orders(db, activity_id)
        for oid in set(activity_update.order_ids):
            coupon_dao.create_activity_orders(db, activity_id, oid)

    return db_activity


def delete_activity(db: Session, activity_id: str) -> bool:
    success = coupon_dao.delete_activity(db, activity_id)
    if success:
        coupon_dao.soft_delete_activity_goods(db, activity_id)
        coupon_dao.soft_delete_activity_orders(db, activity_id)
    return success


# ==================== Activity Goods Service ====================

def get_activity_goods_list(
    db: Session,
    activities_id: Optional[str] = None,
    product_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 20
) -> dict:
    total, items = coupon_dao.get_activity_goods_list(db, activities_id, product_id, skip, limit)
    return {"total": total, "items": [dict(row._mapping) for row in items]}


def create_activity_goods(db: Session, activities_id: str, product_id: str):
    return coupon_dao.create_activity_goods(db, activities_id, product_id)


def delete_activity_goods(db: Session, activities_id: str, product_id: Optional[str] = None) -> bool:
    coupon_dao.soft_delete_activity_goods(db, activities_id, product_id)
    return True


# ==================== Activity Orders Service ====================

def get_activity_orders_list(
    db: Session,
    activities_id: Optional[str] = None,
    orders_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 20
) -> dict:
    total, items = coupon_dao.get_activity_orders_list(db, activities_id, orders_id, skip, limit)
    return {"total": total, "items": [dict(row._mapping) for row in items]}


def create_activity_orders(db: Session, activities_id: str, orders_id: str):
    return coupon_dao.create_activity_orders(db, activities_id, orders_id)


def delete_activity_orders(db: Session, activities_id: str, orders_id: Optional[str] = None) -> bool:
    coupon_dao.soft_delete_activity_orders(db, activities_id, orders_id)
    return True
