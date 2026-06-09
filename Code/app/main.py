import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from fastapi import HTTPException
from api import user_api_router, role_api_router, address_api_router, log_api_router, ai_api_router, data_router, shopping_cart,coupon_api_router,goods_router
from utils.jwt_utils import decode_access_token
from utils.logger import get_logger

# 初始化日志系统
logger = get_logger("main")

# 白名单：不需要 Token 认证的路径
WHITELIST = [
    "/users/login",
    "/users/register",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/data-analysis/users/weekly"
    "/goods"
]


# 创建 FastAPI 实例
app = FastAPI(
    title="电商管理平台 API",
    description="基于 FastAPI 的电商管理平台，使用 SQLAlchemy 进行数据库操作，采用三层架构",
    version="1.0.0"
)


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """
    JWT 认证中间件
    对非白名单路径进行 Token 验证
    """
    start_time = time.time()
    
    # 1. 检查是否在白名单中（前缀匹配）
    if any(request.url.path.startswith(path) for path in WHITELIST):
        response = await call_next(request)
        return response

    response = await call_next(request)
    return response

    # 2. 获取 Token
    token = None
    if "Authorization" in request.headers:
        auth_header = request.headers["Authorization"]
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
    
    if not token:
        return JSONResponse(
            status_code=401,
            content={"code": 401, "message": "未授权，请先登录", "data": None}
        )
    
    # 3. 验证 Token
    try:
        payload = decode_access_token(token)
        if payload is None:
            return JSONResponse(
                status_code=401,
                content={"code": 401, "message": "Token 无效或已过期", "data": None}
            )
        
        # 将用户信息存入 request.state
        request.state.user = {
            "id": payload.get("user_id"),
            "username": payload.get("username"),
            "role": payload.get("role", "user")
        }
        
    except Exception as e:
        logger.error(f"Token 验证失败: {str(e)}")
        return JSONResponse(
            status_code=401,
            content={"code": 401, "message": "Token 验证失败", "data": None}
        )
    
    # 4. 继续处理请求
    response = await call_next(request)
    return response


# ===== CORS 跨域 =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== 注册路由 =====
app.include_router(user_api_router)
app.include_router(role_api_router)
app.include_router(address_api_router)
app.include_router(log_api_router)
app.include_router(ai_api_router)
app.include_router(data_router)
app.include_router(shopping_cart)
app.include_router(goods_router)

if __name__ == "__main__":
    import uvicorn
    from dotenv import load_dotenv
    import os

    load_dotenv()

    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "localhost"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("DEBUG", "false").lower() == "true"
    )
