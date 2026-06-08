"""
用户认证数据访问层
使用 SQLAlchemy ORM 进行用户相关数据库操作
"""
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from model.user import User
from utils.uuid_utils import generate_uuid


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """根据用户名获取用户"""
    return db.query(User).filter(User.username == username, User.is_deleted == False).first()


def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    """根据ID获取用户"""
    return db.query(User).filter(User.id == user_id, User.is_deleted == False).first()


def get_user_with_lock_status(db: Session, username: str) -> Optional[User]:
    """获取用户（包含锁定状态）"""
    return db.query(User).filter(User.username == username, User.is_deleted == False).first()


def create_user(db: Session, username: str, hashed_password: str, salt: str, 
               nickname: str = None, phone: str = None, email: str = None,
               user_level: str = "青铜会员", balance: float = 0.00, 
               status: str = "active") -> User:
    """创建用户"""
    db_user = User(
        id=generate_uuid(),
        username=username,
        password=hashed_password,
        salt=salt,
        nickname=nickname,
        phone=phone,
        email=email,
        user_level=user_level,
        balance=balance,
        status=status
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: str, **kwargs) -> Optional[User]:
    """更新用户信息"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    for key, value in kwargs.items():
        if hasattr(db_user, key) and value is not None:
            setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_password(db: Session, user_id: str, hashed_password: str, salt: str) -> Optional[User]:
    """更新用户密码"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    db_user.password = hashed_password
    db_user.salt = salt
    db.commit()
    db.refresh(db_user)
    return db_user


def increment_failed_attempts(db: Session, username: str) -> bool:
    """增加登录失败次数"""
    db_user = get_user_with_lock_status(db, username)
    if not db_user:
        return False
    
    db_user.failed_attempts = (db_user.failed_attempts or 0) + 1
    db.commit()
    db.refresh(db_user)
    return True


def reset_failed_attempts(db: Session, username: str) -> bool:
    """重置登录失败次数"""
    db_user = get_user_with_lock_status(db, username)
    if not db_user:
        return False
    
    db_user.failed_attempts = 0
    db_user.lock_until = None
    db.commit()
    db.refresh(db_user)
    return True


def lock_user(db: Session, username: str, lock_minutes: int = 15) -> bool:
    """锁定用户账户"""
    db_user = get_user_with_lock_status(db, username)
    if not db_user:
        return False
    
    db_user.lock_count = (db_user.lock_count or 0) + 1
    db_user.lock_until = datetime.now() + datetime.timedelta(minutes=lock_minutes)
    db.commit()
    db.refresh(db_user)
    return True


def unlock_user(db: Session, user_id: str) -> Optional[User]:
    """解锁用户账户"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    db_user.failed_attempts = 0
    db_user.lock_until = None
    db.commit()
    db.refresh(db_user)
    return db_user


def reset_lock_count(db: Session, username: str) -> bool:
    """重置锁定次数（登录成功后调用）"""
    db_user = get_user_with_lock_status(db, username)
    if not db_user:
        return False
    
    db_user.lock_count = 0
    db.commit()
    db.refresh(db_user)
    return True


def get_all_users(db: Session, page: int = 1, limit: int = 10) -> List[User]:
    """获取所有用户列表（管理员用）"""
    offset = (page - 1) * limit
    return db.query(User).filter(User.is_deleted == False).order_by(User.created_at.desc()).offset(offset).limit(limit).all()


def get_locked_users(db: Session) -> List[User]:
    """获取所有被锁定的用户"""
    now = datetime.now()
    return db.query(User).filter(
        User.is_deleted == False,
        User.lock_until.isnot(None),
        User.lock_until > now
    ).all()


def count_users(db: Session) -> int:
    """统计用户总数"""
    return db.query(User).filter(User.is_deleted == False).count()


def delete_user(db: Session, user_id: str) -> bool:
    """逻辑删除用户"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return False
    
    db_user.is_deleted = True
    db.commit()
    return True


def freeze_user(db: Session, user_id: str) -> Optional[User]:
    """冻结用户账户"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    db_user.status = "inactive"
    db.commit()
    db.refresh(db_user)
    return db_user


def unfreeze_user(db: Session, user_id: str) -> Optional[User]:
    """解冻用户账户"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    db_user.status = "active"
    db.commit()
    db.refresh(db_user)
    return db_user


def update_balance(db: Session, user_id: str, amount: float) -> Optional[User]:
    """更新用户余额"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    db_user.balance = (db_user.balance or 0) + amount
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_level(db: Session, user_id: str, level: str) -> Optional[User]:
    """更新用户等级"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    db_user.user_level = level
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_discount(db: Session, user_id: str, discount_rate: float, expire_at: datetime = None) -> Optional[User]:
    """更新用户折扣"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    db_user.discount_rate = discount_rate
    db_user.discount_expire_at = expire_at
    db.commit()
    db.refresh(db_user)
    return db_user


def check_username_exists(db: Session, username: str) -> bool:
    """检查用户名是否存在"""
    return db.query(User).filter(User.username == username, User.is_deleted == False).first() is not None


def get_user_pay_password(db: Session, user_id: str) -> Optional[dict]:
    """获取用户支付密码和盐值"""
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    if not user:
        return None
    return {
        "pay_password": user.pay_password,
        "salt": user.salt
    }


def get_user_balance(db: Session, user_id: str) -> Optional[float]:
    """获取用户余额"""
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    if not user:
        return None
    return float(user.balance or 0)


def update_pay_password(db: Session, user_id: str, hashed_password: str) -> Optional[User]:
    """更新用户支付密码"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    db_user.pay_password = hashed_password
    db.commit()
    db.refresh(db_user)
    return db_user