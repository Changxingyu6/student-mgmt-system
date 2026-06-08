"""
用户管理 API 路由
包含用户认证、用户管理等相关接口
"""
from fastapi import APIRouter, Request, Depends, Form
from sqlalchemy.orm import Session
from services import user as user_service
from utils import format_response, require_roles
from database import get_db

# 用户管理路由
router = APIRouter(prefix="/users", tags=["用户管理"])


# ===== 认证相关 =====

@router.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """用户登录"""
    ip_address = request.client.host if request.client else ""
    user_agent = request.headers.get("User-Agent", "")
    result = user_service.login_for_access_token(username, password, db, ip_address, user_agent)
    return format_response(data=result, message="登录成功")


@router.post("/register")
def register_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    related_id: int = Form(None),
    db: Session = Depends(get_db)
):
    """注册新用户（仅限管理员使用，实际使用时应添加权限验证）"""
    result = user_service.register_user(db, username, password, role, related_id)
    return format_response(data=result, message="注册成功")


@router.get("/me")
def get_current_user_info(request: Request, db: Session = Depends(get_db)):
    """获取当前登录用户信息（所有角色都可访问）"""
    current_user = request.state.user
    # 从数据库获取完整用户信息
    db_user = user_repo.get_user_by_id(db, current_user["id"])
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 检查是否被锁定
    is_locked = False
    if db_user.lock_until:
        now = datetime.now()
        if db_user.lock_until > now:
            is_locked = True
    
    user_info = {
        "id": db_user.id,
        "username": db_user.username,
        "role": db_user.role,
        "related_id": db_user.related_id,
        "is_active": db_user.is_active,
        "is_locked": is_locked,
        "failed_attempts": db_user.failed_attempts or 0,
        "lock_count": db_user.lock_count or 0
    }
    return format_response(data=user_info, message="获取成功")


@router.put("/me")
def update_current_user_info(
    request: Request,
    old_password: str = Form(...),
    new_password: str = Form(...),
    db: Session = Depends(get_db)
):
    """更新当前登录用户密码（所有角色都可修改，需要验证旧密码）"""
    current_user = request.state.user
    result = user_service.update_user_password(db, current_user["id"], old_password, new_password)
    return format_response(data=result, message="密码修改成功")


# ===== 管理相关 =====

@router.get("")
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


@router.get("/locked")
@require_roles(["admin"])
def get_locked_users(
    request: Request,
    db: Session = Depends(get_db)
):
    """获取被锁定的用户列表（仅管理员可访问）"""
    data = user_service.get_locked_users(db)
    return format_response(data=data, message="获取成功")


@router.post("/{user_id}/unlock")
@require_roles(["admin"])
def unlock_user(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db)
):
    """解锁用户账户（仅管理员可访问）"""
    data = user_service.unlock_user_account(db, user_id)
    return format_response(data=data, message="解锁成功")
