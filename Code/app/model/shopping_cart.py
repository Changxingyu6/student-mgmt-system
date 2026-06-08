from sqlalchemy import Column, String, DateTime, Boolean
from model import Base
from datetime import datetime


class ShoppingCart(Base):
    """购物车主表 ORM 模型"""
    __tablename__ = "shopping_cart"
    
    cart_id = Column(String(50), primary_key=True, comment="购物车主键ID")
    user_id = Column(String(50), nullable=False, unique=True, comment="用户ID")
    is_active = Column(Boolean, nullable=False, default=True, comment="是否有效 0-无效 1-有效")
    is_deleted = Column(Boolean, nullable=False, default=False, comment="逻辑删除")
    created_time = Column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
    updated_time = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="更新时间")