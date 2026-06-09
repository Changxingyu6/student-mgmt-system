from sqlalchemy.orm import Session
from uuid import uuid4
from typing import Optional
from schema.coupon_request import (
    CouponCreate, CouponUpdate, UserCouponCreate, UserCouponUpdate,
    ActivitiesCreate, ActivitiesUpdate
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
    result = coupon_dao.create_coupon(db, coupon.model_dump())
    db.commit()
    db.refresh(result)
    return result


def update_coupon(db: Session, coupon_id: str, coupon_update: CouponUpdate):
    update_data = coupon_update.model_dump(exclude_unset=True)
    result = coupon_dao.update_coupon(db, coupon_id, update_data)
    if result:
        db.commit()
        db.refresh(result)
    return result


def delete_coupon(db: Session, coupon_id: str) -> bool:
    success = coupon_dao.delete_coupon(db, coupon_id)
    if success:
        db.commit()
    return success


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
    result = coupon_dao.create_user_coupon(db, uc.model_dump())
    db.commit()
    db.refresh(result)
    return result


def receive_coupon(db: Session, coupon_id: str, user_id: str):
    """
    用户领取优惠券（每个用户每种优惠券只能领取一张）
    """
    from datetime import datetime
    
    coupon = coupon_dao.get_coupon_by_id(db, coupon_id)
    if not coupon:
        return None, "优惠券不存在"
    
    if coupon.status != 1:
        return None, "优惠券已下架或已过期"
    
    if coupon.sent_count >= coupon.total_count:
        return None, "优惠券已领完"
    
    existing = coupon_dao.get_user_coupon_by_user_and_coupon(db, user_id, coupon_id)
    if existing:
        return None, "您已领取过该优惠券"
    
    user_coupon_data = {
        "id": generate_id(),
        "coupon_id": coupon_id,
        "user_id": user_id,
        "coupon_no": f"UCP{datetime.now().strftime('%Y%m%d%H%M%S')}{generate_id()[:8]}",
        "status": 1,
        "get_time": datetime.now(),
        "valid_end_time": coupon.valid_end_time
    }
    
    user_coupon = coupon_dao.create_user_coupon(db, user_coupon_data)
    coupon_dao.increment_coupon_sent_count(db, coupon_id)
    db.commit()
    db.refresh(user_coupon)
    
    return user_coupon, None


def update_user_coupon(db: Session, uc_id: str, uc_update: UserCouponUpdate):
    update_data = uc_update.model_dump(exclude_unset=True)
    result = coupon_dao.update_user_coupon(db, uc_id, update_data)
    if result:
        db.commit()
        db.refresh(result)
    return result


def delete_user_coupon(db: Session, uc_id: str) -> bool:
    success = coupon_dao.delete_user_coupon(db, uc_id)
    if success:
        db.commit()
    return success


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
    activity_data = activity.model_dump(exclude={"goods_ids"})
    db_activity = coupon_dao.create_activity(db, activity_data)

    if activity.goods_ids:
        for gid in set(activity.goods_ids):
            coupon_dao.create_activity_goods(db, db_activity.id, gid)

    db.commit()
    db.refresh(db_activity)
    return db_activity


def update_activity(db: Session, activity_id: str, activity_update: ActivitiesUpdate):
    update_data = activity_update.model_dump(exclude_unset=True, exclude={"goods_ids"})
    db_activity = coupon_dao.update_activity(db, activity_id, update_data)
    if not db_activity:
        return None

    if activity_update.goods_ids is not None:
        coupon_dao.soft_delete_activity_goods(db, activity_id)
        for gid in set(activity_update.goods_ids):
            coupon_dao.create_activity_goods(db, activity_id, gid)

    db.commit()
    db.refresh(db_activity)
    return db_activity


def delete_activity(db: Session, activity_id: str) -> bool:
    success = coupon_dao.delete_activity(db, activity_id)
    if success:
        coupon_dao.soft_delete_activity_goods(db, activity_id)
        db.commit()
    return success


# ==================== Activity Goods Service ====================

def get_activity_goods_list(
    db: Session,
    activities_id: Optional[str] = None,
    goods_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 20
) -> dict:
    total, items = coupon_dao.get_activity_goods_list(db, activities_id, goods_id, skip, limit)
    return {"total": total, "items": [dict(row._mapping) for row in items]}


def create_activity_goods(db: Session, activities_id: str, goods_id: str):
    result = coupon_dao.create_activity_goods(db, activities_id, goods_id)
    db.commit()
    return result


def delete_activity_goods(db: Session, activities_id: str, goods_id: Optional[str] = None) -> bool:
    coupon_dao.soft_delete_activity_goods(db, activities_id, goods_id)
    db.commit()
    return True