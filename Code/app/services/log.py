"""
日志服务层
提供登录日志和操作日志的业务逻辑
"""
from sqlalchemy.orm import Session
from typing import Optional, Dict
from datetime import datetime
from dao.log import (
    create_login_log,
    get_login_logs,
    get_login_log_count,
    create_operation_log,
    get_operation_logs,
    get_operation_log_count,
    delete_old_login_logs,
    delete_old_operation_logs
)
from utils.logger import get_logger

logger = get_logger("log_service")


class LoginLogService:
    """登录日志服务"""
    
    @staticmethod
    def log_login(db: Session, username: str, ip_address: str, user_agent: str = "",
                 login_type: str = "password", status: str = "success", 
                 user_id: int = None, error_message: str = ""):
        """记录登录日志"""
        try:
            create_login_log(
                db,
                user_id=user_id,
                username=username,
                ip_address=ip_address,
                user_agent=user_agent,
                login_type=login_type,
                status=status,
                error_message=error_message
            )
            logger.info(f"登录日志记录成功 - 用户: {username} - 状态: {status}")
        except Exception as e:
            logger.error(f"记录登录日志失败: {str(e)}")
    
    @staticmethod
    def get_login_logs(db: Session, user_id: int = None, start_time: datetime = None,
                      end_time: datetime = None, status: str = None, 
                      page: int = 1, limit: int = 10) -> Dict:
        """分页查询登录日志"""
        logs = get_login_logs(db, user_id, start_time, end_time, status, page, limit)
        total = get_login_log_count(db, user_id, start_time, end_time, status)
        
        result = []
        for log in logs:
            result.append({
                "id": log.id,
                "user_id": log.user_id,
                "username": log.username,
                "ip_address": log.ip_address,
                "user_agent": log.user_agent,
                "login_type": log.login_type,
                "status": log.status,
                "error_message": log.error_message,
                "created_at": log.created_at.strftime("%Y-%m-%d %H:%M:%S") if log.created_at else None
            })
        
        return {
            "data": result,
            "total": total,
            "page": page,
            "limit": limit
        }


class OperationLogService:
    """操作日志服务"""
    
    @staticmethod
    def log_operation(db: Session, user_id: int, username: str, module: str, 
                     action: str, target_id: int = None, target_name: str = "",
                     before_data: str = "", after_data: str = "", ip_address: str = ""):
        """记录操作日志"""
        try:
            create_operation_log(
                db,
                user_id=user_id,
                username=username,
                module=module,
                action=action,
                target_id=target_id,
                target_name=target_name,
                before_data=before_data,
                after_data=after_data,
                ip_address=ip_address
            )
            logger.info(f"操作日志记录成功 - 用户: {username} - 模块: {module} - 操作: {action}")
        except Exception as e:
            logger.error(f"记录操作日志失败: {str(e)}")
    
    @staticmethod
    def get_operation_logs(db: Session, user_id: int = None, module: str = None,
                          action: str = None, start_time: datetime = None,
                          end_time: datetime = None, page: int = 1, 
                          limit: int = 10) -> Dict:
        """分页查询操作日志"""
        logs = get_operation_logs(db, user_id, module, action, start_time, end_time, page, limit)
        total = get_operation_log_count(db, user_id, module, action, start_time, end_time)
        
        result = []
        for log in logs:
            result.append({
                "id": log.id,
                "user_id": log.user_id,
                "username": log.username,
                "module": log.module,
                "action": log.action,
                "target_id": log.target_id,
                "target_name": log.target_name,
                "before_data": log.before_data,
                "after_data": log.after_data,
                "ip_address": log.ip_address,
                "created_at": log.created_at.strftime("%Y-%m-%d %H:%M:%S") if log.created_at else None
            })
        
        return {
            "data": result,
            "total": total,
            "page": page,
            "limit": limit
        }
    
    @staticmethod
    def cleanup_old_logs(db: Session, login_days: int = 90, operation_days: int = 180):
        """清理过期日志"""
        try:
            login_deleted = delete_old_login_logs(db, login_days)
            operation_deleted = delete_old_operation_logs(db, operation_days)
            logger.info(f"清理过期日志 - 登录日志删除: {login_deleted} 条, 操作日志删除: {operation_deleted} 条")
            return {"login_deleted": login_deleted, "operation_deleted": operation_deleted}
        except Exception as e:
            logger.error(f"清理过期日志失败: {str(e)}")
            return None