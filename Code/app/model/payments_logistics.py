from sqlalchemy.orm import relationship
from sqlalchemy import Column, BigInteger, String, DateTime, Text, ForeignKey, Index, DECIMAL, func
from sqlalchemy.dialects.mysql import ENUM

# 从统一的 model 模块导入 Base
from . import Base

class Payments(Base):
    # 支付记录表
    __tablename__ = 'payments'
    pay_id = Column(String(50), primary_key=True, comment="支付单ID")
    pay_no = Column(String(64), unique=True, nullable=False, comment="支付流水号")
    # order_id = Column(String(50),ForeignKey("orders.id",ondelete="CASCADE"),nullable=False,comment="订单ID")
    order_id = Column(String(50),nullable=False,comment="订单ID")
    user_id = Column(String(50), nullable=False, comment="用户ID")
    # 枚举直接建在表里
    pay_status = Column(
        ENUM("待支付", "支付中", "支付成功", "支付失败", "已关闭"),
        default="待支付",
        nullable=False,
        comment="支付状态"
    )

    pay_amount = Column(DECIMAL(10,2), nullable=False, comment="支付金额")
    pay_time = Column(DateTime, comment="支付时间")
    pay_method = Column(ENUM("余额"), nullable=False,default="余额")
    is_abnormal = Column(ENUM("0","1"), default="0", comment="0正常1异常")
    create_time = Column(DateTime, default=func.now() ,comment="审计字段")
    expire_time = Column(DateTime, comment="过期时间30分钟")
    update_time = Column(DateTime, default=func.now(), onupdate=func.now() ,comment="更新操作时间")
    is_deleted = Column(ENUM("0","1"), default="0", comment="0正常1删除")

    __table_args__ = (
        Index('idx_order_id', order_id),          # 订单查询必加
        Index('idx_user_id', user_id),            # 用户查询必加
        Index('idx_pay_status', pay_status),      # 状态筛选
    )
class Refund(Base):
    # 退款记录表
    __tablename__ = "refund"
    refund_id = Column(String(50), primary_key=True)
    refund_no = Column(String(64), unique=True, nullable=False)
    # after_sales_id = Column(String(36),ForeignKey("after_sales.id",ondelete="CASCADE"),nullable=False,comment="售后订单ID")
    after_sales_id = Column(String(36),nullable=False,comment="售后订单ID")
    refund_status = Column(
        ENUM("待退款", "退款中", "退款成功", "退款失败"),
        default="待退款", nullable=False
    )
    refund_amount = Column(DECIMAL(10, 2), nullable=False)
    refund_method = Column(ENUM("余额"), nullable=False)
    refund_time = Column(DateTime)
    create_time = Column(DateTime, default=func.now())
    update_time = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新操作时间")
    is_abnormal = Column(ENUM("0", "1"), default="0", comment="0正常1异常")
    is_deleted = Column(ENUM("0", "1"), default="0", comment="0正常1删除")
    __table_args__ = (
        Index('idx_after_sales_id', after_sales_id),  # 售后单查询
        Index('idx_refund_status', refund_status),    # 退款状态筛选
    )
class Logistics(Base):
    # 物流表
    __tablename__ = "logistics"
    logistics_id = Column(String(50), primary_key=True)
    # order_id = Column(String(50),ForeignKey("orders.id",ondelete="CASCADE"),nullable=False,comment="订单ID")
    order_id = Column(String(50),nullable=False,comment="订单ID")
    logistics_no = Column(String(64), unique=True, nullable=False)
    logistics_status = Column(
        ENUM("待发货", "已揽收", "运输中", "派送中", "已签收", "异常"),
        default="待发货", nullable=False
    )
    track_info = Column(Text, nullable=True)
    create_time = Column(DateTime, default=func.now())
    update_time = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新操作时间")
    is_deleted = Column(ENUM("0", "1"), default="0", comment="0正常1删除")

    __table_args__ = (
        Index('idx_order_id', order_id),                # 订单查物流
        Index('idx_logistics_status', logistics_status),# 物流状态筛选
    )

class Return_Logistics(Base):
    # 退货物流表
    __tablename__ = "return_logistics"
    return_logistics_id = Column(String(50), primary_key=True)
    # after_sales_id = Column(String(36),ForeignKey("after_sales.id",ondelete="CASCADE"),nullable=False,comment="售后订单ID")
    after_sales_id = Column(String(36),nullable=False,comment="售后订单ID")
    return_logistics_no = Column(String(64), unique=True, nullable=False)
    return_logistics_status = Column(
        ENUM("待发货", "已揽收", "运输中", "派送中", "已签收", "异常"),
        default="待发货", nullable=False
    )
    return_track_info = Column(Text, nullable=True)
    create_time = Column(DateTime, default=func.now())
    update_time = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新操作时间")
    is_deleted = Column(ENUM("0", "1"), default="0", comment="0正常1删除")
    __table_args__ = (
        Index('idx_after_sales_id', after_sales_id),              # 售后单查退货物流
        Index('idx_return_logistics_status', return_logistics_status), # 退货状态筛选
    )
