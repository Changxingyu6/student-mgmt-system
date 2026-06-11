"""
数据分析业务逻辑层
负责用户统计、商品统计、订单统计和营销统计相关的业务处理
"""
from datetime import datetime

from sqlalchemy.orm import Session
from typing import Dict, List
from dao import data_analysis_dao as analysis_dao
from utils.logger import get_logger

logger = get_logger("data_analysis")


# ========== 用户统计相关 ==========

def get_weekly_new_users(db: Session) -> Dict:
    """获取当周新增用户数"""
    logger.debug("统计当周新增用户")
    count = analysis_dao.count_weekly_new_users(db)
    return {"weekly_new_users": count}


def get_monthly_new_users(db: Session) -> Dict:
    """获取当月新增用户数"""
    logger.debug("统计当月新增用户")
    count = analysis_dao.count_monthly_new_users(db)
    return {"monthly_new_users": count}


def get_user_statistics(db: Session) -> Dict:
    """获取用户综合统计数据"""
    logger.debug("获取用户综合统计数据")
    weekly = analysis_dao.count_weekly_new_users(db)
    monthly = analysis_dao.count_monthly_new_users(db)
    return {
        "weekly_new_users": weekly,
        "monthly_new_users": monthly,
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def get_user_level_statistics(db: Session) -> Dict:
    """获取各用户等级的人数统计"""
    logger.debug("统计各用户等级人数")
    level_data = analysis_dao.count_users_by_level(db)
    
    level_mapping = {'青铜会员': 0, '白银会员': 0, '黄金会员': 0}
    for item in level_data:
        if item["level"] in level_mapping:
            level_mapping[item["level"]] = item["count"]
    
    return {
        "level_statistics": [
            {"level": "青铜会员", "count": level_mapping["青铜会员"]},
            {"level": "白银会员", "count": level_mapping["白银会员"]},
            {"level": "黄金会员", "count": level_mapping["黄金会员"]}
        ],
        "total_users": sum(level_mapping.values())
    }


# ========== 商品统计相关 ==========

def get_top_selling_goods(db: Session, limit: int = 20) -> Dict:
    """获取销量前N的商品"""
    logger.debug(f"获取销量前{limit}的商品")
    goods_list = analysis_dao.get_top_selling_goods(db, limit)
    
    return {
        "top_selling_goods": goods_list,
        "total_count": len(goods_list),
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def get_category_statistics(db: Session) -> Dict:
    """获取各商品分类统计数据"""
    logger.debug("获取商品分类统计")
    category_list = analysis_dao.get_category_statistics(db)
    
    total_goods = sum(item["goods_count"] for item in category_list)
    
    return {
        "category_statistics": category_list,
        "total_categories": len(category_list),
        "total_goods": total_goods,
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def get_low_stock_goods(db: Session) -> Dict:
    """获取库存低于预警值的商品"""
    logger.debug("获取低库存商品")
    low_stock_list = analysis_dao.get_low_stock_goods(db)
    
    total_shortage = sum(item["stock_shortage"] for item in low_stock_list)
    
    return {
        "low_stock_goods": low_stock_list,
        "total_low_stock": len(low_stock_list),
        "total_shortage": total_shortage,
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


# ========== 订单统计相关 ==========

def get_order_statistics_by_period(db: Session, period: str = 'day') -> Dict:
    """按日/周/月统计订单数据"""
    logger.debug(f"按{period}统计订单数据")
    period_map = {'day': '日', 'week': '周', 'month': '月'}
    
    statistics = analysis_dao.get_order_statistics_by_period(db, period)
    
    total_orders = sum(item["total_orders"] for item in statistics)
    total_amount = sum(item["total_amount"] for item in statistics)
    avg_refund_ratio = sum(item["refund_ratio"] for item in statistics) / len(statistics) if statistics else 0
    
    return {
        "period_type": period_map.get(period, period),
        "order_statistics": statistics,
        "total_orders": total_orders,
        "total_amount": round(total_amount, 2),
        "avg_refund_ratio": round(avg_refund_ratio, 2),
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def get_payment_method_statistics(db: Session) -> Dict:
    """获取各支付方式统计数据"""
    logger.debug("获取支付方式统计")
    payment_list = analysis_dao.get_payment_method_statistics(db)
    
    total_orders = sum(item["order_count"] for item in payment_list)
    total_amount = sum(item["total_amount"] for item in payment_list)
    
    return {
        "payment_statistics": payment_list,
        "total_orders": total_orders,
        "total_amount": round(total_amount, 2),
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def get_overdue_unpaid_orders(db: Session, timeout_hours: int = 24) -> Dict:
    """获取未付款超时订单"""
    logger.debug(f"获取超过{timeout_hours}小时未付款的超时订单")
    overdue_list = analysis_dao.get_overdue_unpaid_orders(db, timeout_hours)
    
    total_amount = sum(item["total_amount"] for item in overdue_list)
    
    return {
        "overdue_orders": overdue_list,
        "total_overdue": len(overdue_list),
        "total_amount": round(total_amount, 2),
        "timeout_hours": timeout_hours,
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def get_long_time_unshipped_orders(db: Session, timeout_hours: int = 48) -> Dict:
    """获取长时间未发货订单"""
    logger.debug(f"获取超过{timeout_hours}小时未发货的订单")
    unshipped_list = analysis_dao.get_long_time_unshipped_orders(db, timeout_hours)
    
    total_amount = sum(item["total_amount"] for item in unshipped_list)
    
    return {
        "unshipped_orders": unshipped_list,
        "total_unshipped": len(unshipped_list),
        "total_amount": round(total_amount, 2),
        "timeout_hours": timeout_hours,
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


# ========== 营销数据统计相关 ==========

def get_coupon_statistics(db: Session) -> Dict:
    """获取优惠券统计数据"""
    logger.debug("获取优惠券统计")
    coupon_list = analysis_dao.get_coupon_statistics(db)
    
    total_sent = sum(item["sent_count"] for item in coupon_list)
    total_used = sum(item["used_count"] for item in coupon_list)
    total_use_rate = round(total_used / total_sent * 100, 2) if total_sent > 0 else 0
    
    return {
        "coupon_statistics": coupon_list,
        "total_coupons": len(coupon_list),
        "total_sent": total_sent,
        "total_used": total_used,
        "overall_use_rate": total_use_rate,
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def get_activity_statistics(db: Session) -> Dict:
    """获取营销活动统计数据"""
    logger.debug("获取营销活动统计")
    activity_list = analysis_dao.get_activity_statistics(db)
    
    # 统计进行中、未开始、已结束的活动数量
    ongoing_count = sum(1 for item in activity_list if item["status"] == "进行中")
    upcoming_count = sum(1 for item in activity_list if item["status"] == "未开始")
    ended_count = sum(1 for item in activity_list if item["status"] == "已结束")
    
    return {
        "activity_statistics": activity_list,
        "total_activities": len(activity_list),
        "ongoing_count": ongoing_count,
        "upcoming_count": upcoming_count,
        "ended_count": ended_count,
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }