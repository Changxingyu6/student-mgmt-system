"""
日志管理 API 路由
提供登录日志的查询接口
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from services import log_service
from utils.logger import get_logger
from utils import format_response
from schema.base import ApiResponse

logger = get_logger("logs_api")

router = APIRouter(prefix="/logs", tags=["日志管理"])


@router.get("/login", response_model=ApiResponse[dict], summary="查询登录日志列表")
def get_login_logs(
    user_id: str = Query(None, description="用户ID"),
    start_time: datetime = Query(None, description="开始时间"),
    end_time: datetime = Query(None, description="结束时间"),
    status: str = Query(None, description="登录状态 success/failed"),
    page: int = Query(1, description="页码"),
    limit: int = Query(10, description="每页数量"),
    db: Session = Depends(get_db)
):
    """分页查询登录日志"""
    result = log_service.LoginLogService.get_login_logs(
        db, user_id, start_time, end_time, status, page, limit
    )
    return format_response(data=result, message="查询成功")


@router.delete("/cleanup", response_model=ApiResponse[dict], summary="清理过期日志")
def cleanup_old_logs(
    login_days: int = Query(90, description="登录日志保留天数"),
    db: Session = Depends(get_db)
):
    """清理过期日志"""
    result = log_service.LoginLogService.cleanup_old_logs(db, login_days)
    if not result:
        return format_response(message="清理失败", code=500)
    return format_response(data=result, message="清理成功")
