"""
角色模型
映射数据库 roles 表，用于角色权限管理
"""
from sqlalchemy import Column, Integer, String, DateTime, Enum
from datetime import datetime
from model import BaseModel


class Role(BaseModel):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    role_name = Column(String(50), unique=True, nullable=False, index=True, comment="角色名称")
    description = Column(String(255), comment="角色描述")
    status = Column(Enum('active', 'inactive'), default='active', comment="状态")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
