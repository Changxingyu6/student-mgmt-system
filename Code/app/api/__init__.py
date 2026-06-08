# API 路由模块
# 导入并导出所有路由

from .ai import router as ai_router
from .users import router as users_router
from .logs import router as logs_router

# 统一导出所有路由
__all__ = ["ai_router", "users_router", "logs_router"]