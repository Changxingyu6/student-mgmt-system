"""退款相关模型"""
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from decimal import Decimal
from datetime import datetime
from enum import Enum
from schema.types import IDStr


class Refund_Status(str, Enum):
    """退款状态枚举"""
    pending_refund = "待退款"
    refunding = "退款中"
    refund_success = "退款成功"
    refund_failed = "退款失败"


class IsNormal(str, Enum):
    """是否异常枚举"""
    isnormal = '0'  # 0正常
    unnormal = '1'  # 1异常


class RefundRequest(BaseModel):
    """退款请求模型"""
    after_sales_id: IDStr = Field(..., description="售后单ID")
    order_id: IDStr = Field(..., description="订单ID")
    user_id: IDStr = Field(..., description="用户ID")
    refund_amount: Decimal = Field(..., gt=0, description="退款金额必须大于0")

    @field_validator("refund_amount")
    @classmethod
    def two_decimals(cls, v: Decimal):
        if v.as_tuple().exponent < -2:
            raise ValueError("金额最多允许两位小数")
        return v


class RefundUpdate(BaseModel):
    """退款更新模型"""
    refund_id: IDStr = Field(..., description="退款单ID")
    refund_status: Refund_Status = Field(Refund_Status.pending_refund, description="退款状态")
    refund_time: Optional[datetime] = Field(None, description="退款时间")
    is_abnormal: IsNormal = Field(IsNormal.isnormal, description="是否异常")
    is_deleted: IsNormal = Field(IsNormal.isnormal, description="是否删除")
