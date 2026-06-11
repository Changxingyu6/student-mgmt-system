"""
数据分析数据访问层
提供用户统计、商品统计、订单统计和营销统计相关的数据库操作
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from model.user import User
from model.goods_model import Goods, GoodsCategory, GoodsStock
from model.order_item import OrderItem
from model.coupon import Coupon, UserCoupon, Activities


# ========== 用户统计相关 ==========

def count_new_users_by_date_range(db: Session, start_time: datetime, end_time: datetime) -> int:
    """根据日期范围统计新增用户数量"""
    return db.query(func.count(User.id)).filter(
        User.create_time >= start_time,
        User.create_time <= end_time,
        User.is_deleted == False
    ).scalar() or 0


def count_weekly_new_users(db: Session) -> int:
    """统计当周新增用户（最近7天）"""
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)
    return count_new_users_by_date_range(db, start_time, end_time)


def count_monthly_new_users(db: Session) -> int:
    """统计当月新增用户（最近30天）"""
    end_time = datetime.now()
    start_time = end_time - timedelta(days=30)
    return count_new_users_by_date_range(db, start_time, end_time)


def count_users_by_level(db: Session) -> list:
    """统计各用户等级的人数"""
    result = db.query(
        User.user_level,
        func.count(User.id).label('count')
    ).filter(
        User.is_deleted == False
    ).group_by(User.user_level).all()
    
    return [{"level": row.user_level, "count": row.count} for row in result]


# ========== 商品统计相关 ==========

def get_top_selling_goods(db: Session, limit: int = 20) -> list:
    """查询销量前N的商品"""
    from sqlalchemy import text
    
    sql = """
    SELECT g.id AS goods_id, g.goods_name, 
           SUM(oi.quantity) AS sales_volume, 
           SUM(oi.quantity * g.price) AS sales_amount, 
           gc.category_name
    FROM goods g
    INNER JOIN order_items oi ON g.id COLLATE utf8mb4_unicode_ci = oi.product_id COLLATE utf8mb4_unicode_ci
    INNER JOIN goods_category gc ON g.category_id COLLATE utf8mb4_unicode_ci = gc.id COLLATE utf8mb4_unicode_ci
    WHERE g.sale_status = 1
    GROUP BY g.id, g.goods_name, gc.category_name
    ORDER BY SUM(oi.quantity) DESC
    LIMIT :limit
    """
    
    result = db.execute(text(sql), {"limit": limit}).fetchall()
    
    return [{
        "goods_id": row.goods_id,
        "goods_name": row.goods_name,
        "sales_volume": int(row.sales_volume) if row.sales_volume else 0,
        "sales_amount": float(row.sales_amount) if row.sales_amount else 0,
        "category_name": row.category_name
    } for row in result]


def get_category_statistics(db: Session) -> list:
    """统计各商品分类的在售商品数量、平均售价"""
    from sqlalchemy import text
    
    sql = """
    SELECT gc.id AS category_id, gc.category_name,
           COUNT(g.id) AS goods_count,
           AVG(g.price) AS avg_price
    FROM goods_category gc
    INNER JOIN goods g ON gc.id COLLATE utf8mb4_unicode_ci = g.category_id COLLATE utf8mb4_unicode_ci
    WHERE g.sale_status = 1
    GROUP BY gc.id, gc.category_name
    """
    
    result = db.execute(text(sql)).fetchall()
    
    return [{
        "category_id": row.category_id,
        "category_name": row.category_name,
        "goods_count": int(row.goods_count) if row.goods_count else 0,
        "avg_price": round(float(row.avg_price), 2) if row.avg_price else 0
    } for row in result]


def get_low_stock_goods(db: Session) -> list:
    """查询库存低于预警值的所有商品"""
    from sqlalchemy import text
    
    sql = """
    SELECT g.id AS goods_id, g.goods_name, g.price,
           g.stock_warning, gs.stock_num, gc.category_name
    FROM goods g
    INNER JOIN goods_stock gs ON g.id COLLATE utf8mb4_unicode_ci = gs.goods_id COLLATE utf8mb4_unicode_ci
    INNER JOIN goods_category gc ON g.category_id COLLATE utf8mb4_unicode_ci = gc.id COLLATE utf8mb4_unicode_ci
    WHERE g.sale_status = 1 AND gs.stock_num < g.stock_warning
    """
    
    result = db.execute(text(sql)).fetchall()
    
    return [{
        "goods_id": row.goods_id,
        "goods_name": row.goods_name,
        "price": float(row.price) if row.price else 0,
        "stock_warning": int(row.stock_warning) if row.stock_warning else 0,
        "current_stock": int(row.stock_num) if row.stock_num else 0,
        "category_name": row.category_name,
        "stock_shortage": int(row.stock_warning) - int(row.stock_num) if row.stock_warning and row.stock_num else 0
    } for row in result]


# ========== 订单统计相关 ==========

def get_order_statistics_by_period(db: Session, period: str = 'day') -> list:
    """按日/周/月统计订单数据"""
    from sqlalchemy import text
    
    if period == 'day':
        date_format = "%Y-%m-%d"
        date_trunc = "DATE(o.create_time)"
    elif period == 'week':
        date_format = "%Y-%u"
        date_trunc = "YEAR(o.create_time) * 100 + WEEK(o.create_time)"
    elif period == 'month':
        date_format = "%Y-%m"
        date_trunc = "YEAR(o.create_time) * 100 + MONTH(o.create_time)"
    else:
        date_format = "%Y-%m-%d"
        date_trunc = "DATE(o.create_time)"
    
    sql = f"""
    SELECT 
        {date_trunc} AS period,
        COUNT(o.id) AS total_orders,
        SUM(CASE WHEN o.pay_status = 'paid' THEN 1 ELSE 0 END) AS paid_orders,
        SUM(CASE WHEN o.order_status = 'refund' THEN 1 ELSE 0 END) AS refund_orders,
        SUM(CASE WHEN o.pay_status = 'paid' THEN o.actual_pay_amount ELSE 0 END) AS total_amount
    FROM orders o
    WHERE o.is_deleted = 0
    GROUP BY {date_trunc}
    ORDER BY {date_trunc} DESC
    LIMIT 30
    """
    
    result = db.execute(text(sql)).fetchall()
    
    statistics = []
    for row in result:
        total = row.total_orders if row.total_orders else 0
        refund = row.refund_orders if row.refund_orders else 0
        refund_ratio = round(refund / total * 100, 2) if total > 0 else 0
        
        statistics.append({
            "period": str(row.period),
            "total_orders": int(total),
            "paid_orders": int(row.paid_orders) if row.paid_orders else 0,
            "refund_orders": int(refund),
            "refund_ratio": refund_ratio,
            "total_amount": round(float(row.total_amount), 2) if row.total_amount else 0
        })
    
    return statistics


def get_payment_method_statistics(db: Session) -> list:
    """统计各支付方式的订单数量与交易金额"""
    from sqlalchemy import text
    
    sql = """
    SELECT 
        o.payment_method,
        COUNT(o.id) AS order_count,
        SUM(o.actual_pay_amount) AS total_amount
    FROM orders o
    WHERE o.is_deleted = 0 AND o.pay_status = 'paid'
    GROUP BY o.payment_method
    ORDER BY total_amount DESC
    """
    
    result = db.execute(text(sql)).fetchall()
    
    return [{
        "payment_method": row.payment_method,
        "order_count": int(row.order_count) if row.order_count else 0,
        "total_amount": round(float(row.total_amount), 2) if row.total_amount else 0
    } for row in result]


def get_overdue_unpaid_orders(db: Session, timeout_hours: int = 24) -> list:
    """查询未付款超时订单"""
    from sqlalchemy import text
    
    sql = f"""
    SELECT 
        o.order_id,
        o.user_id,
        o.total_amount,
        o.actual_pay_amount,
        o.create_time,
        o.expire_time,
        TIMESTAMPDIFF(MINUTE, o.create_time, NOW()) AS overdue_minutes
    FROM orders o
    WHERE o.is_deleted = 0 
      AND o.pay_status = 'unpaid' 
      AND o.expire_time < NOW()
    ORDER BY overdue_minutes DESC
    """
    
    result = db.execute(text(sql)).fetchall()
    
    return [{
        "order_id": row.order_id,
        "user_id": row.user_id,
        "total_amount": round(float(row.total_amount), 2) if row.total_amount else 0,
        "actual_pay_amount": round(float(row.actual_pay_amount), 2) if row.actual_pay_amount else 0,
        "create_time": row.create_time.strftime("%Y-%m-%d %H:%M:%S") if row.create_time else None,
        "expire_time": row.expire_time.strftime("%Y-%m-%d %H:%M:%S") if row.expire_time else None,
        "overdue_minutes": int(row.overdue_minutes) if row.overdue_minutes else 0
    } for row in result]


def get_long_time_unshipped_orders(db: Session, timeout_hours: int = 48) -> list:
    """查询长时间未发货订单"""
    from sqlalchemy import text
    
    sql = f"""
    SELECT 
        o.order_id,
        o.user_id,
        o.total_amount,
        o.pay_time,
        TIMESTAMPDIFF(HOUR, o.pay_time, NOW()) AS wait_hours,
        o.receiver_name,
        o.receiver_phone
    FROM orders o
    WHERE o.is_deleted = 0 
      AND o.pay_status = 'paid' 
      AND o.logistics_status = 'waiting_ship'
      AND o.pay_time IS NOT NULL
      AND TIMESTAMPDIFF(HOUR, o.pay_time, NOW()) >= {timeout_hours}
    ORDER BY wait_hours DESC
    """
    
    result = db.execute(text(sql)).fetchall()
    
    return [{
        "order_id": row.order_id,
        "user_id": row.user_id,
        "total_amount": round(float(row.total_amount), 2) if row.total_amount else 0,
        "pay_time": row.pay_time.strftime("%Y-%m-%d %H:%M:%S") if row.pay_time else None,
        "wait_hours": int(row.wait_hours) if row.wait_hours else 0,
        "receiver_name": row.receiver_name,
        "receiver_phone": row.receiver_phone
    } for row in result]


# ========== 营销数据统计相关 ==========

def get_coupon_statistics(db: Session) -> list:
    """统计各优惠券领取数量、使用数量、核销率"""
    result = db.query(
        Coupon.id,
        Coupon.coupons_no,
        Coupon.coupons_name,
        Coupon.type,
        Coupon.face_value,
        Coupon.min_spend,
        Coupon.total_count,
        Coupon.sent_count,
        Coupon.used_count
    ).filter(Coupon.is_deleted == 0).all()
    
    statistics = []
    for row in result:
        sent_count = row.sent_count if row.sent_count else 0
        used_count = row.used_count if row.used_count else 0
        use_rate = round(used_count / sent_count * 100, 2) if sent_count > 0 else 0
        
        statistics.append({
            "coupon_id": row.id,
            "coupon_no": row.coupons_no,
            "coupon_name": row.coupons_name,
            "type": row.type,
            "type_name": "满减" if row.type == 1 else "折扣" if row.type == 2 else "无门槛",
            "face_value": round(float(row.face_value), 2) if row.face_value else 0,
            "min_spend": round(float(row.min_spend), 2) if row.min_spend else 0,
            "total_count": int(row.total_count) if row.total_count else 0,
            "sent_count": sent_count,
            "used_count": used_count,
            "use_rate": use_rate,
            "remaining_count": int(row.total_count) - sent_count if row.total_count else 0
        })
    
    return statistics


def get_activity_statistics(db: Session) -> list:
    """统计每场营销活动基本信息"""
    result = db.query(
        Activities.id,
        Activities.activities_name,
        Activities.activities_type,
        Activities.face_value,
        Activities.min_spend,
        Activities.start_time,
        Activities.end_time,
        Activities.status
    ).filter(Activities.is_deleted == 0).all()
    
    statistics = []
    for row in result:
        now = datetime.now()
        if row.start_time and row.end_time:
            if row.start_time <= now <= row.end_time:
                status = "进行中"
            elif now < row.start_time:
                status = "未开始"
            else:
                status = "已结束"
        else:
            status = "未知"
        
        statistics.append({
            "activity_id": row.id,
            "activity_name": row.activities_name,
            "activity_type": row.activities_type,
            "activity_type_name": "满减" if row.activities_type == '1' else "折扣" if row.activities_type == '2' else "其他",
            "face_value": round(float(row.face_value), 2) if row.face_value else 0,
            "min_spend": round(float(row.min_spend), 2) if row.min_spend else 0,
            "start_time": row.start_time.strftime("%Y-%m-%d %H:%M:%S") if row.start_time else None,
            "end_time": row.end_time.strftime("%Y-%m-%d %H:%M:%S") if row.end_time else None,
            "status": status
        })
    
    return statistics