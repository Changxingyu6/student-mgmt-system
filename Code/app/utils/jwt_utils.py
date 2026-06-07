"""
JWT 工具函数
提供 JWT token 生成和解析功能
"""
from datetime import datetime, timedelta
from typing import Optional
import jwt
from dotenv import load_dotenv
import os
from pathlib import Path
from fastapi import HTTPException, status

# 获取当前文件所在目录（utils/）
UTILS_DIR = Path(__file__).resolve().parent

# 加载环境变量（从 app/.env 文件）
load_dotenv(UTILS_DIR.parent / ".env")

# JWT 设置
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


def create_access_token(data: dict) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    # 使用 UTC 时间，JWT 标准要求
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # 添加标准声明
    to_encode.update({
        "iat": datetime.utcnow(),  # 签发时间（UTC）
        "exp": expire
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """解析 Token，返回 payload（包含异常处理）"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="认证令牌已过期")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="认证令牌无效")