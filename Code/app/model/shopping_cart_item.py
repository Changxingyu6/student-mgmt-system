from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from model import Base
from datetime import datetime


class ShoppingCartItem(Base):
    """购物车项表 ORM 模型"""
    __tablename__ = "shopping_cart_item"
    
    item_id = Column(String(50), primary_key=True, comment="购物车项主键ID")
    cart_id = Column(String(50), ForeignKey('shopping_cart.cart_id'), nullable=False, comment="购物车ID")
    goods_id = Column(String(50), nullable=False, comment="商品ID")
    spec_id = Column(String(50), nullable=True, comment="商品规格ID，无规格为null")
    buy_num = Column(Integer, nullable=False, default=1, comment="购买数量")
    is_checked = Column(Boolean, nullable=False, default=False, comment="是否选中 0-未选中 1-选中")
    is_deleted = Column(Boolean, nullable=False, default=False, comment="逻辑删除")
    created_time = Column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
    updated_time = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    cart = relationship("ShoppingCart", backref="items")