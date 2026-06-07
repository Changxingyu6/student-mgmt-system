"""
用户模型
映射数据库 users 表，用于用户认证
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from model import BaseModel


class User(BaseModel):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    password = Column(String(32), nullable=False, comment="密码（MD5加密，32位）")
    salt = Column(String(32), nullable=False, comment="加密盐值")
    role = Column(String(20), nullable=False, comment="角色：admin/teacher/student")
    related_id = Column(Integer, comment="关联ID（学生ID或教师ID）")
    is_active = Column(Boolean, default=True, comment="是否启用")
    failed_attempts = Column(Integer, default=0, comment="连续登录失败次数")
    lock_until = Column(DateTime, comment="账户锁定截止时间")
    lock_count = Column(Integer, default=0, comment="连续锁定次数")