# API 路由模块
# 导入并导出所有路由

from .user_api import router as user_api_router
from .role_api import router as role_api_router
from .address_api import router as address_api_router
from .log_api import router as log_api_router
from .ai_api import router as ai_api_router

# 统一导出所有路由
__all__ = ["user_api_router", "role_api_router", "address_api_router", "log_api_router", "ai_api_router"]