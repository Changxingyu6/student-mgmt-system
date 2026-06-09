"""退货物流相关模型"""
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum
from schema.types import IDStr


class Return_Logistics_Status(str, Enum):
    """退货物流状态枚举"""
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


class Return_LogisticsRequest(BaseModel):
    """退货物流请求模型"""
    after_sales_id: IDStr = Field(..., description="售后单ID")
    order_id: IDStr = Field(..., description="订单ID")
    return_logistics_status: Return_Logistics_Status = Field(..., description="退货物流状态")
    return_track_info: str = Field(..., description="退货物流轨迹信息")
    is_deleted: IsNormal = Field(IsNormal.isnormal, description="是否删除")


class Return_LogisticsUpdate(BaseModel):
    """退货物流更新模型"""
    return_logistics_id: IDStr = Field(..., description="退货物流单ID")
    return_logistics_status: Return_Logistics_Status = Field(..., description="退货物流状态")
    return_track_info: Optional[str] = Field(None, description="退货物流轨迹信息")
    is_deleted: IsNormal = Field(IsNormal.isnormal, description="是否删除")
