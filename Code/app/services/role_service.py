"""
角色业务逻辑层
提供角色管理的业务逻辑
"""
from sqlalchemy.orm import Session
from typing import Optional, List
from dao import role_dao as role_repo
from model.role import Role
from model.user import User
from schema.role import RoleResponse, RoleListResponse, RoleCreateRequest, RoleUpdateRequest


def _convert_role_to_response(role: Role) -> RoleResponse:
    """将角色模型转换为响应对象"""
    return RoleResponse(
        id=role.id,
        role_name=role.role_name,
        description=role.description,
        status=role.status,
        create_time=role.create_time,
        update_time=role.update_time
    )


def get_role_by_id(db: Session, role_id: int) -> Optional[RoleResponse]:
    """根据ID获取角色"""
    role = role_repo.get_role_by_id(db, role_id)
    if role:
        return _convert_role_to_response(role)
    return None


def get_role_by_name(db: Session, role_name: str) -> Optional[RoleResponse]:
    """根据名称获取角色"""
    role = role_repo.get_role_by_name(db, role_name)
    if role:
        return _convert_role_to_response(role)
    return None


def get_all_roles(db: Session) -> RoleListResponse:
    """获取所有角色"""
    roles = role_repo.get_all_roles(db)
    items = [_convert_role_to_response(role) for role in roles]
    return RoleListResponse(total=len(items), items=items)


def create_role(db: Session, request: RoleCreateRequest) -> RoleResponse:
    """创建角色"""
    # 检查角色名称是否已存在
    existing_role = role_repo.get_role_by_name(db, request.role_name)
    if existing_role:
        raise ValueError(f"角色名称 '{request.role_name}' 已存在")
    
    role = role_repo.create_role(db, request.role_name, request.description)
    return _convert_role_to_response(role)


def update_role(db: Session, role_id: int, request: RoleUpdateRequest) -> Optional[RoleResponse]:
    """更新角色信息"""
    # 检查角色是否存在
    role = role_repo.get_role_by_id(db, role_id)
    if not role:
        raise ValueError("角色不存在")
    
    # 如果修改角色名称，检查是否已存在
    if request.role_name and request.role_name != role.role_name:
        existing_role = role_repo.get_role_by_name(db, request.role_name)
        if existing_role:
            raise ValueError(f"角色名称 '{request.role_name}' 已存在")
    
    updated_role = role_repo.update_role(
        db, role_id,
        role_name=request.role_name,
        description=request.description,
        status=request.status
    )
    
    if updated_role:
        return _convert_role_to_response(updated_role)
    return None


def delete_role(db: Session, role_id: int) -> bool:
    """删除角色"""
    # 检查角色是否存在
    role = role_repo.get_role_by_id(db, role_id)
    if not role:
        raise ValueError("角色不存在")
    
    # 检查是否有用户使用该角色
    user_count = role_repo.count_users_by_role(db, role_id)
    if user_count > 0:
        raise ValueError(f"该角色下有 {user_count} 个用户，无法删除")
    
    return role_repo.delete_role(db, role_id)


def get_users_by_role(db: Session, role_id: int) -> List[User]:
    """获取指定角色的所有用户"""
    return role_repo.get_users_by_role(db, role_id)


def update_user_role(db: Session, user_id: int, role_id: int) -> bool:
    """更新用户角色"""
    from dao import user_dao as user_repo

    # 检查用户是否存在
    user = user_repo.get_user_by_id(db, user_id)
    if not user:
        raise ValueError("用户不存在")
    
    # 检查角色是否存在
    role = role_repo.get_role_by_id(db, role_id)
    if not role:
        raise ValueError("角色不存在")
    
    user.role_id = role_id
    db.commit()
    db.refresh(user)
    return True


def get_user_role(db: Session, user_id: str) -> Optional[str]:
    """获取用户角色名称"""
    from dao.user_dao import get_user_by_id
    
    user = get_user_by_id(db, user_id)
    if user and user.role:
        return user.role.role_name
    return None
