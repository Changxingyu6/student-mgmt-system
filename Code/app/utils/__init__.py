"""
工具函数模块
提供通用工具函数
"""
from .crypto import generate_salt, md5_hash, verify_password
from .jwt_utils import create_access_token, decode_access_token


def format_response(data=None, message="success", code=200):
    """统一响应格式"""
    return {
        "code": code,
        "message": message,
        "data": data
    }


# 导出所有工具函数
__all__ = [
    "format_response",
    "generate_salt",
    "md5_hash",
    "verify_password",
    "create_access_token",
    "decode_access_token"
]
