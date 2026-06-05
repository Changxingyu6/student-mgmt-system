from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import students_router,auth_public_router,auth_protected_router

# 创建 FastAPI 实例
app = FastAPI(
    title="学生管理系统 API",
    description="基于 FastAPI 的学生管理系统，使用 SQLAlchemy 进行数据库操作，采用三层架构",
    version="1.0.0"
)

# 配置 CORS（跨域资源共享）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 允许所有来源（生产环境应限制具体域名）
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
)

# 注册路由
# 公开路由（无需认证）
app.include_router(auth_public_router)

# 受保护路由（需要认证）
app.include_router(auth_protected_router)
app.include_router(students_router)


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
