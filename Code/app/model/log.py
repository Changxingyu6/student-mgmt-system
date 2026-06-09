"""
日志模型
记录登录日志
"""
from sqlalchemy import Column, String, DateTime, Enum
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
