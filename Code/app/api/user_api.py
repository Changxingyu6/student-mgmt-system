"""
用户管理 API 路由
包含用户认证、用户管理等相关接口
"""
from fastapi import APIRouter, Request, Depends, Form, Body, HTTPException
from sqlalchemy.orm import Session
from services import user_service
from utils import format_response, require_roles
from database import get_db
from schema.user import *
from schema.role import UserRoleUpdateRequest

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.post("/login", summary="用户登录")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """用户登录获取token"""
    ip_address = request.client.host if request.client else ""
    user_agent = request.headers.get("User-Agent", "")
    result = user_service.login_for_access_token(username, password, db, ip_address, user_agent)
    return format_response(data=result, message="登录成功")


@router.post("/register", summary="用户注册")
def register_user(
    request: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    """注册新用户"""
    result = user_service.register_user(
        db, request.username, request.password,
        request.nickname, request.phone, request.email
    )
    return format_response(data=result, message="注册成功")


@router.get("/me", summary="获取当前用户信息")
def get_current_user_info(request: Request, db: Session = Depends(get_db)):
    """获取当前登录用户信息（所有角色都可访问）"""
    current_user = request.state.user
    result = user_service.get_user_by_id(db, current_user["id"])
    return format_response(data=result, message="获取成功")


@router.put("/me", summary="修改密码")
def update_current_user_password(
    request: Request,
    password_request: UserPasswordUpdateRequest = Body(...),
    db: Session = Depends(get_db)
):
    """更新当前登录用户密码（需要验证旧密码）"""
    current_user = request.state.user
    result = user_service.update_user_password(
        db, current_user["id"], password_request.old_password, password_request.new_password
    )
    return format_response(data=result, message="密码修改成功")


@router.put("/me/profile", summary="更新个人信息")
def update_current_user_profile(
    request: Request,
    profile_request: UserProfileUpdateRequest = Body(...),
    db: Session = Depends(get_db)
):
    """更新当前登录用户个人信息"""
    current_user = request.state.user
    result = user_service.update_user_profile(
        db, current_user["id"],
        profile_request.nickname,
        profile_request.phone,
        profile_request.email,
        profile_request.gender,
        profile_request.avatar
    )
    return format_response(data=result, message="更新成功")


@router.get("", summary="获取用户列表")
@require_roles(["admin"])
def get_users(
    request: Request,
    db: Session = Depends(get_db),
    page: int = 1,
    limit: int = 10
):
    """获取用户列表（仅管理员可访问）"""
    data = user_service.get_all_users(db, page, limit)
    return format_response(data=data)


@router.get("/{user_id}", summary="获取用户详情")
@require_roles(["admin"])
def get_user_detail(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db)
):
    """获取指定用户详情（仅管理员可访问）"""
    result = user_service.get_user_by_id(db, user_id)
    return format_response(data=result, message="获取成功")


@router.post("", summary="创建用户")
@require_roles(["admin"])
def create_user(
    request: Request,
    user_request: UserCreateRequest = Body(...),
    db: Session = Depends(get_db)
):
    """创建新用户（仅管理员可访问）"""
    result = user_service.create_user(
        db,
        user_request.username,
        user_request.password,
        user_request.nickname,
        user_request.phone,
        user_request.email,
        user_request.user_level,
        user_request.balance,
        user_request.status
    )
    return format_response(data=result, message="创建成功")


@router.put("/{user_id}", summary="更新用户信息")
@require_roles(["admin"])
def update_user(
    request: Request,
    user_id: int,
    user_request: UserUpdateRequest = Body(...),
    db: Session = Depends(get_db)
):
    """更新用户信息（仅管理员可访问）"""
    result = user_service.update_user(
        db, user_id,
        user_request.nickname,
        user_request.phone,
        user_request.email,
        user_request.user_level,
        user_request.status
    )
    return format_response(data=result, message="更新成功")


@router.delete("/{user_id}", summary="删除用户")
@require_roles(["admin"])
def delete_user(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db)
):
    """删除用户（仅管理员可访问，逻辑删除）"""
    result = user_service.delete_user(db, user_id)
    return format_response(data=result, message="删除成功")


@router.get("/locked", summary="获取锁定用户列表")
@require_roles(["admin"])
def get_locked_users(
    request: Request,
    db: Session = Depends(get_db)
):
    """获取被锁定的用户列表（仅管理员可访问）"""
    data = user_service.get_locked_users(db)
    return format_response(data=data, message="获取成功")


@router.post("/{user_id}/unlock", summary="解锁用户")
@require_roles(["admin"])
def unlock_user(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db)
):
    """解锁用户账户（仅管理员可访问）"""
    data = user_service.unlock_user_account(db, user_id)
    return format_response(data=data, message="解锁成功")


@router.post("/{user_id}/freeze", summary="冻结用户")
@require_roles(["admin"])
def freeze_user(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db)
):
    """冻结用户账户（仅管理员可访问）"""
    data = user_service.freeze_user(db, user_id)
    return format_response(data=data, message="冻结成功")


@router.post("/{user_id}/unfreeze", summary="解冻用户")
@require_roles(["admin"])
def unfreeze_user(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db)
):
    """解冻用户账户（仅管理员可访问）"""
    data = user_service.unfreeze_user(db, user_id)
    return format_response(data=data, message="解冻成功")


@router.post("/{user_id}/recharge", summary="充值余额")
@require_roles(["admin"])
def recharge_balance(
    request: Request,
    user_id: int,
    balance_request: BalanceOperationRequest = Body(...),
    db: Session = Depends(get_db)
):
    """为用户充值余额（仅管理员可访问）"""
    result = user_service.recharge_balance(
        db, user_id, balance_request.amount, balance_request.reason
    )
    return format_response(data=result, message="充值成功")


@router.post("/{user_id}/role", summary="修改用户角色")
@require_roles()  # 只有 admin 能访问
def update_user_role(
    request: Request,
    user_id: int,
    role_request: UserRoleUpdateRequest = Body(...),
    db: Session = Depends(get_db)
):
    """修改用户角色（仅管理员可访问）"""
    from services import role_service
    try:
        success = role_service.update_user_role(db, user_id, role_request.role_id)
        if success:
            return format_response(message="角色修改成功")
        else:
            raise HTTPException(status_code=400, detail="角色修改失败")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))