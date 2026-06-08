"""
权限装饰器
提供方法级角色权限控制

使用规则：
- 不写装饰器：所有已认证用户都能访问
- @require_roles()：只有 admin 能访问
- @require_roles(["manager"])：admin + manager
- @require_roles(["user"])：admin + user
- @require_roles(["user", "manager"])：admin + manager + user
"""
from functools import wraps
from fastapi import HTTPException, status, Request


def require_roles(allowed_roles: list = None):
    """
    角色权限装饰器（从中间件获取用户信息）

    使用示例：
    @router.get("/users")                    # 所有已认证用户
    @router.get("/users")
    @require_roles()                         # 只有 admin
    @router.get("/users")
    @require_roles(["manager"])              # admin + manager
    @router.get("/users")
    @require_roles(["user", "manager"])      # admin + manager + user

    Args:
        allowed_roles: 允许访问的角色列表，不传或传空列表时只有 admin 能访问
    """
    # 如果不传参数，默认只有 admin 能访问
    if allowed_roles is None:
        allowed_roles = []

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

            # 3. 获取用户角色
            user_role = current_user.get("role", "")

            # 4. admin 默认拥有所有权限
            if user_role == "admin":
                return func(*args, request=request, **kwargs)

            # 5. 如果装饰器不传参数（allowed_roles 为空），只有 admin 能访问
            if not allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="权限不足，需要管理员权限"
                )

            # 6. 检查用户角色是否在允许列表中
            if user_role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"权限不足，需要角色: {', '.join(allowed_roles)}"
                )

            # 7. 执行原函数
            return func(*args, request=request, **kwargs)

        return wrapper

    return decorator
