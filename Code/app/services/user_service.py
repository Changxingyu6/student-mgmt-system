"""
用户业务逻辑层
负责用户登录、密码验证、JWT生成、用户管理等业务
"""
import os
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from fastapi import HTTPException, status
from dao import user_dao as user_repo
from utils import generate_salt, md5_hash, verify_password, create_access_token
from utils.logger import get_logger
from services.log_service import LoginLogService
from schema.user import UserResponse

logger = get_logger("user")

MAX_FAILED_ATTEMPTS = int(os.getenv("MAX_FAILED_ATTEMPTS", "5"))
LOCK_DURATIONS = [int(x) for x in os.getenv("LOCK_DURATIONS", "5,15,30,60,120").split(",")]


def get_lock_duration_by_count(lock_count: int) -> int:
    index = min(lock_count - 1, len(LOCK_DURATIONS) - 1)
    return LOCK_DURATIONS[index]


def check_user_locked(db: Session, username: str) -> bool:
    user = user_repo.get_user_with_lock_status(db, username)
    if not user:
        return False
    
    if user.lock_until:
        now = datetime.now()
        if user.lock_until > now:
            return True
        else:
            user_repo.reset_failed_attempts(db, username)
            db.commit()
    return False


def get_lock_remaining_time(db: Session, username: str) -> int:
    user = user_repo.get_user_with_lock_status(db, username)
    if not user or not user.lock_until:
        return 0
    
    now = datetime.now()
    remaining = (user.lock_until - now).total_seconds()
    return max(0, int(remaining))


def _convert_user_to_response(user) -> dict:
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
        "status": user.status,
        "is_locked": is_locked,
        "failed_attempts": user.failed_attempts or 0,
        "lock_count": user.lock_count or 0,
        "create_time": user.create_time,
        "update_time": user.update_time,
        "role": user.role.role_name if user.role else "user"
    }


def authenticate_user(username: str, password: str, db: Session) -> Optional[dict]:
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
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"账户已被锁定，请{remaining_minutes}分钟后再试",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = authenticate_user(username, password, db)
    
    if not user:
        user_repo.increment_failed_attempts(db, username)
        db.commit()
        
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
            db.commit()
            
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
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"用户名或密码错误，还剩{remaining_attempts}次尝试机会",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_repo.reset_failed_attempts(db, username)
    user_repo.reset_lock_count(db, username)
    db.commit()
    
    from services import role_service
    user_role = role_service.get_user_role(db, user["id"]) or "user"
    
    access_token = create_access_token(
        data={
            "sub": str(user["id"]),
            "username": user["username"],
            "role": user_role,
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
    db.commit()
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


def update_user_password(db: Session, user_id: str, old_password: str, new_password: str) -> dict:
    logger.info(f"修改密码尝试 - 用户ID: {user_id}")
    
    user = user_repo.get_user_by_id(db, user_id)
    if not user:
        logger.error(f"修改密码失败 - 用户不存在 - 用户ID: {user_id}")
        raise HTTPException(status_code=404, detail="用户不存在")
    
    if not verify_password(user.salt, old_password, user.password):
        logger.warn(f"修改密码失败 - 旧密码不正确 - 用户ID: {user_id}")
        raise HTTPException(status_code=400, detail="旧密码不正确")
    
    new_salt = generate_salt()
    hashed_new_password = md5_hash(new_salt, new_password)
    
    updated_user = user_repo.update_user_password(db, user_id, hashed_new_password, new_salt)
    db.commit()
    db.refresh(updated_user)
    
    logger.info(f"密码修改成功 - 用户ID: {user_id} - 用户名: {updated_user.username}")
    
    return _convert_user_to_response(updated_user)


def register_user(db: Session, username: str, password: str, nickname: str = None,
                 phone: str = None, email: str = None) -> dict:
    logger.info(f"用户注册尝试 - 用户名: {username}")
    
    if user_repo.check_username_exists(db, username):
        logger.warn(f"注册失败 - 用户名已存在 - 用户名: {username}")
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    salt = generate_salt()
    hashed_password = md5_hash(salt, password)
    
    new_user = user_repo.create_user(db, username, hashed_password, salt, nickname, phone, email)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"注册成功 - 用户名: {username} - 用户ID: {new_user.id}")
    
    return _convert_user_to_response(new_user)


def get_user_by_id(db: Session, user_id: str) -> dict:
    logger.info(f"获取用户详情 - 用户ID: {user_id}")
    
    user = user_repo.get_user_by_id(db, user_id)
    if not user:
        logger.error(f"获取用户详情失败 - 用户不存在 - 用户ID: {user_id}")
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return _convert_user_to_response(user)


def get_all_users(db: Session, page: int = 1, limit: int = 10) -> dict:
    logger.info(f"获取用户列表 - 页码: {page}, 每页数量: {limit}")
    users = user_repo.get_all_users(db, page, limit)
    total = user_repo.count_users(db)
    
    result = []
    for user in users:
        result.append(_convert_user_to_response(user))
    
    return {"data": result, "total": total, "page": page, "limit": limit}


def get_locked_users(db: Session) -> List[dict]:
    logger.info("获取被锁定用户列表")
    users = user_repo.get_locked_users(db)
    
    result = []
    for user in users:
        result.append(_convert_user_to_response(user))
    
    return result


def unlock_user_account(db: Session, user_id: str) -> dict:
    logger.info(f"解锁用户账户 - 用户ID: {user_id}")
    
    user = user_repo.unlock_user(db, user_id)
    if not user:
        logger.error(f"解锁失败 - 用户不存在 - 用户ID: {user_id}")
        raise HTTPException(status_code=404, detail="用户不存在")
    
    db.commit()
    db.refresh(user)
    logger.info(f"解锁成功 - 用户ID: {user_id} - 用户名: {user.username}")
    
    return _convert_user_to_response(user)


def create_user(db: Session, username: str, password: str, nickname: str = None,
               phone: str = None, email: str = None, user_level: str = "青铜会员",
               balance: float = 0.00, status: str = "active") -> dict:
    logger.info(f"管理员创建用户 - 用户名: {username}")
    
    if user_repo.check_username_exists(db, username):
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    salt = generate_salt()
    hashed_password = md5_hash(salt, password)
    
    new_user = user_repo.create_user(
        db, username, hashed_password, salt, 
        nickname, phone, email, user_level, balance, status
    )
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"创建用户成功 - 用户ID: {new_user.id}")
    
    return _convert_user_to_response(new_user)


def update_user(db: Session, user_id: str, nickname: str = None, phone: str = None,
               email: str = None, user_level: str = None, status: str = None) -> dict:
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
    db.commit()
    db.refresh(updated_user)
    
    logger.info(f"更新用户信息成功 - 用户ID: {user_id}")
    
    return _convert_user_to_response(updated_user)


def delete_user(db: Session, user_id: str) -> dict:
    logger.info(f"管理员删除用户 - 用户ID: {user_id}")
    
    if not user_repo.delete_user(db, user_id):
        raise HTTPException(status_code=404, detail="用户不存在")
    
    db.commit()
    logger.info(f"删除用户成功 - 用户ID: {user_id}")
    
    return {"id": user_id, "message": "删除成功"}


def recharge_balance(db: Session, user_id: str, amount: float, reason: str = None) -> dict:
    logger.info(f"管理员充值余额 - 用户ID: {user_id}, 金额: {amount}")
    
    if amount <= 0:
        raise HTTPException(status_code=400, detail="充值金额必须大于0")
    
    user = user_repo.update_balance(db, user_id, amount)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    db.commit()
    db.refresh(user)
    logger.info(f"充值成功 - 用户ID: {user_id}, 余额: {user.balance}")
    
    return _convert_user_to_response(user)


def deduct_balance(db: Session, user_id: str, amount: float, reason: str = None) -> dict:
    from decimal import Decimal
    logger.info(f"管理员扣除余额 - 用户ID: {user_id}, 金额: {amount}")
    
    if amount <= 0:
        raise HTTPException(status_code=400, detail="扣除金额必须大于0")
    
    user = user_repo.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    amount_decimal = Decimal(str(amount))
    if Decimal(str(user.balance or 0)) < amount_decimal:
        raise HTTPException(status_code=400, detail="余额不足")
    
    user = user_repo.update_balance(db, user_id, -float(amount_decimal))
    db.commit()
    db.refresh(user)
    
    logger.info(f"扣除成功 - 用户ID: {user_id}, 余额: {user.balance}")
    
    return _convert_user_to_response(user)


def upgrade_user_level(db: Session, user_id: str, level: str) -> dict:
    logger.info(f"管理员升级用户等级 - 用户ID: {user_id}, 等级: {level}")
    
    valid_levels = ["青铜会员", "白银会员", "黄金会员"]
    if level not in valid_levels:
        raise HTTPException(status_code=400, detail=f"无效的用户等级，可选值: {', '.join(valid_levels)}")
    
    user = user_repo.update_user_level(db, user_id, level)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    db.commit()
    db.refresh(user)
    logger.info(f"升级成功 - 用户ID: {user_id}, 等级: {user.user_level}")
    
    return _convert_user_to_response(user)


def set_user_discount(db: Session, user_id: str, discount_rate: float) -> dict:
    logger.info(f"管理员设置用户折扣 - 用户ID: {user_id}, 折扣率: {discount_rate}")
    
    if discount_rate <= 0 or discount_rate > 1:
        raise HTTPException(status_code=400, detail="折扣率必须在0到1之间")
    
    user = user_repo.update_user_discount(db, user_id, discount_rate)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    db.commit()
    db.refresh(user)
    logger.info(f"设置折扣成功 - 用户ID: {user_id}, 折扣率: {user.discount_rate}")
    
    return _convert_user_to_response(user)


def update_user_profile(db: Session, user_id: str, nickname: str = None, phone: str = None,
                      email: str = None, gender: str = None, avatar: str = None) -> dict:
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
    
    db.commit()
    db.refresh(updated_user)
    logger.info(f"更新个人信息成功 - 用户ID: {user_id}")
    
    return _convert_user_to_response(updated_user)


def verify_pay_password(db: Session, user_id: str, password: str) -> bool:
    logger.debug(f"验证支付密码 - 用户ID: {user_id}")
    
    result = user_repo.get_user_pay_password(db, user_id)
    if not result:
        logger.warn(f"验证支付密码失败 - 用户不存在 - 用户ID: {user_id}")
        return False
    
    if not result["pay_password"]:
        logger.warn(f"验证支付密码失败 - 未设置支付密码 - 用户ID: {user_id}")
        return False
    
    if not verify_password(result["salt"], password, result["pay_password"]):
        logger.warn(f"验证支付密码失败 - 密码不正确 - 用户ID: {user_id}")
        return False
    
    logger.debug(f"支付密码验证成功 - 用户ID: {user_id}")
    return True


def check_balance_sufficient(db: Session, user_id: str, amount: float) -> bool:
    from decimal import Decimal
    logger.debug(f"检查余额 - 用户ID: {user_id}, 金额: {amount}")
    
    if amount <= 0:
        logger.warn(f"检查余额失败 - 金额必须大于0 - 用户ID: {user_id}, 金额: {amount}")
        return False
    
    balance = user_repo.get_user_balance(db, user_id)
    if balance is None:
        logger.warn(f"检查余额失败 - 用户不存在 - 用户ID: {user_id}")
        return False
    
    amount_decimal = Decimal(str(amount))
    balance_decimal = Decimal(str(balance))
    if balance_decimal < amount_decimal:
        logger.warn(f"检查余额失败 - 余额不足 - 用户ID: {user_id}, 余额: {balance}, 需要: {amount}")
        return False
    
    user_repo.update_balance(db, user_id, -float(amount_decimal))
    
    logger.debug(f"余额扣减成功 - 用户ID: {user_id}, 扣减金额: {amount}")
    return True


def update_user_points_and_level(user_id: str, points_add: int, db: Session) -> dict:
    """
    更新用户积分并升级会员等级
    规则：
    - 积分按原价/10计算
    - 1000积分 = 白银会员（95折）
    - 10000积分 = 黄金会员（9折）
    """
    logger.debug(f"更新用户积分 - 用户ID: {user_id}, 增加积分: {points_add}")
    
    # 获取用户当前信息
    user = user_repo.get_user_by_id(db, user_id)
    if not user:
        logger.warn(f"更新积分失败 - 用户不存在 - 用户ID: {user_id}")
        return {"success": False, "message": "用户不存在"}
    
    # 更新积分
    current_points = user.points or 0
    new_points = current_points + points_add
    user.points = new_points
    
    # 根据积分升级会员等级
    current_level = user.user_level
    current_discount = user.discount_rate
    
    if new_points >= 10000:
        new_level = "黄金会员"
        new_discount = 0.90
    elif new_points >= 1000:
        new_level = "白银会员"
        new_discount = 0.95
    else:
        new_level = "青铜会员"
        new_discount = 1.00
    
    # 更新等级和折扣
    user.user_level = new_level
    user.discount_rate = new_discount
    
    db.commit()
    
    logger.debug(f"积分更新成功 - 用户ID: {user_id}, 原积分: {current_points}, 新积分: {new_points}, 原等级: {current_level}, 新等级: {new_level}")
    
    return {
        "success": True,
        "message": "积分更新成功",
        "data": {
            "user_id": user_id,
            "points": new_points,
            "user_level": new_level,
            "discount_rate": new_discount
        }
    }
