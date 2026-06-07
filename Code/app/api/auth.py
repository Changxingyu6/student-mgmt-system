"""
用户认证 API 路由
包含登录、注册、查看/修改个人信息等接口
"""
from fastapi import APIRouter, HTTPException, status, Form, Request, Depends
from sqlalchemy.orm import Session
from database import get_db
from services import auth as auth_service
from utils import format_response

router = APIRouter(prefix="/auth", tags=["用户认证"])


@router.post("/login")
def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """用户登录"""
    result = auth_service.login_for_access_token(username, password, db)
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
    result = auth_service.register_user(db, username, password, role, related_id)
    return format_response(data=result, message="注册成功")


# ===== 受保护路由（需要认证）=====

@router.get("/me")
def get_current_user_info(request: Request):
    """获取当前登录用户信息（所有角色都可访问）"""
    # 直接使用中间件存储的用户信息
    current_user = request.state.user
    return format_response(data=current_user, message="获取成功")


@router.put("/me")
def update_current_user_info(
    request: Request,
    old_password: str = Form(...),
    new_password: str = Form(...),
    db: Session = Depends(get_db)
):
    """更新当前登录用户密码（所有角色都可修改，需要验证旧密码）"""
    # 直接使用中间件存储的用户信息
    current_user = request.state.user
    
    # 调用服务层进行密码修改（包含旧密码验证）
    result = auth_service.update_user_password(db, current_user["id"], old_password, new_password)
    return format_response(data=result, message="密码修改成功")