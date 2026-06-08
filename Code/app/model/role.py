"""
角色模型
映射数据库 roles 表，用于角色权限管理
"""
from sqlalchemy import Column, String, DateTime, Enum
from datetime import datetime
from model import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(String(50), primary_key=True, index=True, comment="角色ID（UUID）")
    role_name = Column(String(50), unique=True, nullable=False, index=True, comment="角色名称")
    description = Column(String(255), comment="角色描述")
    status = Column(Enum('active', 'inactive'), default='active', comment="状态")
    created_time = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
