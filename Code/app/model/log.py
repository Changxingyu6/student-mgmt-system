"""
日志模型
记录登录日志和操作日志
"""
from sqlalchemy import Column, String, DateTime, Text, Enum
from datetime import datetime
from model import Base


class LoginLog(Base):
    """登录日志模型"""
    __tablename__ = "login_logs"
    
    id = Column(String(50), primary_key=True, index=True, comment="日志ID（UUID）")
    user_id = Column(String(50), comment="用户ID（登录成功时记录）")
    username = Column(String(50), comment="登录用户名")
    ip_address = Column(String(50), comment="登录IP")
    user_agent = Column(String(255), comment="浏览器信息")
    login_type = Column(Enum('password', 'sms', 'wechat', 'alipay'), default='password', comment='登录方式')
    status = Column(Enum('success', 'failed'), comment="登录状态")
    error_message = Column(String(255), comment="错误信息")
    create_time = Column(DateTime, default=datetime.now, nullable=False, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment="更新时间")
    
    __table_args__ = {
        'comment': '登录日志表'
    }


class OperationLog(Base):
    """操作日志模型"""
    __tablename__ = "operation_logs"
    
    id = Column(String(50), primary_key=True, index=True, comment="日志ID（UUID）")
    user_id = Column(String(50), nullable=False, comment="操作用户ID")
    username = Column(String(50), comment="操作用户名")
    module = Column(String(50), comment="操作模块")
    action = Column(String(50), comment="操作类型")
    target_id = Column(String(50), comment="操作对象ID")
    target_name = Column(String(255), comment="操作对象名称")
    before_data = Column(Text, comment="操作前数据（JSON）")
    after_data = Column(Text, comment="操作后数据（JSON）")
    ip_address = Column(String(50), comment="操作IP")
    create_time = Column(DateTime, default=datetime.now, nullable=False, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment="更新时间")
    
    __table_args__ = {
        'comment': '操作日志表'
    }