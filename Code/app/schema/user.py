"""
用户管理 Schema
定义用户相关的请求和响应数据结构
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime


class UserLoginRequest(BaseModel):
    """用户登录请求"""
    username: str = Field(..., description="用户名", min_length=3, max_length=50)
    password: str = Field(..., description="密码")


class UserRegisterRequest(BaseModel):
    """用户注册请求"""
    username: str = Field(..., description="用户名", min_length=3, max_length=50)
    password: str = Field(..., description="密码")
    nickname: Optional[str] = Field(None, description="昵称", max_length=50)
    phone: Optional[str] = Field(None, description="手机号")
    email: Optional[EmailStr] = Field(None, description="邮箱")

    @validator('phone')
    def validate_phone(cls, v):
        if v and not v.isdigit():
            raise ValueError('手机号必须为数字')
        return v


class UserProfileUpdateRequest(BaseModel):
    """更新个人信息请求"""
    nickname: Optional[str] = Field(None, description="昵称", max_length=50)
    phone: Optional[str] = Field(None, description="手机号")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    gender: Optional[str] = Field(None, description="性别", pattern='^(male|female|other)$')
    avatar: Optional[str] = Field(None, description="头像URL")

    @validator('phone')
    def validate_phone(cls, v):
        if v and not v.isdigit():
            raise ValueError('手机号必须为数字')
        return v


class UserPasswordUpdateRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., description="新密码")


class UserCreateRequest(BaseModel):
    """管理员创建用户请求"""
    username: str = Field(..., description="用户名", min_length=3, max_length=50)
    password: str = Field(..., description="初始密码")
    nickname: Optional[str] = Field(None, description="昵称", max_length=50)
    phone: Optional[str] = Field(None, description="手机号")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    user_level: Optional[str] = Field("青铜会员", description="用户等级", pattern='^(青铜会员|白银会员|黄金会员)$')
    balance: Optional[float] = Field(0.00, description="初始余额", ge=0)
    status: Optional[str] = Field("active", description="状态", pattern='^(active|inactive|banned)$')


class UserUpdateRequest(BaseModel):
    """管理员更新用户请求"""
    nickname: Optional[str] = Field(None, description="昵称", max_length=50)
    phone: Optional[str] = Field(None, description="手机号")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    user_level: Optional[str] = Field(None, description="用户等级", pattern='^(青铜会员|白银会员|黄金会员)$')
    status: Optional[str] = Field(None, description="状态", pattern='^(active|inactive|banned)$')


class BalanceOperationRequest(BaseModel):
    """余额操作请求"""
    amount: float = Field(..., description="金额", gt=0)
    reason: Optional[str] = Field(None, description="操作原因", max_length=255)


class DiscountSetRequest(BaseModel):
    """设置折扣请求"""
    discount_rate: float = Field(..., description="折扣率", ge=0.1, le=1.0)


class UserResponse(BaseModel):
    """用户响应模型"""
    id: str = Field(..., description="用户ID（UUID）")
    username: str = Field(..., description="用户名")
    nickname: Optional[str] = Field(None, description="昵称")
    phone: Optional[str] = Field(None, description="手机号")
    email: Optional[str] = Field(None, description="邮箱")
    gender: Optional[str] = Field(None, description="性别", pattern='^(male|female|other)$')
    avatar: Optional[str] = Field(None, description="头像URL")
    user_level: str = Field(..., description="用户等级")
    points: int = Field(..., description="会员积分")
    balance: float = Field(..., description="用户余额")
    discount_rate: float = Field(..., description="优惠折扣率")
    status: str = Field(..., description="账号状态")
    is_locked: bool = Field(..., description="是否被锁定")
    failed_attempts: int = Field(..., description="登录失败次数")
    lock_count: int = Field(..., description="锁定次数")
    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")


class UserListResponse(BaseModel):
    """用户列表响应模型"""
    data: list[UserResponse] = Field(..., description="用户列表")
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    limit: int = Field(..., description="每页数量")


class LoginResponse(BaseModel):
    """登录响应模型"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(..., description="令牌类型")
    user: UserResponse = Field(..., description="用户信息")


# 导出的公共接口
__all__ = [
    "UserLoginRequest",
    "UserRegisterRequest",
    "UserProfileUpdateRequest",
    "UserPasswordUpdateRequest",
    "UserCreateRequest",
    "UserUpdateRequest",
    "BalanceOperationRequest",
    "DiscountSetRequest",
    "UserResponse",
    "UserListResponse",
    "LoginResponse"
]