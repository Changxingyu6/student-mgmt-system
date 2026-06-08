"""
用户收货地址 Schema
定义地址相关的请求和响应数据结构
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AddressCreateRequest(BaseModel):
    """创建收货地址请求"""
    receiver_name: str = Field(..., description="收货人姓名", max_length=50)
    receiver_phone: str = Field(..., description="收货人电话", max_length=20)
    province: Optional[str] = Field(None, description="省份", max_length=50)
    city: Optional[str] = Field(None, description="城市", max_length=50)
    district: Optional[str] = Field(None, description="区县", max_length=50)
    detail_address: str = Field(..., description="详细地址", max_length=255)
    is_default: Optional[bool] = Field(False, description="是否设为默认地址")


class AddressUpdateRequest(BaseModel):
    """更新收货地址请求"""
    receiver_name: Optional[str] = Field(None, description="收货人姓名", max_length=50)
    receiver_phone: Optional[str] = Field(None, description="收货人电话", max_length=20)
    province: Optional[str] = Field(None, description="省份", max_length=50)
    city: Optional[str] = Field(None, description="城市", max_length=50)
    district: Optional[str] = Field(None, description="区县", max_length=50)
    detail_address: Optional[str] = Field(None, description="详细地址", max_length=255)
    is_default: Optional[bool] = Field(None, description="是否设为默认地址")


class AddressResponse(BaseModel):
    """收货地址响应"""
    id: str = Field(..., description="地址ID（UUID）")
    receiver_name: str = Field(..., description="收货人姓名")
    receiver_phone: str = Field(..., description="收货人电话")
    province: Optional[str] = Field(None, description="省份")
    city: Optional[str] = Field(None, description="城市")
    district: Optional[str] = Field(None, description="区县")
    detail_address: str = Field(..., description="详细地址")
    is_default: bool = Field(..., description="是否默认地址")
    created_at: datetime = Field(..., description="创建时间")


class AddressListResponse(BaseModel):
    """地址列表响应"""
    data: list[AddressResponse] = Field(..., description="地址列表")
    total: int = Field(..., description="总记录数")