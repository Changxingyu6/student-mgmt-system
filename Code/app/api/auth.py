"""
用户认证 API 路由
包含登录、注册、查看/修改个人信息等接口
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Optional
from deps import get_current_user
from services import auth as auth_service
from utils import format_response

# 公开路由（无需认证）
public_router = APIRouter(prefix="/auth", tags=["用户认证"])

# 受保护路由（需要认证）
protected_router = APIRouter(prefix="/auth", tags=["用户认证"], dependencies=[Depends(get_current_user)])


# ===== 公开路由（无需认证）=====

@public_router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    result = Depends(auth_service.login_for_access_token)
):
    """用户登录"""
    return format_response(data=result, message="登录成功")


@public_router.post("/register")
def register_user(
    new_user = Depends(auth_service.register_user)
):
    """注册新用户（仅限管理员使用，实际使用时应添加权限验证）"""
    return format_response(data=new_user, message="注册成功")


# ===== 受保护路由（需要认证）=====

@protected_router.get("/me")
def get_current_user_info(
    current_user: dict = Depends(get_current_user)
):
    """获取当前登录用户信息（所有角色都可访问）"""
    return format_response(data=current_user, message="获取成功")


@protected_router.put("/me")
def update_current_user_info(
    updated_user = Depends(auth_service.update_user_info)
):
    """更新当前登录用户信息（所有角色都可修改个人信息）"""
    return format_response(data=updated_user, message="更新成功")