# API 路由模块
# 导入并导出所有路由

from .user_api import router as user_api_router
from .role_api import router as role_api_router
from .address_api import router as address_api_router
from .log_api import router as log_api_router
from .ai_api import router as ai_api_router
from .data_analysis_api import router as data_router
from .shopping_cart_api import router as shopping_cart
from .coupon_api import router as coupon_api_router
from .goods_api import goods_router
from .pay_api import router as pay_api_router
from .refund_api import router as refund_api_router
from .logistics_api import router as logistics_api_router
from .return_logistics_api import router as return_logistics_api_router


# 统一导出所有路由
__all__ = [
    "user_api_router",
    "role_api_router",
    "address_api_router",
    "log_api_router",
    "ai_api_router",
    "data_router",
    "shopping_cart",
    "pay_api_router",
    "refund_api_router",
    "logistics_api_router",
    "return_logistics_api_router"
]

