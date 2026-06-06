# 数据库模型模块
# 使用 SQLAlchemy ORM 定义数据库表映射

from sqlalchemy import create_engine, Column, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class BaseModel(Base):
    """
    基础模型类，提供通用字段和方法
    所有业务模型都应继承此类
    """
    __abstract__ = True  # 抽象类，不会创建表
    
    created_at = Column(
        DateTime, 
        default=func.now(), 
        nullable=False, 
        comment="创建时间"
    )
    updated_at = Column(
        DateTime, 
        default=func.now(), 
        onupdate=func.now(), 
        nullable=False, 
        comment="更新时间"
    )
    