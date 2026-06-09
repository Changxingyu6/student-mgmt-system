"""
角色数据访问层
提供角色相关的数据库操作
"""
from sqlalchemy.orm import Session
from typing import Optional, List
from model.role import Role
from model.user import User
from utils.uuid_utils import generate_uuid


def get_role_by_id(db: Session, role_id: str) -> Optional[Role]:
    """根据ID获取角色"""
    return db.query(Role).filter(Role.id == role_id, Role.status == 'active').first()


def get_role_by_name(db: Session, role_name: str) -> Optional[Role]:
    """根据名称获取角色"""
    return db.query(Role).filter(Role.role_name == role_name, Role.status == 'active').first()


def get_all_roles(db: Session) -> List[Role]:
    """获取所有角色"""
    return db.query(Role).filter(Role.status == 'active').all()


def create_role(db: Session, role_name: str, description: str = None) -> Role:
    """创建角色"""
    role = Role(id=generate_uuid(), role_name=role_name, description=description)
    db.add(role)
    return role


def update_role(db: Session, role_id: str, role_name: str = None, description: str = None, status: str = None) -> Optional[Role]:
    """更新角色信息"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if role:
        if role_name:
            role.role_name = role_name
        if description:
            role.description = description
        if status:
            role.status = status
    return role


def delete_role(db: Session, role_id: str) -> bool:
    """删除角色（逻辑删除）"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if role:
        role.status = 'inactive'
        return True
    return False


def get_users_by_role(db: Session, role_id: str) -> List[User]:
    """获取指定角色的所有用户"""
    return db.query(User).filter(User.role_id == role_id, User.is_deleted == False).all()


def count_users_by_role(db: Session, role_id: str) -> int:
    """统计指定角色的用户数量"""
    return db.query(User).filter(User.role_id == role_id, User.is_deleted == False).count()