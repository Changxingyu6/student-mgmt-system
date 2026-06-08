import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from fastapi import HTTPException
from api import ai_router, users_router, logs_router, addresses_router
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
]


# 创建 FastAPI 实例
app = FastAPI(
    title="电商管理平台 API",
    description="基于 FastAPI 的电商管理平台，使用 SQLAlchemy 进行数据库操作，采用三层架构",
    version="1.0.0"
)


# ===== 请求日志中间件 =====
@app.middleware('http')
async def log_middleware(request: Request, call_next):
    """请求日志中间件：记录所有 HTTP 请求信息"""
    # 记录请求开始时间
    start_time = time.time()
    
    # 获取请求信息
    method = request.method
    path = request.url.path
    query_params = str(request.url.query) if request.url.query else ""
    client_ip = request.client.host if request.client else "unknown"
    
    # 记录请求开始
    logger.info(f"请求开始 - IP: {client_ip} - {method} {path}{'?' + query_params if query_params else ''}")
    
    # 继续处理请求
    try:
        response = await call_next(request)
        
        # 计算耗时
        duration = (time.time() - start_time) * 1000
        
        # 记录请求结束
        logger.info(f"请求结束 - IP: {client_ip} - {method} {path} - 状态码: {response.status_code} - 耗时: {duration:.2f}ms")
        
        return response
    except Exception as e:
        # 记录异常
        duration = (time.time() - start_time) * 1000
        logger.error(f"请求异常 - IP: {client_ip} - {method} {path} - 异常: {str(e)} - 耗时: {duration:.2f}ms")
        raise


# ===== 认证中间件 =====
@app.middleware('http')
async def auth_middleware(request: Request, call_next):
    """全局认证中间件：白名单跳过，其他路径验证 Token 并存储用户信息"""
    path = request.url.path
    
    # 1. 检查是否在白名单中
    if any(path.startswith(w) for w in WHITELIST):
        return await call_next(request)
    
    # 2. 获取 Token
    auth_header = request.headers.get("Authorization", "")
    
    if not auth_header.startswith("Bearer "):
        logger.warn(f"认证失败 - 未提供令牌 - 路径: {path}")
        return JSONResponse(
            status_code=401,
            content={"detail": "未提供认证令牌"}
        )
    
    token = auth_header[7:]  # 去掉 "Bearer " 前缀
    
    # 3. 验证 Token 并存储用户信息
    try:
        payload = decode_access_token(token)
        # 将用户信息存入 request state，供后续接口使用
        request.state.user = {
            "id": payload.get("user_id"),
            "username": payload.get("username"),
            "role": payload.get("roles", [])[0] if payload.get("roles") else ""
        }
        logger.debug(f"认证成功 - 用户: {request.state.user['username']} - 角色: {request.state.user['role']}")
    except HTTPException as e:
        logger.warn(f"认证失败 - Token无效 - 路径: {path} - 错误: {e.detail}")
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
    
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
app.include_router(users_router)
app.include_router(addresses_router)
app.include_router(ai_router)
app.include_router(logs_router)


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
