"""
售后订单表模型
映射数据库 after_sales 表
"""
from sqlalchemy import Column, String, DECIMAL, BIGINT, SMALLINT, Boolean, DateTime
from datetime import datetime
from model import Base


class AfterSale(Base):
    """售后订单表模型"""
    __tablename__ = "after_sales"
    
    id = Column(String(50), primary_key=True, index=True, comment="主键id")
    order_id = Column(String(50), nullable=False, index=True, comment="订单编号")
    user_id = Column(String(50), nullable=False, comment="用户id")
    product_id = Column(String(64), nullable=False, comment="商品id")
    after_sale_type = Column(String(32), nullable=False, comment="售后类型")
    reason = Column(String(255), nullable=False, comment="售后原因")
    refund_amount = Column(DECIMAL(10, 2), nullable=False, comment="退款金额")
    refund_quantity = Column(BIGINT, nullable=False, comment="退款数量")
    actual_pay_amount = Column(DECIMAL(10, 2), nullable=False, comment="实付金额")
    audit_status = Column(String(32), default='pending', comment="审核状态")
    after_sale_status = Column(SMALLINT, nullable=False, default=1, comment="1-仅退款 2-全额退款")
    shipping_address = Column(String(255), nullable=False, comment="收货地址")
    payment_method = Column(String(32), nullable=False, comment="支付方式")
    order_create_time = Column(DateTime, nullable=False, comment="下单时间")
    order_ship_time = Column(DateTime, comment="发货时间")
    order_complete_time = Column(DateTime, comment="完成时间")
    remark = Column(String(255), comment="备注")
    is_deleted = Column(Boolean, nullable=False, default=False, comment="逻辑删除")
    create_time = Column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="更新时间")
