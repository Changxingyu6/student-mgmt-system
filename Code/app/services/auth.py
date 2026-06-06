"""
用户认证业务逻辑层
负责用户登录、密码验证、JWT生成等认证相关业务
"""
from sqlalchemy.orm import Session
from typing import Optional
from fastapi import HTTPException, status, Depends
from datetime import timedelta
import jwt
from dotenv import load_dotenv
import os
from pathlib import Path
from dao import user as user_repo
from database import get_db
from utils import generate_salt, md5_hash, verify_password, create_access_token, decode_access_token

# 获取当前文件所在目录（services/）
SERVICE_DIR = Path(__file__).resolve().parent

# 加载环境变量（从 app/.env 文件）
load_dotenv(SERVICE_DIR.parent / ".env")

# JWT 设置
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


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
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(user["id"]),           # 标准声明：用户ID（字符串格式）
            "username": user["username"],      # 自定义声明：用户名
            "roles": [user["role"]],           # 自定义声明：用户角色列表
            "user_id": user["id"]              # 自定义声明：用户ID（整数格式）
        },
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


def get_current_user(
    token: str, 
    db: Session
) -> dict:
    """从token获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_access_token(token)
        user_id_str: str = payload.get("sub")     # 标准声明：用户ID（字符串）
        username: str = payload.get("username")   # 自定义声明：用户名
        roles: list = payload.get("roles", [])    # 自定义声明：角色列表
        user_id: int = payload.get("user_id")     # 自定义声明：用户ID（整数）
        
        # 获取角色（取第一个角色）
        role: str = roles[0] if roles else ""
        
        if user_id_str is None or user_id is None:
            raise credentials_exception
        
        # 验证用户是否存在
        user = user_repo.get_user_by_id(db, user_id)
        if user is None:
            raise credentials_exception
        
        return {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "related_id": user.related_id
        }
    except jwt.InvalidTokenError:
        raise credentials_exception


def update_user_info(
    user_id: int, 
    username: str = None, 
    password: str = None, 
    db: Session = Depends(get_db)
) -> dict:
    """更新用户信息"""
    update_data = {}
    if username:
        update_data["username"] = username
    if password:
        # 生成新的salt和加密密码
        salt = generate_salt()
        update_data["password"] = md5_hash(salt, password)
        update_data["salt"] = salt
    
    updated_user = user_repo.update_user(db, user_id, **update_data)
    
    if not updated_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return {
        "id": updated_user.id,
        "username": updated_user.username,
        "role": updated_user.role,
        "related_id": updated_user.related_id
    }


def register_user(
    username: str, 
    password: str, 
    role: str = "student", 
    related_id: int = None,
    db: Session = Depends(get_db)
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