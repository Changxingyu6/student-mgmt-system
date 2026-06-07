# API 路由模块
# 导入并导出所有路由

from .students import router as students_router
from .auth import router as auth_router
from .ai import router as ai_router

# 统一导出所有路由
__all__ = ["students_router", "auth_router", "ai_router"]