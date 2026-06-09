"""
订单明细表模型
映射数据库 order_items 表
"""
from sqlalchemy import Column, String, BIGINT, DECIMAL, Boolean, DateTime
from datetime import datetime
from model import Base


class OrderItem(Base):
    """订单明细表模型"""
    __tablename__ = "order_items"
    
    id = Column(String(50), primary_key=True, index=True, comment="主键id")
    order_id = Column(String(64), nullable=False, index=True, comment="订单编号")
    product_id = Column(String(64), nullable=False, comment="商品id")
    product_name = Column(String(255), nullable=False, comment="商品名称")
    spec_info = Column(String(255), comment="规格信息")
    product_image = Column(String(500), comment="商品图片")
    quantity = Column(BIGINT, nullable=False, comment="购买数量")
    total_amount = Column(DECIMAL(10, 2), nullable=False, comment="总计金额")
    item_remark = Column(String(255), comment="商品明细备注")
    is_deleted = Column(Boolean, nullable=False, default=False, comment="逻辑删除")
    create_time = Column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="更新时间")
