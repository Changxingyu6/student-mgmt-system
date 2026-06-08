"""
用户业务逻辑层
负责用户登录、密码验证、JWT生成、用户管理等业务
"""
import os
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from fastapi import HTTPException, status
from dao import user as user_repo
from utils import generate_salt, md5_hash, verify_password, create_access_token
from utils.logger import get_logger
from utils.password_policy import validate_password
from services.log import LoginLogService

# 获取日志记录器
logger = get_logger("user")

# 登录失败限制配置（从环境变量读取）
MAX_FAILED_ATTEMPTS = int(os.getenv("MAX_FAILED_ATTEMPTS", "5"))
# 阶梯式锁定时间配置（分钟），逗号分隔：第1次锁定时长,第2次锁定时长,...
LOCK_DURATIONS = [int(x) for x in os.getenv("LOCK_DURATIONS", "5,15,30,60,120").split(",")]


def get_lock_duration_by_count(lock_count: int) -> int:
    """根据锁定次数获取对应的锁定时长（分钟）"""
    # lock_count 从 1 开始，数组索引从 0 开始
    index = min(lock_count - 1, len(LOCK_DURATIONS) - 1)
    return LOCK_DURATIONS[index]


def check_user_locked(db: Session, username: str) -> bool:
    """检查用户是否被锁定"""
    user = user_repo.get_user_with_lock_status(db, username)
    if not user:
        return False
    
    # 检查锁定时间是否已过期
    if user.lock_until:
        now = datetime.now()
        if user.lock_until > now:
            return True
        else:
            # 锁定时间已过期，自动解锁
            user_repo.reset_failed_attempts(db, username)
    return False


def get_lock_remaining_time(db: Session, username: str) -> int:
    """获取剩余锁定时间（秒）"""
    user = user_repo.get_user_with_lock_status(db, username)
    if not user or not user.lock_until:
        return 0
    
    now = datetime.now()
    remaining = (user.lock_until - now).total_seconds()
    return max(0, int(remaining))


def authenticate_user(
    username: str, 
    password: str, 
    db: Session
) -> Optional[dict]:
    """验证用户身份"""
    logger.debug(f"验证用户身份 - 用户名: {username}")
    user = user_repo.get_user_by_username(db, username)
    if not user:
        logger.warn(f"用户不存在 - 用户名: {username}")
        return None
    if not verify_password(user.salt, password, user.password):
        logger.warn(f"密码验证失败 - 用户名: {username}")
        return None
    
    logger.debug(f"用户验证成功 - 用户名: {username}")
    # 返回用户信息（不含密码和salt）
    return {
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "related_id": user.related_id
    }


def login_for_access_token(
    username: str, 
    password: str, 
    db: Session,
    ip_address: str = "",
    user_agent: str = ""
) -> dict:
    """用户登录获取token"""
    logger.info(f"用户登录尝试 - 用户名: {username}")
    
    # 检查用户是否被锁定
    if check_user_locked(db, username):
        remaining_seconds = get_lock_remaining_time(db, username)
        remaining_minutes = (remaining_seconds // 60) + 1
        logger.warn(f"登录失败 - 账户已被锁定 - 用户名: {username}")
        
        # 记录登录失败日志
        LoginLogService.log_login(
            db=db,
            username=username,
            ip_address=ip_address,
            user_agent=user_agent,
            login_type="password",
            status="failed",
            error_message=f"账户已被锁定，请{remaining_minutes}分钟后再试"
        )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"账户已被锁定，请{remaining_minutes}分钟后再试",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = authenticate_user(username, password, db)
    
    if not user:
        # 增加失败次数
        user_repo.increment_failed_attempts(db, username)
        
        # 获取当前失败次数
        db_user = user_repo.get_user_with_lock_status(db, username)
        failed_count = db_user.failed_attempts if db_user else 0
        
        if failed_count >= MAX_FAILED_ATTEMPTS:
            # 获取当前用户的锁定次数
            db_user = user_repo.get_user_with_lock_status(db, username)
            current_lock_count = (db_user.lock_count or 0) + 1
            # 获取对应的锁定时长
            lock_duration = get_lock_duration_by_count(current_lock_count)
            # 锁定账户
            user_repo.lock_user(db, username, lock_duration)
            logger.error(f"账户已被锁定 - 用户名: {username} - 锁定次数: {current_lock_count} - 锁定时长: {lock_duration}分钟")
            
            # 记录登录失败日志
            LoginLogService.log_login(
                db=db,
                username=username,
                ip_address=ip_address,
                user_agent=user_agent,
                login_type="password",
                status="failed",
                error_message=f"登录失败{MAX_FAILED_ATTEMPTS}次，账户已被锁定{lock_duration}分钟（第{current_lock_count}次锁定）"
            )
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"登录失败{MAX_FAILED_ATTEMPTS}次，账户已被锁定{lock_duration}分钟（第{current_lock_count}次锁定）",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        remaining_attempts = MAX_FAILED_ATTEMPTS - failed_count
        logger.warn(f"登录失败 - 用户名或密码错误 - 用户名: {username} - 剩余尝试次数: {remaining_attempts}")
        
        # 记录登录失败日志
        LoginLogService.log_login(
            db=db,
            username=username,
            ip_address=ip_address,
            user_agent=user_agent,
            login_type="password",
            status="failed",
            error_message=f"用户名或密码错误，还剩{remaining_attempts}次尝试机会"
        )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"用户名或密码错误，还剩{remaining_attempts}次尝试机会",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 登录成功，重置失败次数
    user_repo.reset_failed_attempts(db, username)
    
    # 重置锁定次数（登录成功后重新开始阶梯）
    user_repo.reset_lock_count(db, username)
    
    access_token = create_access_token(
        data={
            "sub": str(user["id"]),           # 标准声明：用户ID（字符串格式）
            "username": user["username"],      # 自定义声明：用户名
            "roles": [user["role"]],           # 自定义声明：用户角色列表
            "user_id": user["id"]              # 自定义声明：用户ID（整数格式）
        }
    )
    
    logger.info(f"登录成功 - 用户名: {username} - 角色: {user['role']}")
    
    # 记录登录成功日志
    LoginLogService.log_login(
        db=db,
        user_id=user["id"],
        username=username,
        ip_address=ip_address,
        user_agent=user_agent,
        login_type="password",
        status="success"
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


def update_user_password(
    db: Session,
    user_id: int,
    old_password: str,
    new_password: str
) -> dict:
    """修改用户密码（需要验证旧密码）"""
    logger.info(f"修改密码尝试 - 用户ID: {user_id}")
    
    # 获取用户信息
    user = user_repo.get_user_by_id(db, user_id)
    
    if not user:
        logger.error(f"修改密码失败 - 用户不存在 - 用户ID: {user_id}")
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 验证旧密码
    if not verify_password(user.salt, old_password, user.password):
        logger.warn(f"修改密码失败 - 旧密码不正确 - 用户ID: {user_id}")
        raise HTTPException(status_code=400, detail="旧密码不正确")
    
    # 验证新密码复杂度
    validate_password(new_password)
    
    # 生成新的salt和加密密码
    new_salt = generate_salt()
    hashed_new_password = md5_hash(new_salt, new_password)
    
    # 更新密码
    updated_user = user_repo.update_user(db, user_id, password=hashed_new_password, salt=new_salt)
    
    logger.info(f"密码修改成功 - 用户ID: {user_id} - 用户名: {updated_user.username}")
    
    return {
        "id": updated_user.id,
        "username": updated_user.username,
        "role": updated_user.role,
        "related_id": updated_user.related_id
    }


def register_user(
    db: Session,
    username: str, 
    password: str, 
    role: str = "student", 
    related_id: int = None
) -> dict:
    """注册新用户"""
    logger.info(f"用户注册尝试 - 用户名: {username} - 角色: {role}")
    
    # 检查用户名是否已存在
    existing_user = user_repo.get_user_by_username(db, username)
    if existing_user:
        logger.warn(f"注册失败 - 用户名已存在 - 用户名: {username}")
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 验证密码复杂度
    validate_password(password)
    
    # 生成salt并加密密码
    salt = generate_salt()
    hashed_password = md5_hash(salt, password)
    
    # 创建用户
    new_user = user_repo.create_user(db, username, hashed_password, salt, role, related_id)
    
    logger.info(f"注册成功 - 用户名: {username} - 用户ID: {new_user.id}")
    
    return {
        "id": new_user.id,
        "username": new_user.username,
        "role": new_user.role,
        "related_id": new_user.related_id
    }


def get_all_users(db: Session, page: int = 1, limit: int = 10) -> dict:
    """获取所有用户列表（管理员用）"""
    logger.info(f"获取用户列表 - 页码: {page}, 每页数量: {limit}")
    users = user_repo.get_all_users(db, page, limit)
    total = user_repo.count_users(db)
    
    result = []
    now = datetime.now()
    for user in users:
        is_locked = False
        lock_remaining = 0
        if user.lock_until and user.lock_until > now:
            is_locked = True
            lock_remaining = int((user.lock_until - now).total_seconds())
        
        result.append({
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "related_id": user.related_id,
            "is_active": user.is_active,
            "is_locked": is_locked,
            "lock_remaining_seconds": lock_remaining,
            "failed_attempts": user.failed_attempts or 0,
            "lock_count": user.lock_count or 0
        })
    
    return {
        "data": result,
        "total": total,
        "page": page,
        "limit": limit
    }


def get_locked_users(db: Session) -> List[dict]:
    """获取所有被锁定的用户"""
    logger.info("获取被锁定用户列表")
    users = user_repo.get_locked_users(db)
    
    result = []
    now = datetime.now()
    for user in users:
        lock_remaining = int((user.lock_until - now).total_seconds()) if user.lock_until else 0
        result.append({
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "lock_remaining_seconds": lock_remaining,
            "failed_attempts": user.failed_attempts or 0,
            "lock_count": user.lock_count or 0
        })
    
    return result


def unlock_user_account(db: Session, user_id: int) -> dict:
    """解锁用户账户（管理员用）"""
    logger.info(f"解锁用户账户 - 用户ID: {user_id}")
    
    user = user_repo.unlock_user(db, user_id)
    if not user:
        logger.error(f"解锁失败 - 用户不存在 - 用户ID: {user_id}")
        raise HTTPException(status_code=404, detail="用户不存在")
    
    logger.info(f"解锁成功 - 用户ID: {user_id} - 用户名: {user.username}")
    
    return {
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "is_locked": False
    }