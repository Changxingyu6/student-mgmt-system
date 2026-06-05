# API 路由模块
# 导入并导出所有路由

from .students import router as students_router
from .auth import public_router as auth_public_router, protected_router as auth_protected_router

# 统一导出所有路由
__all__ = ["students_router", "auth_public_router", "auth_protected_router"]