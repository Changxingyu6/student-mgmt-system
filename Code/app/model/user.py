"""
用户模型
映射数据库 users 表，用于用户认证
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, DECIMAL, Enum
from datetime import datetime
from model import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    password = Column(String(32), nullable=False, comment="密码（MD5加密，32位）")
    salt = Column(String(32), nullable=False, comment="加密盐值")
    nickname = Column(String(50), comment="昵称")
    phone = Column(String(20), comment="手机号")
    email = Column(String(100), comment="邮箱")
    gender = Column(Enum('male', 'female', 'other'), comment="性别")
    avatar = Column(String(255), comment="头像URL")
    user_level = Column(Enum('青铜会员', '白银会员', '黄金会员'), default='青铜会员', comment="用户等级")
    points = Column(Integer, default=0, comment="会员积分")
    balance = Column(DECIMAL(10, 2), default=0.00, comment="用户余额")
    discount_rate = Column(DECIMAL(5, 2), default=1.00, comment="优惠折扣率（1.00表示原价，0.9表示9折）")
    default_address_id = Column(Integer, comment="默认收货地址ID")
    status = Column(Enum('active', 'inactive', 'banned'), default='active', comment="账号状态")
    is_deleted = Column(Boolean, default=False, comment="逻辑删除")
    failed_attempts = Column(Integer, default=0, comment="连续登录失败次数")
    lock_until = Column(DateTime, comment="账户锁定截止时间")
    lock_count = Column(Integer, default=0, comment="连续锁定次数")
