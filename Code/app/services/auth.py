"""
用户认证业务逻辑层
负责用户登录、密码验证、JWT生成等认证相关业务
"""
from sqlalchemy.orm import Session
from typing import Optional
from fastapi import HTTPException, status
from dao import user as user_repo
from utils import generate_salt, md5_hash, verify_password, create_access_token


def authenticate_user(
    username: str, 
    password: str, 
    db: Session
) -> Optional[dict]:
    """验证用户身份"""
    user = user_repo.get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(user.salt, password, user.password):
        return None
    
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
    db: Session
) -> dict:
    """用户登录获取token"""
    user = authenticate_user(username, password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={
            "sub": str(user["id"]),           # 标准声明：用户ID（字符串格式）
            "username": user["username"],      # 自定义声明：用户名
            "roles": [user["role"]],           # 自定义声明：用户角色列表
            "user_id": user["id"]              # 自定义声明：用户ID（整数格式）
        }
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
    # 获取用户信息
    user = user_repo.get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 验证旧密码
    if not verify_password(user.salt, old_password, user.password):
        raise HTTPException(status_code=400, detail="旧密码不正确")
    
    # 生成新的salt和加密密码
    new_salt = generate_salt()
    hashed_new_password = md5_hash(new_salt, new_password)
    
    # 更新密码
    updated_user = user_repo.update_user(db, user_id, password=hashed_new_password, salt=new_salt)
    
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
    # 检查用户名是否已存在
    existing_user = user_repo.get_user_by_username(db, username)
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 生成salt并加密密码
    salt = generate_salt()
    hashed_password = md5_hash(salt, password)
    
    # 创建用户
    new_user = user_repo.create_user(db, username, hashed_password, salt, role, related_id)
    
    return {
        "id": new_user.id,
        "username": new_user.username,
        "role": new_user.role,
        "related_id": new_user.related_id
    }