"""物流相关模型"""
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum
from schema.types import IDStr


class Logistics_Status(str, Enum):
    """物流状态枚举"""
    to_be_shipped = '待发货'
    collected = '已揽收'
    in_transit = '运输中'
    out_for_delivery = '派送中'
    signed = '已签收'
    abnormal = '异常'


class IsNormal(str, Enum):
    """是否异常枚举"""
    isnormal = '0'  # 0正常
    unnormal = '1'  # 1异常


class LogisticsRequest(BaseModel):
    """物流请求模型"""
    order_id: IDStr = Field(..., description="订单ID")
    logistics_status: Optional[Logistics_Status] = Field(None, description="物流状态（可选，不传则默认待发货）")
    track_info: str = Field(..., description="物流轨迹信息")
    is_deleted: IsNormal = Field(IsNormal.isnormal, description="是否删除")


class LogisticsUpdate(BaseModel):
    """物流更新模型"""
    logistics_id: IDStr = Field(..., description="物流单ID")
    logistics_status: Logistics_Status = Field(..., description="物流状态")
    track_info: Optional[str] = Field(None, description="物流轨迹信息")
    is_deleted: IsNormal = Field(IsNormal.isnormal, description="是否删除")
