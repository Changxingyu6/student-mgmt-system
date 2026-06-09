"""
四个模块测试数据
包含：支付模块、退款模块、物流模块、退货物流模块
"""

import uuid

# ==================== 支付模块测试数据 ====================
pay_test_data = {
    # 创建支付记录 - POST /pay_api/pay
    "create_pay": {
        "order_id": str(uuid.uuid4()),
        "user_id": str(uuid.uuid4()),
        "pay_amount": 99.99,
        "pay_method": "余额"
    },
    
    # 查询支付记录 - GET /pay_api/pay/{order_id}
    "query_pay": {
        "order_id": "test-order-001"  # 替换为实际创建后的 order_id
    },
    
    # 更新支付记录 - PUT /pay_api/pay
    "update_pay": {
        "pay_id": "test-pay-001",  # 替换为实际创建后的 pay_id
        "pay_status": "支付成功",
        "pay_time": "2024-01-15 10:30:00"
    },
    
    # 删除支付记录 - DELETE /pay_api/pay/{order_id}
    "delete_pay": {
        "order_id": "test-order-001"  # 替换为实际创建后的 order_id
    },
    
    # 处理支付 - POST /pay_api/pay/process
    "process_pay": {
        "pay_id": "test-pay-001",  # 替换为实际创建后的 pay_id
        "user_id": str(uuid.uuid4()),
        "pay_password": "e10adc3949ba59abbe56e057f20f883e"  # MD5: 123456
    }
}

# ==================== 退款模块测试数据 ====================
refund_test_data = {
    # 创建退款记录 - POST /refund_api/refund
    "create_refund": {
        "after_sales_id": str(uuid.uuid4()),
        "refund_amount": 50.00,
        "refund_method": "余额"
    },
    
    # 查询退款记录 - GET /refund_api/refund/{refund_id}
    "query_refund": {
        "refund_id": "test-refund-001"  # 替换为实际创建后的 refund_id
    },
    
    # 更新退款记录 - PUT /refund_api/refund
    "update_refund": {
        "refund_id": "test-refund-001",  # 替换为实际创建后的 refund_id
        "refund_status": "退款成功",
        "refund_time": "2024-01-15 11:00:00"
    },
    
    # 删除退款记录 - DELETE /refund_api/refund/{refund_id}
    "delete_refund": {
        "refund_id": "test-refund-001"  # 替换为实际创建后的 refund_id
    }
}

# ==================== 物流模块测试数据 ====================
logistics_test_data = {
    # 创建物流记录 - POST /logistics_api/logistics
    "create_logistics": {
        "order_id": str(uuid.uuid4()),
        "logistics_status": "待发货",
        "track_info": "等待商家发货"
    },
    
    # 查询物流记录 - GET /logistics_api/logistics/{logistics_id}
    "query_logistics": {
        "logistics_id": "test-logistics-001"  # 替换为实际创建后的 logistics_id
    },
    
    # 按订单查询物流 - GET /logistics_api/logistics/order/{order_id}
    "query_logistics_by_order": {
        "order_id": "test-order-001"  # 替换为实际的 order_id
    },
    
    # 更新物流记录 - PUT /logistics_api/logistics
    "update_logistics": {
        "logistics_id": "test-logistics-001",  # 替换为实际创建后的 logistics_id
        "logistics_status": "运输中",
        "track_info": "已到达北京转运中心"
    },
    
    # 删除物流记录 - DELETE /logistics_api/logistics/{logistics_id}
    "delete_logistics": {
        "logistics_id": "test-logistics-001"  # 替换为实际创建后的 logistics_id
    }
}

# ==================== 退货物流模块测试数据 ====================
return_logistics_test_data = {
    # 创建退货物流记录 - POST /return_logistics_api/return_logistics
    "create_return_logistics": {
        "after_sales_id": str(uuid.uuid4()),
        "return_logistics_status": "待发货",
        "return_track_info": "等待用户发货"
    },
    
    # 查询退货物流记录 - GET /return_logistics_api/return_logistics/{return_logistics_id}
    "query_return_logistics": {
        "return_logistics_id": "test-return-logistics-001"  # 替换为实际创建后的 ID
    },
    
    # 按售后ID查询 - GET /return_logistics_api/return_logistics/after_sales/{after_sales_id}
    "query_return_logistics_by_after_sales": {
        "after_sales_id": "test-after-sales-001"  # 替换为实际的 after_sales_id
    },
    
    # 更新退货物流记录 - PUT /return_logistics_api/return_logistics
    "update_return_logistics": {
        "return_logistics_id": "test-return-logistics-001",  # 替换为实际创建后的 ID
        "return_logistics_status": "运输中",
        "return_track_info": "已到达商家仓库"
    },
    
    # 删除退货物流记录 - DELETE /return_logistics_api/return_logistics/{return_logistics_id}
    "delete_return_logistics": {
        "return_logistics_id": "test-return-logistics-001"  # 替换为实际创建后的 ID
    }
}

# ==================== 测试数据汇总 ====================
test_data = {
    "pay": pay_test_data,
    "refund": refund_test_data,
    "logistics": logistics_test_data,
    "return_logistics": return_logistics_test_data
}

if __name__ == "__main__":
    import json
    print("=== 四个模块测试数据 ===")
    print(json.dumps(test_data, ensure_ascii=False, indent=2))
