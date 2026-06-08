"""
数据分析数据访问层
提供用户统计相关的数据库操作
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from model.user import User


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