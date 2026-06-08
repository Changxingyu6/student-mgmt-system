"""
数据分析业务逻辑层
负责用户统计相关的业务处理
"""
from datetime import datetime

from sqlalchemy.orm import Session
from typing import Dict, List
from dao import data_analysis_dao as analysis_dao
from utils.logger import get_logger

logger = get_logger("data_analysis")


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