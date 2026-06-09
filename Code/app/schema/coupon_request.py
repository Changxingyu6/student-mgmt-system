from pydantic import BaseModel, Field
from typing import Optional, Any, List
from datetime import datetime
from decimal import Decimal


# 统一的响应格式
class ResponseModel(BaseModel):
    code: int = 200
    msg: str = "success"
    data: Optional[Any] = None

#优惠券
class CouponBase(BaseModel):
    coupons_no: str
    coupons_name: str
    type: int = Field(..., ge=1, le=3, description="1满减,2折扣,3无门槛")
    face_value: Decimal = Field(..., max_digits=10, decimal_places=2)
    min_spend: Decimal = Field(0.00, max_digits=10, decimal_places=2)
    total_count: int = Field(0, ge=0)
    sent_count: int = Field(0, ge=0)
    used_count: int = Field(0, ge=0)
    valid_start_time: datetime
    valid_end_time: datetime
    status: int = Field(1, ge=0, le=2, description="0下架,1生效,2过期")


class CouponCreate(CouponBase):
    pass


class CouponUpdate(BaseModel):
    coupons_name: Optional[str] = None
    type: Optional[int] = Field(None, ge=1, le=3)
    face_value: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2)
    min_spend: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2)
    total_count: Optional[int] = Field(None, ge=0)
    sent_count: Optional[int] = Field(None, ge=0)
    used_count: Optional[int] = Field(None, ge=0)
    valid_start_time: Optional[datetime] = None
    valid_end_time: Optional[datetime] = None
    status: Optional[int] = Field(None, ge=0, le=2)


class CouponOut(CouponBase):
    id: str
    is_deleted: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CouponQuery(BaseModel):
    coupons_no: Optional[str] = None
    coupons_name: Optional[str] = None
    type: Optional[int] = None
    status: Optional[int] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)

#用户优惠券
class UserCouponBase(BaseModel):
    coupon_id: str
    user_id: str
    coupon_no: str
    status: int = Field(0, ge=0, le=2, description="0未领取,1已领取,2已过期")
    get_time: datetime
    use_time: Optional[datetime] = None
    valid_end_time: datetime


class UserCouponCreate(UserCouponBase):
    pass


class UserCouponUpdate(BaseModel):
    status: Optional[int] = Field(None, ge=0, le=2)
    use_time: Optional[datetime] = None
    valid_end_time: Optional[datetime] = None


class UserCouponOut(UserCouponBase):
    id: str
    is_deleted: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserCouponQuery(BaseModel):
    user_id: Optional[str] = None
    coupon_id: Optional[str] = None
    status: Optional[int] = None
    page: int = 1
    page_size: int = 20

#优惠券使用日志
class CouponUseLogBase(BaseModel):
    user_coupon_id: str
    user_id: str
    status: int = Field(0, ge=0, le=1, description="0使用失败,1使用成功")
    order_id: Optional[str] = None
    remark: Optional[str] = None


class CouponUseLogCreate(CouponUseLogBase):
    pass


class CouponUseLogUpdate(BaseModel):
    status: Optional[int] = Field(None, ge=0, le=1)
    remark: Optional[str] = None


class CouponUseLogOut(CouponUseLogBase):
    id: str
    is_deleted: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CouponUseLogQuery(BaseModel):
    user_id: Optional[str] = None
    user_coupon_id: Optional[str] = None
    status: Optional[int] = None
    page: int = 1
    page_size: int = 20

#营销活动
class ActivitiesBase(BaseModel):
    activities_name: str
    activities_type: str = Field(..., pattern="^(1|2)$", description="1满减,2折扣")
    face_value: Decimal = Field(..., max_digits=10, decimal_places=2)
    min_spend: Decimal = Field(0.00, max_digits=10, decimal_places=2)
    start_time: datetime
    end_time: datetime
    status: int = Field(1, ge=0, le=1, description="0下架,1生效")


class ActivitiesCreate(ActivitiesBase):
    goods_ids: Optional[List[str]] = []
    order_ids: Optional[List[str]] = []


class ActivitiesUpdate(BaseModel):
    activities_name: Optional[str] = None
    activities_type: Optional[str] = Field(None, pattern="^(1|2)$")
    face_value: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2)
    min_spend: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[int] = Field(None, ge=0, le=1)
    goods_ids: Optional[List[str]] = None
    order_ids: Optional[List[str]] = None


class ActivitiesOut(ActivitiesBase):
    id: str
    is_deleted: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ActivitiesQuery(BaseModel):
    activities_name: Optional[str] = None
    activities_type: Optional[str] = None
    status: Optional[int] = None
    page: int = 1
    page_size: int = 20

#活动商品关联
class ActivityGoodsCreate(BaseModel):
    activities_id: str
    product_id: str


class ActivityGoodsDelete(BaseModel):
    activities_id: str
    product_id: Optional[str] = None


class ActivityGoodsQuery(BaseModel):
    activities_id: Optional[str] = None
    product_id: Optional[str] = None
    page: int = 1
    page_size: int = 20

#活动订单关联
class ActivityOrdersCreate(BaseModel):
    activities_id: str
    orders_id: str


class ActivityOrdersDelete(BaseModel):
    activities_id: str
    orders_id: Optional[str] = None


class ActivityOrdersQuery(BaseModel):
    activities_id: Optional[str] = None
    orders_id: Optional[str] = None
    page: int = 1
    page_size: int = 20
