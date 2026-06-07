from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from fastapi import HTTPException
from api import students_router, auth_router, ai_router
from utils.jwt_utils import decode_access_token

# 白名单：不需要 Token 认证的路径
WHITELIST = [
    "/auth/login",
    "/auth/register",
    "/docs",
    "/redoc",
    "/openapi.json",
]


# 创建 FastAPI 实例
app = FastAPI(
    title="学生管理系统 API",
    description="基于 FastAPI 的学生管理系统，使用 SQLAlchemy 进行数据库操作，采用三层架构",
    version="1.0.0"
)


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
    except HTTPException as e:
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
app.include_router(auth_router)
app.include_router(students_router)
app.include_router(ai_router)


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
