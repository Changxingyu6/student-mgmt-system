"""
订单模块数据校验 Schema
定义请求和响应的数据结构
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ========== 订单主表 Schema ==========

class OrderItemCreate(BaseModel):
    """创建订单时的商品项"""
    product_id: str = Field(..., description="商品ID")
    quantity: int = Field(..., gt=0, description="购买数量")


class OrderCreateRequest(BaseModel):
    """创建订单请求"""
    address_id: str = Field(..., description="收货地址ID")
    coupon_id: Optional[str] = Field(None, description="优惠券ID")
    items: List[OrderItemCreate] = Field(..., description="商品列表")
    payment_method: str = Field(..., description="支付方式")
    remark: Optional[str] = Field(None, description="订单备注")


class OrderStatusUpdateRequest(BaseModel):
    """修改订单状态请求"""
    order_status: str = Field(..., description="订单状态")
    remark: Optional[str] = Field(None, description="备注")


class OrderResponse(BaseModel):
    """订单响应"""
    id: str = Field(..., description="主键ID")
    order_id: str = Field(..., description="订单编号")
    user_id: str = Field(..., description="用户ID")
    total_amount: float = Field(..., description="订单总金额")
    actual_pay_amount: float = Field(..., description="实付金额")
    coupon_discount: float = Field(..., description="优惠券抵扣")
    member_discount: float = Field(..., description="会员折扣")
    order_status: str = Field(..., description="订单状态")
    pay_status: str = Field(..., description="支付状态")
    logistics_status: str = Field(..., description="物流状态")
    payment_method: str = Field(..., description="支付方式")
    remark: Optional[str] = Field(None, description="订单备注")
    receiver_name: str = Field(..., description="收货人姓名")
    receiver_phone: str = Field(..., description="收货人电话")
    shipping_address: str = Field(..., description="收货地址")
    expire_time: datetime = Field(..., description="失效时间")
    pay_time: Optional[datetime] = Field(None, description="支付时间")
    ship_time: Optional[datetime] = Field(None, description="发货时间")
    receive_time: Optional[datetime] = Field(None, description="签收时间")
    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")


class OrderListResponse(BaseModel):
    """订单列表响应"""
    list: List[OrderResponse] = Field(..., description="订单列表")
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页数量")


# ========== 订单明细表 Schema ==========

class OrderItemResponse(BaseModel):
    """订单明细响应"""
    id: str = Field(..., description="主键ID")
    order_id: str = Field(..., description="订单编号")
    product_id: str = Field(..., description="商品ID")
    product_name: str = Field(..., description="商品名称")
    spec_info: Optional[str] = Field(None, description="规格信息")
    product_image: Optional[str] = Field(None, description="商品图片")
    quantity: int = Field(..., description="购买数量")
    total_amount: float = Field(..., description="总计金额")
    item_remark: Optional[str] = Field(None, description="商品明细备注")
    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")


class OrderItemListResponse(BaseModel):
    """订单明细列表响应"""
    list: List[OrderItemResponse] = Field(..., description="订单明细列表")
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页数量")


# ========== 售后订单表 Schema ==========

class AfterSaleCreateRequest(BaseModel):
    """创建售后申请请求"""
    order_id: str = Field(..., description="订单编号")
    product_id: str = Field(..., description="商品ID")
    after_sale_type: str = Field(..., description="售后类型：refund-退款，return-退货退款")
    reason: str = Field(..., description="售后原因")
    refund_amount: float = Field(..., gt=0, description="退款金额")
    refund_quantity: int = Field(..., gt=0, description="退款数量")
    remark: Optional[str] = Field(None, description="备注")


class AfterSaleAuditRequest(BaseModel):
    """审核售后订单请求"""
    audit_status: str = Field(..., description="审核状态：approved-通过，rejected-拒绝")
    remark: Optional[str] = Field(None, description="审核备注")


class AfterSaleResponse(BaseModel):
    """售后订单响应"""
    id: str = Field(..., description="主键ID")
    order_id: str = Field(..., description="订单编号")
    user_id: str = Field(..., description="用户ID")
    product_id: str = Field(..., description="商品ID")
    after_sale_type: str = Field(..., description="售后类型")
    reason: str = Field(..., description="售后原因")
    refund_amount: float = Field(..., description="退款金额")
    refund_quantity: int = Field(..., description="退款数量")
    actual_pay_amount: float = Field(..., description="实付金额")
    audit_status: str = Field(..., description="审核状态")
    after_sale_status: int = Field(..., description="1-仅退款 2-全额退款")
    shipping_address: str = Field(..., description="收货地址")
    payment_method: str = Field(..., description="支付方式")
    order_create_time: datetime = Field(..., description="下单时间")
    order_ship_time: Optional[datetime] = Field(None, description="发货时间")
    order_complete_time: Optional[datetime] = Field(None, description="完成时间")
    remark: Optional[str] = Field(None, description="备注")
    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")


class AfterSaleListResponse(BaseModel):
    """售后订单列表响应"""
    list: List[AfterSaleResponse] = Field(..., description="售后订单列表")
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页数量")
