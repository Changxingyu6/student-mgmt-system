"""
UUID 工具类
提供 UUID 生成功能
"""
import uuid


def generate_uuid() -> str:
    """
    生成标准 UUID（36位，带连字符）
    
    Returns:
        str: 36位 UUID 字符串，如 'a1b2c3d4-e5f6-7890-a1b2-c3d4e5f67890'
    """
    return str(uuid.uuid4())
