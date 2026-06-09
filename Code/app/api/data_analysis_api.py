"""
数据分析 API 路由
提供用户统计相关的 RESTful API 接口
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict
from database import get_db
from services import data_analysis_service as analysis_service
from utils import format_response

router = APIRouter(prefix="/data-analysis", tags=["数据分析"])


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