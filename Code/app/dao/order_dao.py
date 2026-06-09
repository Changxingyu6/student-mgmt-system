"""
订单数据访问层
"""
from sqlalchemy.orm import Session
from typing import Optional, Dict
from datetime import datetime, timedelta
from utils.uuid_utils import generate_uuid
from model.order import Order
from model.order_item import OrderItem


def create_order(db: Session, user_id: str, total_amount: float, address_info: Dict) -> Dict:
    """创建订单主表"""
    order_uuid = generate_uuid()
    expire_time = datetime.now() + timedelta(minutes=30)
    order = Order(
        id=order_uuid,
        order_id=order_uuid,  # 直接使用UUID作为订单编号
        user_id=user_id,
        total_amount=total_amount,
        actual_pay_amount=total_amount,
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
        "expire_time": expire_time.strftime("%Y-%m-%d %H:%M:%S")
    }


def create_order_item(db: Session, order_id: str, item_data: Dict) -> Dict:
    """创建订单明细"""
    order_item = OrderItem(
        id=generate_uuid(),
        order_id=order_id,
        product_id=item_data["goods_id"],
        product_name=item_data["goods_name"],
        spec_info=item_data["spec_info"],
        quantity=item_data["buy_num"],
        total_amount=item_data["price"] * item_data["buy_num"]
    )
    db.add(order_item)
    
    return {
        "id": order_item.id,
        "order_id": order_item.order_id,
        "product_id": order_item.product_id
    }