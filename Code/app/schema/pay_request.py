"""支付相关模型"""
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from decimal import Decimal
from datetime import datetime
from enum import Enum
from schema.types import IDStr


class Pay_Status(str, Enum):
    """支付状态枚举"""
    pending_payment = "待支付"
    processing = "支付中"
    payment_succeeded = "支付成功"
    payment_failed = "支付失败"
    pay_losed = "已关闭"


class IsNormal(str, Enum):
    """是否异常枚举"""
    isnormal = '0'  # 0正常
    unnormal = '1'  # 1异常


class PayRequest(BaseModel):
    """支付记录请求模型"""
    order_id: IDStr = Field(..., description="订单ID")
    user_id: IDStr = Field(..., description="用户ID")
    pay_amount: Decimal = Field(..., gt=0, description="支付金额必须大于0")

    @field_validator("pay_amount")
    @classmethod
    def two_decimals(cls, v: Decimal):
        if v.as_tuple().exponent < -2:
            raise ValueError("金额最多允许两位小数")
        return v


class Payupdata(BaseModel):
    """支付更新模型"""
    pay_id: IDStr = Field(..., description="支付单ID")
    # pay_time: Optional[datetime] = Field(None, description="支付时间")
    pay_status: Pay_Status = Field(Pay_Status.pending_payment, description="支付状态")
    is_abnormal: IsNormal = Field(IsNormal.isnormal, description="是否异常")
    is_deleted: IsNormal = Field(IsNormal.isnormal, description="是否删除")


class PaymentRequest(BaseModel):
    """支付请求模型"""
    pay_id: IDStr = Field(..., description="支付单ID")
    user_id: IDStr = Field(..., description="用户ID")
    pay_amount: Optional[Decimal] = Field(None, description="支付金额（可选，不传则从支付记录获取）")
    pay_password: str = Field(..., min_length=1, description="支付密码")
    coupon_id: Optional[IDStr] = Field(None, description="优惠券ID（可选）")
