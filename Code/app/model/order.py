"""
订单主表模型
映射数据库 orders 表
"""
from sqlalchemy import Column, String, DECIMAL, DateTime, Boolean
from datetime import datetime
from model import Base


class Order(Base):
    """订单主表模型"""
    __tablename__ = "orders"
    
    id = Column(String(50), primary_key=True, index=True, comment="主键id")
    order_id = Column(String(50), unique=True, nullable=False, index=True, comment="订单编号")
    user_id = Column(String(50), nullable=False, index=True, comment="用户id")
    total_amount = Column(DECIMAL(10, 2), nullable=False, comment="订单总金额")
    actual_pay_amount = Column(DECIMAL(10, 2), nullable=False, default=0.00, comment="实付金额")
    coupon_discount = Column(DECIMAL(10, 2), nullable=False, default=0.00, comment="优惠券抵扣")
    member_discount = Column(DECIMAL(10, 2), nullable=False, default=0.00, comment="会员折扣")
    order_status = Column(String(32), nullable=False, default='pending', comment="订单状态")
    pay_status = Column(String(32), nullable=False, default='unpaid', comment="支付状态")
    logistics_status = Column(String(32), nullable=False, default='waiting_ship', comment="物流状态")
    payment_method = Column(String(32), nullable=False, comment="支付方式")
    remark = Column(String(255), comment="订单备注")
    receiver_name = Column(String(32), nullable=False, comment="收货人姓名")
    receiver_phone = Column(String(20), nullable=False, comment="收货人电话")
    shipping_address = Column(String(255), nullable=False, comment="收货地址")
    expire_time = Column(DateTime, nullable=False, comment="失效时间")
    pay_time = Column(DateTime, comment="支付时间")
    ship_time = Column(DateTime, comment="发货时间")
    receive_time = Column(DateTime, comment="签收时间")
    is_deleted = Column(Boolean, nullable=False, default=False, comment="逻辑删除")
    create_time = Column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="更新时间")
