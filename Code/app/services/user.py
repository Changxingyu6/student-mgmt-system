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
from schema.user import UserResponse

# 获取日志记录器
logger = get_logger("user")

# 登录失败限制配置（从环境变量读取）
MAX_FAILED_ATTEMPTS = int(os.getenv("MAX_FAILED_ATTEMPTS", "5"))
# 阶梯式锁定时间配置（分钟），逗号分隔：第1次锁定时长,第2次锁定时长,...
LOCK_DURATIONS = [int(x) for x in os.getenv("LOCK_DURATIONS", "5,15,30,60,120").split(",")]


def get_lock_duration_by_count(lock_count: int) -> int:
    """根据锁定次数获取对应的锁定时长（分钟）"""
    index = min(lock_count - 1, len(LOCK_DURATIONS) - 1)
    return LOCK_DURATIONS[index]


def check_user_locked(db: Session, username: str) -> bool:
    """检查用户是否被锁定"""
    user = user_repo.get_user_with_lock_status(db, username)
    if not user:
        return False
    
    if user.lock_until:
        now = datetime.now()
        if user.lock_until > now:
            return True
        else:
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


def _convert_user_to_response(user) -> dict:
    """将用户对象转换为响应格式"""
    now = datetime.now()
    is_locked = False
    if user.lock_until and user.lock_until > now:
        is_locked = True
    
    return {
        "id": user.id,
        "username": user.username,
        "nickname": user.nickname,
        "phone": user.phone,
        "email": user.email,
        "gender": user.gender,
        "avatar": user.avatar,
        "user_level": user.user_level,
        "points": user.points or 0,
        "balance": float(user.balance or 0),
        "discount_rate": float(user.discount_rate or 1.0),
        "discount_expire_at": user.discount_expire_at,
        "status": user.status,
        "is_locked": is_locked,
        "failed_attempts": user.failed_attempts or 0,
        "lock_count": user.lock_count or 0,
        "created_at": user.created_at,
        "updated_at": user.updated_at
    }


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
    return _convert_user_to_response(user)


def login_for_access_token(
    username: str, 
    password: str, 
    db: Session,
    ip_address: str = "",
    user_agent: str = ""
) -> dict:
    """用户登录获取token"""
    logger.info(f"用户登录尝试 - 用户名: {username}")
    
    if check_user_locked(db, username):
        remaining_seconds = get_lock_remaining_time(db, username)
        remaining_minutes = (remaining_seconds // 60) + 1
        logger.warn(f"登录失败 - 账户已被锁定 - 用户名: {username}")
        
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
        user_repo.increment_failed_attempts(db, username)
        
        db_user = user_repo.get_user_with_lock_status(db, username)
        failed_count = db_user.failed_attempts if db_user else 0
        
        if failed_count >= MAX_FAILED_ATTEMPTS:
            db_user = user_repo.get_user_with_lock_status(db, username)
            current_lock_count = (db_user.lock_count or 0) + 1
            lock_duration = get_lock_duration_by_count(current_lock_count)
            user_repo.lock_user(db, username, lock_duration)
            logger.error(f"账户已被锁定 - 用户名: {username} - 锁定次数: {current_lock_count} - 锁定时长: {lock_duration}分钟")
            
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
    
    user_repo.reset_failed_attempts(db, username)
    user_repo.reset_lock_count(db, username)
    
    access_token = create_access_token(
        data={
            "sub": str(user["id"]),
            "username": user["username"],
            "roles": ["admin"],
            "user_id": user["id"]
        }
    )
    
    logger.info(f"登录成功 - 用户名: {username}")
    
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
    
    user = user_repo.get_user_by_id(db, user_id)
    
    if not user:
        logger.error(f"修改密码失败 - 用户不存在 - 用户ID: {user_id}")
        raise HTTPException(status_code=404, detail="用户不存在")
    
    if not verify_password(user.salt, old_password, user.password):
        logger.warn(f"修改密码失败 - 旧密码不正确 - 用户ID: {user_id}")
        raise HTTPException(status_code=400, detail="旧密码不正确")
    
    validate_password(new_password)
    
    new_salt = generate_salt()
    hashed_new_password = md5_hash(new_salt, new_password)
    
    updated_user = user_repo.update_user_password(db, user_id, hashed_new_password, new_salt)
    
    logger.info(f"密码修改成功 - 用户ID: {user_id} - 用户名: {updated_user.username}")
    
    return _convert_user_to_response(updated_user)


def register_user(
    db: Session,
    username: str, 
    password: str, 
    nickname: str = None,
    phone: str = None,
    email: str = None
) -> dict:
    """注册新用户"""
    logger.info(f"用户注册尝试 - 用户名: {username}")
    
    if user_repo.check_username_exists(db, username):
        logger.warn(f"注册失败 - 用户名已存在 - 用户名: {username}")
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    validate_password(password)
    
    salt = generate_salt()
    hashed_password = md5_hash(salt, password)
    
    new_user = user_repo.create_user(db, username, hashed_password, salt, nickname, phone, email)
    
    logger.info(f"注册成功 - 用户名: {username} - 用户ID: {new_user.id}")
    
    return _convert_user_to_response(new_user)


def get_user_by_id(db: Session, user_id: int) -> dict:
    """获取用户详情"""
    logger.info(f"获取用户详情 - 用户ID: {user_id}")
    
    user = user_repo.get_user_by_id(db, user_id)
    if not user:
        logger.error(f"获取用户详情失败 - 用户不存在 - 用户ID: {user_id}")
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return _convert_user_to_response(user)


def get_all_users(db: Session, page: int = 1, limit: int = 10) -> dict:
    """获取所有用户列表（管理员用）"""
    logger.info(f"获取用户列表 - 页码: {page}, 每页数量: {limit}")
    users = user_repo.get_all_users(db, page, limit)
    total = user_repo.count_users(db)
    
    result = []
    for user in users:
        result.append(_convert_user_to_response(user))
    
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
    for user in users:
        result.append(_convert_user_to_response(user))
    
    return result


def unlock_user_account(db: Session, user_id: int) -> dict:
    """解锁用户账户（管理员用）"""
    logger.info(f"解锁用户账户 - 用户ID: {user_id}")
    
    user = user_repo.unlock_user(db, user_id)
    if not user:
        logger.error(f"解锁失败 - 用户不存在 - 用户ID: {user_id}")
        raise HTTPException(status_code=404, detail="用户不存在")
    
    logger.info(f"解锁成功 - 用户ID: {user_id} - 用户名: {user.username}")
    
    return _convert_user_to_response(user)


def create_user(
    db: Session,
    username: str,
    password: str,
    nickname: str = None,
    phone: str = None,
    email: str = None,
    user_level: str = "青铜会员",
    balance: float = 0.00,
    status: str = "active"
) -> dict:
    """管理员创建用户"""
    logger.info(f"管理员创建用户 - 用户名: {username}")
    
    if user_repo.check_username_exists(db, username):
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    validate_password(password)
    
    salt = generate_salt()
    hashed_password = md5_hash(salt, password)
    
    new_user = user_repo.create_user(
        db, username, hashed_password, salt, 
        nickname, phone, email, user_level, balance, status
    )
    
    logger.info(f"创建用户成功 - 用户ID: {new_user.id}")
    
    return _convert_user_to_response(new_user)


def update_user(
    db: Session,
    user_id: int,
    nickname: str = None,
    phone: str = None,
    email: str = None,
    user_level: str = None,
    status: str = None
) -> dict:
    """管理员更新用户信息"""
    logger.info(f"管理员更新用户信息 - 用户ID: {user_id}")
    
    user = user_repo.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    update_data = {}
    if nickname is not None:
        update_data['nickname'] = nickname
    if phone is not None:
        update_data['phone'] = phone
    if email is not None:
        update_data['email'] = email
    if user_level is not None:
        update_data['user_level'] = user_level
    if status is not None:
        update_data['status'] = status
    
    updated_user = user_repo.update_user(db, user_id, **update_data)
    
    logger.info(f"更新用户信息成功 - 用户ID: {user_id}")
    
    return _convert_user_to_response(updated_user)


def delete_user(db: Session, user_id: int) -> dict:
    """管理员删除用户（逻辑删除）"""
    logger.info(f"管理员删除用户 - 用户ID: {user_id}")
    
    if not user_repo.delete_user(db, user_id):
        raise HTTPException(status_code=404, detail="用户不存在")
    
    logger.info(f"删除用户成功 - 用户ID: {user_id}")
    
    return {"id": user_id, "message": "删除成功"}


def freeze_user(db: Session, user_id: int) -> dict:
    """管理员冻结用户账户"""
    logger.info(f"管理员冻结用户 - 用户ID: {user_id}")
    
    user = user_repo.freeze_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    logger.info(f"冻结用户成功 - 用户ID: {user_id}")
    
    return _convert_user_to_response(user)


def unfreeze_user(db: Session, user_id: int) -> dict:
    """管理员解冻用户账户"""
    logger.info(f"管理员解冻用户 - 用户ID: {user_id}")
    
    user = user_repo.unfreeze_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    logger.info(f"解冻用户成功 - 用户ID: {user_id}")
    
    return _convert_user_to_response(user)


def recharge_balance(db: Session, user_id: int, amount: float, reason: str = None) -> dict:
    """管理员为用户充值余额"""
    logger.info(f"管理员充值余额 - 用户ID: {user_id}, 金额: {amount}")
    
    if amount <= 0:
        raise HTTPException(status_code=400, detail="充值金额必须大于0")
    
    user = user_repo.update_balance(db, user_id, amount)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    logger.info(f"充值成功 - 用户ID: {user_id}, 余额: {user.balance}")
    
    return _convert_user_to_response(user)


def deduct_balance(db: Session, user_id: int, amount: float, reason: str = None) -> dict:
    """管理员扣除用户余额"""
    logger.info(f"管理员扣除余额 - 用户ID: {user_id}, 金额: {amount}")
    
    if amount <= 0:
        raise HTTPException(status_code=400, detail="扣除金额必须大于0")
    
    user = user_repo.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    if (user.balance or 0) < amount:
        raise HTTPException(status_code=400, detail="余额不足")
    
    user = user_repo.update_balance(db, user_id, -amount)
    
    logger.info(f"扣除成功 - 用户ID: {user_id}, 余额: {user.balance}")
    
    return _convert_user_to_response(user)


def upgrade_user_level(db: Session, user_id: int, level: str) -> dict:
    """管理员升级用户等级"""
    logger.info(f"管理员升级用户等级 - 用户ID: {user_id}, 等级: {level}")
    
    valid_levels = ["青铜会员", "白银会员", "黄金会员"]
    if level not in valid_levels:
        raise HTTPException(status_code=400, detail=f"无效的用户等级，可选值: {', '.join(valid_levels)}")
    
    user = user_repo.update_user_level(db, user_id, level)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    logger.info(f"升级成功 - 用户ID: {user_id}, 等级: {user.user_level}")
    
    return _convert_user_to_response(user)


def set_user_discount(db: Session, user_id: int, discount_rate: float, expire_at: datetime = None) -> dict:
    """管理员设置用户折扣"""
    logger.info(f"管理员设置用户折扣 - 用户ID: {user_id}, 折扣率: {discount_rate}")
    
    if discount_rate <= 0 or discount_rate > 1:
        raise HTTPException(status_code=400, detail="折扣率必须在0到1之间")
    
    user = user_repo.update_user_discount(db, user_id, discount_rate, expire_at)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    logger.info(f"设置折扣成功 - 用户ID: {user_id}, 折扣率: {user.discount_rate}")
    
    return _convert_user_to_response(user)


def update_user_profile(
    db: Session,
    user_id: int,
    nickname: str = None,
    phone: str = None,
    email: str = None,
    gender: str = None,
    avatar: str = None
) -> dict:
    """用户更新个人信息"""
    logger.info(f"用户更新个人信息 - 用户ID: {user_id}")
    
    update_data = {}
    if nickname is not None:
        update_data['nickname'] = nickname
    if phone is not None:
        update_data['phone'] = phone
    if email is not None:
        update_data['email'] = email
    if gender is not None:
        update_data['gender'] = gender
    if avatar is not None:
        update_data['avatar'] = avatar
    
    updated_user = user_repo.update_user(db, user_id, **update_data)
    if not updated_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    logger.info(f"更新个人信息成功 - 用户ID: {user_id}")
    
    return _convert_user_to_response(updated_user)