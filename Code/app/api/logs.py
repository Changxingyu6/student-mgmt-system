"""
日志管理API路由
提供登录日志和操作日志的查询接口
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from services.log import LoginLogService, OperationLogService
from utils.logger import get_logger

logger = get_logger("logs_api")

router = APIRouter(prefix="/logs", tags=["日志管理"])


@router.get("/login", summary="查询登录日志列表")
def get_login_logs(
    user_id: int = Query(None, description="用户ID"),
    start_time: datetime = Query(None, description="开始时间"),
    end_time: datetime = Query(None, description="结束时间"),
    status: str = Query(None, description="登录状态: success/failed"),
    page: int = Query(1, description="页码"),
    limit: int = Query(10, description="每页数量"),
    db: Session = Depends(get_db)
):
    """分页查询登录日志"""
    result = LoginLogService.get_login_logs(
        db, user_id, start_time, end_time, status, page, limit
    )
    return {"code": 200, "message": "查询成功", "data": result}


@router.get("/operation", summary="查询操作日志列表")
def get_operation_logs(
    user_id: int = Query(None, description="用户ID"),
    module: str = Query(None, description="操作模块"),
    action: str = Query(None, description="操作类型"),
    start_time: datetime = Query(None, description="开始时间"),
    end_time: datetime = Query(None, description="结束时间"),
    page: int = Query(1, description="页码"),
    limit: int = Query(10, description="每页数量"),
    db: Session = Depends(get_db)
):
    """分页查询操作日志"""
    result = OperationLogService.get_operation_logs(
        db, user_id, module, action, start_time, end_time, page, limit
    )
    return {"code": 200, "message": "查询成功", "data": result}


@router.delete("/cleanup", summary="清理过期日志")
def cleanup_old_logs(
    login_days: int = Query(90, description="登录日志保留天数"),
    operation_days: int = Query(180, description="操作日志保留天数"),
    db: Session = Depends(get_db)
):
    """清理过期日志"""
    result = OperationLogService.cleanup_old_logs(db, login_days, operation_days)
    if not result:
        return {"code": 500, "message": "清理失败"}
    return {"code": 200, "message": "清理成功", "data": result}