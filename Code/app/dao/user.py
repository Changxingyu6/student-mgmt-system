"""
用户认证数据访问层
使用 SQLAlchemy ORM 进行用户相关数据库操作
"""
from sqlalchemy.orm import Session
from typing import Optional
from model.user import User


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """根据用户名获取用户"""
    return db.query(User).filter(User.username == username, User.is_active == True).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """根据ID获取用户"""
    return db.query(User).filter(User.id == user_id, User.is_active == True).first()


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