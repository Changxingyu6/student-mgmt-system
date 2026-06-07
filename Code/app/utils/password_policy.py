"""
密码安全策略模块
提供密码复杂度校验功能
"""
import re
from fastapi import HTTPException


def validate_password(password: str) -> None:
    """
    验证密码复杂度
    
    规则：
    - 至少8位
    - 至少包含大写字母、小写字母、数字中的2种
    - 可选：至少包含一个特殊字符
    
    Args:
        password: 待验证的密码
        
    Raises:
        HTTPException: 密码不符合要求时抛出
    """
    # 检查长度
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="密码长度至少需要8位")
    
    # 检查字符类型
    has_upper = bool(re.search(r'[A-Z]', password))
    has_lower = bool(re.search(r'[a-z]', password))
    has_digit = bool(re.search(r'[0-9]', password))
    has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
    
    # 至少需要2种字符类型
    type_count = sum([has_upper, has_lower, has_digit, has_special])
    if type_count < 2:
        raise HTTPException(
            status_code=400, 
            detail="密码至少需要包含大写字母、小写字母、数字或特殊字符中的2种"
        )


def get_password_strength(password: str) -> str:
    """
    评估密码强度
    
    Returns:
        密码强度等级：weak/medium/strong
    """
    score = 0
    
    # 长度评分
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    
    # 字符类型评分
    if bool(re.search(r'[A-Z]', password)):
        score += 1
    if bool(re.search(r'[a-z]', password)):
        score += 1
    if bool(re.search(r'[0-9]', password)):
        score += 1
    if bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password)):
        score += 1
    
    # 返回强度等级
    if score <= 2:
        return "weak"
    elif score <= 4:
        return "medium"
    else:
        return "strong"
