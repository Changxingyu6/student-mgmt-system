"""
依赖注入模块
定义所有 API 路由需要的依赖
"""
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from services import auth as auth_service


def get_current_user(
    authorization: str = Header(None, description="认证令牌，格式：Bearer <token>"),
    db: Session = Depends(get_db),
) -> dict:
    """
    获取当前用户（Token 校验依赖）
    从请求头中提取 Authorization: Bearer <token>
    验证 token 并返回用户信息
    """
    # 1. 检查是否提供了 Authorization 头
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 2. 检查 token 格式
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="认证令牌格式错误，应为：Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = authorization[7:]  # 去掉 "Bearer " 前缀
    
    # 3. 验证 token 并获取用户信息（使用 Service 层）
    try:
        user = auth_service.get_current_user(token, db)
        return user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="认证令牌无效或已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )
