# API 路由模块
# 导入并导出所有路由

from .students import router as students_router
from .ai import router as ai_router
from .users import router as users_router

# 统一导出所有路由
__all__ = ["students_router", "ai_router", "users_router"]