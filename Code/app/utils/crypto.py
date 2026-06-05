"""
加密工具函数
提供密码加密、盐值生成等功能
"""
import hashlib
import random
import string


def generate_salt(length: int = 8) -> str:
    """生成随机盐值"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def md5_hash(salt: str, password: str) -> str:
    """MD5加密：MD5(salt + password)"""
    return hashlib.md5((salt + password).encode()).hexdigest()


def verify_password(salt: str, plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return md5_hash(salt, plain_password) == hashed_password