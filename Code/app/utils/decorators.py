"""
权限装饰器
提供方法级角色权限控制
"""
from functools import wraps
from fastapi import HTTPException, status, Request


def require_roles(allowed_roles: list):
    """
    角色权限装饰器（从中间件获取用户信息）

    使用示例：
    @router.get("/students")
    @require_roles(["admin", "teacher"])
    def get_students(request: Request):
        ...

    Args:
        allowed_roles: 允许访问的角色列表，如 ["admin", "teacher"]
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, request: Request = None, **kwargs):
            # 1. 检查 request 对象是否存在
            if request is None:
                # 尝试从参数中获取 request
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break

                if request is None:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="请求对象不存在"
                    )

            # 2. 获取当前用户信息（从中间件设置的 request.state）
            current_user = getattr(request.state, 'user', None)

            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="未认证，请先登录"
                )

            # 3. 检查用户角色权限
            user_role = current_user.get("role", "")

            if user_role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"权限不足，需要角色: {', '.join(allowed_roles)}"
                )

            # 4. 执行原函数
            return func(*args, request=request, **kwargs)

        return wrapper

    return decorator
