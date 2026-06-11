"""
订单数据访问层
"""
from sqlalchemy.orm import Session
from typing import Optional, Dict
from datetime import datetime, timedelta
from utils.uuid_utils import generate_uuid
from model.order import Order
from model.order_item import OrderItem


def create_order(db: Session, user_id: str, total_amount: float, address_info: Dict, actual_pay_amount: float = None) -> Dict:
    """创建订单主表"""
    order_uuid = generate_uuid()
    expire_time = datetime.now() + timedelta(minutes=30)
    
    # 如果没有传入实际支付金额，使用原价
    if actual_pay_amount is None:
        actual_pay_amount = total_amount
    
    # 保留两位小数
    total_amount = round(total_amount, 2)
    actual_pay_amount = round(actual_pay_amount, 2)
    
    order = Order(
        id=order_uuid,
        order_id=order_uuid,  # 直接使用UUID作为订单编号
        user_id=user_id,
        total_amount=total_amount,
        actual_pay_amount=actual_pay_amount,
        order_status='pending',
        pay_status='unpaid',
        logistics_status='waiting_ship',
        payment_method='balance',
        receiver_name=address_info.get('name', ''),
        receiver_phone=address_info.get('phone', ''),
        shipping_address=address_info.get('address', ''),
        expire_time=expire_time
    )
    db.add(order)
    
    return {
        "id": order_uuid,
        "order_id": order_uuid,
        "total_amount": float(total_amount),
        "actual_pay_amount": float(actual_pay_amount),
        "expire_time": expire_time.strftime("%Y-%m-%d %H:%M:%S")
    }


def create_order_item(db: Session, order_id: str, item_data: Dict) -> bool:
    """创建订单明细"""
    item_uuid = generate_uuid()
    order_item = OrderItem(
        id=item_uuid,
        order_id=order_id,
        product_id=item_data.get('goods_id', ''),
        product_name=item_data.get('goods_name', ''),
        spec_info=item_data.get('spec_info', ''),
        quantity=item_data.get('buy_num', 1),
        total_amount=item_data.get('price', 0) * item_data.get('buy_num', 1)
    )
    db.add(order_item)
    return True


def get_orders_by_user_id(db: Session, user_id: str, order_id=None, order_status=None, pay_status=None, logistics_status=None, start_time=None, end_time=None) -> list:
    """获取用户订单列表（支持筛选）"""
    query = db.query(Order).filter(
        Order.user_id == user_id,
        Order.is_deleted == False
    )
    
    # 添加筛选条件
    if order_id:
        query = query.filter(Order.order_id.like(f"%{order_id}%"))
    if order_status:
        query = query.filter(Order.order_status == order_status)
    if pay_status:
        query = query.filter(Order.pay_status == pay_status)
    if logistics_status:
        query = query.filter(Order.logistics_status == logistics_status)
    if start_time:
        query = query.filter(Order.create_time >= start_time)
    if end_time:
        query = query.filter(Order.create_time <= end_time)
    
    orders = query.order_by(Order.create_time.desc()).all()
    
    result = []
    for order in orders:
        result.append({
            "id": order.id,
            "order_id": order.order_id,
            "user_id": order.user_id,
            "total_amount": float(order.total_amount),
            "actual_pay_amount": float(order.actual_pay_amount) if order.actual_pay_amount else 0,
            "order_status": order.order_status,
            "pay_status": order.pay_status,
            "logistics_status": order.logistics_status,
            "payment_method": order.payment_method,
            "receiver_name": order.receiver_name,
            "receiver_phone": order.receiver_phone,
            "shipping_address": order.shipping_address,
            "create_time": order.create_time.strftime("%Y-%m-%d %H:%M:%S") if order.create_time else None,
            "update_time": order.update_time.strftime("%Y-%m-%d %H:%M:%S") if order.update_time else None,
            "expire_time": order.expire_time.strftime("%Y-%m-%d %H:%M:%S") if order.expire_time else None
        })
    return result


def update_order_status(db: Session, order_id: str, status_data: Dict) -> bool:
    """更新订单状态"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return False
    
    if 'order_status' in status_data:
        order.order_status = status_data['order_status']
    if 'pay_status' in status_data:
        order.pay_status = status_data['pay_status']
    if 'logistics_status' in status_data:
        order.logistics_status = status_data['logistics_status']
    order.update_time = datetime.now()
    
    return True


def get_order_items_by_order_id(db: Session, order_id: str) -> list:
    """获取订单明细"""
    items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
    result = []
    for item in items:
        # 计算单价（总价 / 数量）
        quantity = item.quantity or 1
        total_amount = float(item.total_amount) if item.total_amount else 0
        price = round(total_amount / quantity, 2)
        
        result.append({
            "id": item.id,
            "order_id": item.order_id,
            "product_id": item.product_id,
            "product_name": item.product_name,
            "spec_info": item.spec_info,
            "quantity": item.quantity,
            "price": price,
            "total_amount": total_amount
        })
    return result


def get_order_by_id(db: Session, order_id: str) -> dict:
    """根据订单ID获取订单信息"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return None
    return {
        "id": order.id,
        "order_id": order.order_id,
        "total_amount": float(order.total_amount) if order.total_amount else 0,
        "order_status": order.order_status,
        "pay_status": order.pay_status,
        "logistics_status": order.logistics_status
    }