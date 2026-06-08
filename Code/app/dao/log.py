"""
日志数据访问层
提供登录日志和操作日志的数据库操作
"""
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta
from model.log import LoginLog, OperationLog
from utils.uuid_utils import generate_uuid


def create_login_log(db: Session, **kwargs) -> LoginLog:
    """创建登录日志"""
    kwargs['id'] = generate_uuid()
    log = LoginLog(**kwargs)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_login_logs(db: Session, user_id: str = None, start_time: datetime = None, 
                  end_time: datetime = None, status: str = None, page: int = 1, 
                  limit: int = 10) -> List[LoginLog]:
    """查询登录日志列表"""
    query = db.query(LoginLog)
    
    if user_id:
        query = query.filter(LoginLog.user_id == user_id)
    if start_time:
        query = query.filter(LoginLog.create_time >= start_time)
    if end_time:
        query = query.filter(LoginLog.create_time <= end_time)
    if status:
        query = query.filter(LoginLog.status == status)
    
    offset = (page - 1) * limit
    return query.order_by(LoginLog.create_time.desc()).offset(offset).limit(limit).all()


def get_login_log_count(db: Session, user_id: str = None, start_time: datetime = None, 
                       end_time: datetime = None, status: str = None) -> int:
    """统计登录日志数量"""
    query = db.query(LoginLog)
    
    if user_id:
        query = query.filter(LoginLog.user_id == user_id)
    if start_time:
        query = query.filter(LoginLog.create_time >= start_time)
    if end_time:
        query = query.filter(LoginLog.create_time <= end_time)
    if status:
        query = query.filter(LoginLog.status == status)
    
    return query.count()


def create_operation_log(db: Session, **kwargs) -> OperationLog:
    """创建操作日志"""
    kwargs['id'] = generate_uuid()
    log = OperationLog(**kwargs)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_operation_logs(db: Session, user_id: str = None, module: str = None, 
                      action: str = None, start_time: datetime = None, 
                      end_time: datetime = None, page: int = 1, 
                      limit: int = 10) -> List[OperationLog]:
    """查询操作日志列表"""
    query = db.query(OperationLog)
    
    if user_id:
        query = query.filter(OperationLog.user_id == user_id)
    if module:
        query = query.filter(OperationLog.module == module)
    if action:
        query = query.filter(OperationLog.action == action)
    if start_time:
        query = query.filter(OperationLog.create_time >= start_time)
    if end_time:
        query = query.filter(OperationLog.create_time <= end_time)
    
    offset = (page - 1) * limit
    return query.order_by(OperationLog.create_time.desc()).offset(offset).limit(limit).all()


def get_operation_log_count(db: Session, user_id: str = None, module: str = None, 
                           action: str = None, start_time: datetime = None, 
                           end_time: datetime = None) -> int:
    """统计操作日志数量"""
    query = db.query(OperationLog)
    
    if user_id:
        query = query.filter(OperationLog.user_id == user_id)
    if module:
        query = query.filter(OperationLog.module == module)
    if action:
        query = query.filter(OperationLog.action == action)
    if start_time:
        query = query.filter(OperationLog.create_time >= start_time)
    if end_time:
        query = query.filter(OperationLog.create_time <= end_time)
    
    return query.count()


def delete_old_login_logs(db: Session, days: int = 90) -> int:
    """删除指定天数之前的登录日志"""
    cutoff_time = datetime.now() - timedelta(days=days)
    deleted_count = db.query(LoginLog).filter(LoginLog.create_time < cutoff_time).delete()
    db.commit()
    return deleted_count


def delete_old_operation_logs(db: Session, days: int = 180) -> int:
    """删除指定天数之前的操作日志"""
    cutoff_time = datetime.now() - timedelta(days=days)
    deleted_count = db.query(OperationLog).filter(OperationLog.create_time < cutoff_time).delete()
    db.commit()
    return deleted_count