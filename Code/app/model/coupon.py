from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DECIMAL, ForeignKey, Table, VARCHAR, DateTime

from model import Base
from database import engine

activities_goods = Table(
    'activities_goods',
    Base.metadata,
    Column('activities_id', VARCHAR(50), ForeignKey('activities.id'), primary_key=True),
    Column('goods_id', VARCHAR(50), ForeignKey('goods.id'), primary_key=True),
    Column('is_deleted',Integer, default=0,index=True, comment='0正常,1删除')
)

# activities_orders = Table(
#     'activities_orders',
#     Base.metadata,
#     Column('activities_id', VARCHAR(50), ForeignKey('activities.id'), primary_key=True),
#     Column('orders_id', VARCHAR(50), ForeignKey('orders.id'), primary_key=True),
#     Column('is_deleted',Integer, default=0,index=True, comment='0正常,1删除')
# )

class Coupon(Base):
    __tablename__ = 'coupons'
    id = Column(VARCHAR(50), primary_key=True, comment='主键ID')
    coupons_no = Column(String(50), nullable=False, unique=True, comment='券编号')
    coupons_name = Column(String(200), nullable=False, comment='券名称')
    type = Column(Integer, nullable=False, comment='1满减,2折扣,3无门槛')
    face_value = Column(DECIMAL(10,2), nullable=False, default=1.00, comment='面额/折扣值')
    min_spend = Column(DECIMAL(10,2), nullable=False, default=0.00, comment='满减门槛')
    total_count = Column(Integer, nullable=False, default=0, comment='发放总量')
    sent_count = Column(Integer, nullable=False, default=0, comment="已发放数量")
    used_count = Column(Integer, nullable=False, default=0, comment="已使用数量")
    valid_start_time = Column(DateTime, nullable=False, comment="有效期开始时间")
    valid_end_time = Column(DateTime, nullable=False, comment="有效期结束时间")
    status = Column(Integer, nullable=False, default=1, comment="0下架，1生效，2过期")
    is_deleted = Column(Integer, default=0, comment='0正常,1删除')
    user_coupons = relationship('UserCoupon', back_populates='coupons')
class UserCoupon(Base):
    __tablename__ = 'user_coupons'
    id = Column(VARCHAR(50), primary_key=True, comment='主键ID')
    coupon_id = Column(VARCHAR(50), ForeignKey('coupons.id'), nullable=False, comment='关联券ID')
    user_id = Column(VARCHAR(50), ForeignKey('users.id'), nullable=False, comment='关联用户ID')
    coupon_no = Column(String(50), nullable=False, comment='优惠券编号')
    status = Column(Integer, nullable=False, default=0, comment='0未领取,1已领取,2已过期')
    get_time = Column(DateTime, nullable=False, comment='领取时间')
    use_time = Column(DateTime, nullable=True, comment='使用时间')
    valid_end_time = Column(DateTime, nullable=False, comment='有效期结束时间')
    is_deleted = Column(Integer, default=0, comment='0正常,1删除')
    coupons = relationship('Coupon', back_populates='user_coupons')
    coupon_use_log = relationship('CouponUseLog', back_populates='user_coupon')

class CouponUseLog(Base):
    __tablename__ = 'coupon_use_log'
    id = Column(VARCHAR(50),primary_key=True,comment='主键ID')
    user_coupon_id = Column(VARCHAR(50),ForeignKey('user_coupons.id'),nullable=False,comment='用户券ID')
    user_id = Column(VARCHAR(50),ForeignKey('users.id'),nullable=False,comment='关联用户ID')
    status = Column(Integer,nullable=False,default=0,comment='0使用失败,1使用成功')
    order_id = Column(VARCHAR(50),ForeignKey('orders.id'),comment='关联订单ID')
    remark = Column(VARCHAR(255),nullable=True,comment='备注信息')
    is_deleted = Column(Integer, default=0, comment='0正常,1删除')
    user_coupon = relationship('UserCoupon', back_populates='coupon_use_log')


class Activities(Base):
    __tablename__ = 'activities'
    id = Column(VARCHAR(50), primary_key=True, comment='主键ID')
    activities_name = Column(String(200), nullable=False, comment='活动名称')
    activities_type = Column(String(10), nullable=False, comment='1满减,2折扣')
    face_value = Column(DECIMAL(10, 2), nullable=False, default=1.00, comment='面额/折扣值')
    min_spend = Column(DECIMAL(10, 2), nullable=False, default=0.00, comment='满减门槛')
    start_time = Column(DateTime, nullable=False, comment='开始时间')
    end_time = Column(DateTime, nullable=False, comment='结束时间')
    status = Column(Integer, nullable=False, default=1, comment="0下架,1生效")
    is_deleted = Column(Integer, default=0, comment='0正常,1删除')


Base.metadata.create_all(engine)
