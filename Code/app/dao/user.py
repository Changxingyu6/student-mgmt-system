"""
用户认证数据访问层
使用 SQLAlchemy ORM 进行用户相关数据库操作
"""
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from model.user import User


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """根据用户名获取用户（包含锁定状态检查）"""
    return db.query(User).filter(User.username == username, User.is_active == True).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """根据ID获取用户"""
    return db.query(User).filter(User.id == user_id, User.is_active == True).first()


def get_user_with_lock_status(db: Session, username: str) -> Optional[User]:
    """获取用户（包含锁定状态）"""
    return db.query(User).filter(User.username == username, User.is_active == True).first()


def create_user(db: Session, username: str, hashed_password: str, salt: str, role: str, related_id: int = None) -> User:
    """创建用户"""
    db_user = User(
        username=username,
        password=hashed_password,
        salt=salt,
        role=role,
        related_id=related_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, username: str = None, password: str = None, salt: str = None) -> Optional[User]:
    """更新用户信息"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    if username:
        db_user.username = username
    if password:
        db_user.password = password
    if salt:
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
    
    # 增加锁定次数
    db_user.lock_count = (db_user.lock_count or 0) + 1
    # 计算锁定截止时间（转换为 datetime 对象）
    lock_timestamp = datetime.now().timestamp() + lock_minutes * 60
    db_user.lock_until = datetime.fromtimestamp(lock_timestamp)
    db.commit()
    db.refresh(db_user)
    return True


def unlock_user(db: Session, user_id: int) -> Optional[User]:
    """解锁用户账户"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    db_user.failed_attempts = 0
    db_user.lock_until = None
    # 解锁时保留 lock_count，以便下次锁定仍按阶梯计算
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
    return db.query(User).filter(User.is_active == True).offset(offset).limit(limit).all()


def get_locked_users(db: Session) -> List[User]:
    """获取所有被锁定的用户"""
    now = datetime.now()
    return db.query(User).filter(
        User.is_active == True,
        User.lock_until.isnot(None),
        User.lock_until > now
    ).all()


def count_users(db: Session) -> int:
    """统计用户总数"""
    return db.query(User).filter(User.is_active == True).count()