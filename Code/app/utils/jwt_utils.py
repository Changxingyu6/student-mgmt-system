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

# 获取当前文件所在目录（utils/）
UTILS_DIR = Path(__file__).resolve().parent

# 加载环境变量（从 app/.env 文件）
load_dotenv(UTILS_DIR.parent / ".env")

# JWT 设置
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    
    # 添加标准声明
    to_encode.update({
        "iat": datetime.now(),  # 签发时间
        "exp": expire
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """解析访问令牌"""
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload