from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List, Tuple
from uuid import uuid4
from model.coupon import Coupon, UserCoupon, Activities, activities_goods


def generate_id() -> str:
    return str(uuid4())


# ==================== Coupon DAO ====================

def get_coupon_by_id(db: Session, coupon_id: str) -> Optional[Coupon]:
    return db.query(Coupon).filter(Coupon.id == coupon_id, Coupon.is_deleted == 0).first()


def get_coupon_by_no(db: Session, coupon_no: str) -> Optional[Coupon]:
    return db.query(Coupon).filter(Coupon.coupons_no == coupon_no, Coupon.is_deleted == 0).first()


def get_coupon_list(
    db: Session,
    filters: Dict[str, Any],
    skip: int = 0,
    limit: int = 20
) -> Tuple[List[Coupon], int]:
    query = db.query(Coupon).filter(Coupon.is_deleted == 0)
    if filters.get('coupons_no'):
        query = query.filter(Coupon.coupons_no == filters['coupons_no'])
    if filters.get('coupons_name'):
        query = query.filter(Coupon.coupons_name.like(f"%{filters['coupons_name']}%"))
    if filters.get('type') is not None:
        query = query.filter(Coupon.type == filters['type'])
    if filters.get('status') is not None:
        query = query.filter(Coupon.status == filters['status'])
    total = query.count()
    items = query.order_by(Coupon.valid_start_time.desc()).offset(skip).limit(limit).all()
    return items, total


def create_coupon(db: Session, data: Dict[str, Any]) -> Coupon:
    coupon = Coupon(id=generate_id(), **data)
    db.add(coupon)
    return coupon


def update_coupon(db: Session, coupon_id: str, update_data: Dict[str, Any]) -> Optional[Coupon]:
    coupon = get_coupon_by_id(db, coupon_id)
    if not coupon:
        return None
    for field, value in update_data.items():
        if field not in ('id', 'is_deleted'):
            setattr(coupon, field, value)
    return coupon


def delete_coupon(db: Session, coupon_id: str) -> bool:
    coupon = get_coupon_by_id(db, coupon_id)
    if not coupon:
        return False
    coupon.is_deleted = 1
    return True


# ==================== UserCoupon DAO ====================

def get_user_coupon_by_id(db: Session, uc_id: str) -> Optional[UserCoupon]:
    return db.query(UserCoupon).filter(UserCoupon.id == uc_id, UserCoupon.is_deleted == 0).first()


def get_user_coupon_list(
    db: Session,
    filters: Dict[str, Any],
    skip: int = 0,
    limit: int = 20
) -> Tuple[List[UserCoupon], int]:
    query = db.query(UserCoupon).filter(UserCoupon.is_deleted == 0)
    if filters.get('user_id'):
        query = query.filter(UserCoupon.user_id == filters['user_id'])
    if filters.get('coupon_id'):
        query = query.filter(UserCoupon.coupon_id == filters['coupon_id'])
    if filters.get('status') is not None:
        query = query.filter(UserCoupon.status == filters['status'])
    total = query.count()
    items = query.order_by(UserCoupon.get_time.desc()).offset(skip).limit(limit).all()
    return items, total


def create_user_coupon(db: Session, data: Dict[str, Any]) -> UserCoupon:
    if 'id' not in data or not data['id']:
        data['id'] = generate_id()
    uc = UserCoupon(**data)
    db.add(uc)
    return uc


def update_user_coupon(db: Session, uc_id: str, update_data: Dict[str, Any]) -> Optional[UserCoupon]:
    uc = get_user_coupon_by_id(db, uc_id)
    if not uc:
        return None
    for field, value in update_data.items():
        if field not in ('id', 'is_deleted'):
            setattr(uc, field, value)
    return uc


def delete_user_coupon(db: Session, uc_id: str) -> bool:
    uc = get_user_coupon_by_id(db, uc_id)
    if not uc:
        return False
    uc.is_deleted = 1
    return True


def get_user_coupon_by_user_and_coupon(db: Session, user_id: str, coupon_id: str) -> Optional[UserCoupon]:
    return db.query(UserCoupon).filter(
        UserCoupon.user_id == user_id,
        UserCoupon.coupon_id == coupon_id,
        UserCoupon.is_deleted == 0
    ).first()


def increment_coupon_sent_count(db: Session, coupon_id: str):
    coupon = get_coupon_by_id(db, coupon_id)
    if coupon:
        coupon.sent_count += 1


# ==================== Activities DAO ====================

def get_activity_by_id(db: Session, activity_id: str) -> Optional[Activities]:
    return db.query(Activities).filter(Activities.id == activity_id, Activities.is_deleted == 0).first()


def get_activity_list(
    db: Session,
    filters: Dict[str, Any],
    skip: int = 0,
    limit: int = 20
) -> Tuple[List[Activities], int]:
    query = db.query(Activities).filter(Activities.is_deleted == 0)
    if filters.get('activities_name'):
        query = query.filter(Activities.activities_name.like(f"%{filters['activities_name']}%"))
    if filters.get('activities_type'):
        query = query.filter(Activities.activities_type == filters['activities_type'])
    if filters.get('status') is not None:
        query = query.filter(Activities.status == filters['status'])
    total = query.count()
    items = query.order_by(Activities.start_time.desc()).offset(skip).limit(limit).all()
    return items, total


def create_activity(db: Session, data: Dict[str, Any]) -> Activities:
    activity = Activities(id=generate_id(), **data)
    db.add(activity)
    return activity


def update_activity(db: Session, activity_id: str, update_data: Dict[str, Any]) -> Optional[Activities]:
    activity = get_activity_by_id(db, activity_id)
    if not activity:
        return None
    for field, value in update_data.items():
        if field not in ('id', 'is_deleted'):
            setattr(activity, field, value)
    return activity


def delete_activity(db: Session, activity_id: str) -> bool:
    activity = get_activity_by_id(db, activity_id)
    if not activity:
        return False
    activity.is_deleted = 1
    return True


# ==================== Activity Goods Relation DAO ====================

def create_activity_goods(db: Session, activity_id: str, goods_id: str):
    stmt = activities_goods.insert().values(activities_id=activity_id, goods_id=goods_id, is_deleted=0)
    db.execute(stmt)


def soft_delete_activity_goods(db: Session, activity_id: str, goods_id: Optional[str] = None):
    stmt = activities_goods.update().where(activities_goods.c.activities_id == activity_id)
    if goods_id:
        stmt = stmt.where(activities_goods.c.goods_id == goods_id)
    stmt = stmt.values(is_deleted=1)
    db.execute(stmt)


def get_activity_goods_list(
    db: Session,
    activity_id: Optional[str] = None,
    goods_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 20
) -> Tuple[int, List[Any]]:
    query = db.query(activities_goods).filter(activities_goods.c.is_deleted == 0)
    if activity_id:
        query = query.filter(activities_goods.c.activities_id == activity_id)
    if goods_id:
        query = query.filter(activities_goods.c.goods_id == goods_id)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return total, items