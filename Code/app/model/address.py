"""
用户收货地址模型
映射数据库 user_addresses 表
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from datetime import datetime
from model import Base


class UserAddress(Base):
    __tablename__ = "user_addresses"
    
    id = Column(String(50), primary_key=True, index=True, comment="地址ID（UUID）")
    user_id = Column(String(50), ForeignKey('users.id'), nullable=False, comment="用户ID")
    receiver_name = Column(String(50), nullable=False, comment="收货人姓名")
    receiver_phone = Column(String(20), nullable=False, comment="收货人电话")
    province = Column(String(50), comment="省份")
    city = Column(String(50), comment="城市")
    district = Column(String(50), comment="区县")
    detail_address = Column(String(255), nullable=False, comment="详细地址")
    is_default = Column(Boolean, default=False, comment="是否默认地址")
    is_deleted = Column(Boolean, default=False, comment="逻辑删除")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
