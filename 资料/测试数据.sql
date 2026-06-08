-- ============================================
-- 测试数据
-- ============================================

USE ecommerce_db;

-- ============================================
-- 1. 角色表测试数据
-- ============================================
INSERT INTO roles (id, role_name, description, status, create_time, update_time) VALUES
('r-001', 'admin', '系统管理员', 'active', NOW(), NOW()),
('r-002', 'user', '普通用户', 'active', NOW(), NOW()),
('r-003', 'vip', 'VIP会员', 'active', NOW(), NOW());

-- ============================================
-- 2. 用户表测试数据
-- 注意：密码为 MD5(salt + "123456")，所有用户密码都是 123456
-- ============================================
INSERT INTO users (id, username, password, salt, nickname, phone, email, gender, user_level, balance, status, role_id, create_time, update_time) VALUES
('u-admin001', 'admin', 'c1ad4b548d7034415bb2d2ef0a44c204', 'adminSalt123', '系统管理员', '13800000001', 'admin@example.com', 'male', '黄金会员', 10000.00, 'active', 'r-001', NOW(), NOW()),
('u-user001', 'user1', 'd9a2905e81a119a573ac7b139316aa80', 'user1Salt123', '张三', '13800000002', 'zhangsan@example.com', 'male', '白银会员', 5000.00, 'active', 'r-002', NOW(), NOW()),
('u-user002', 'user2', 'd3844cfc49293676b63aa3921700e718', 'user2Salt123', '李四', '13800000003', 'lisi@example.com', 'female', '青铜会员', 1000.00, 'active', 'r-002', NOW(), NOW()),
('u-user003', 'vipuser', 'a18cb43caee770d5fbfa1d1808386c8f', 'vipSalt123', '王五', '13800000004', 'wangwu@example.com', 'male', '黄金会员', 50000.00, 'active', 'r-003', NOW(), NOW()),
('u-user004', 'testuser', 'c493ea81abaabb5369815f26dff96bea', 'testSalt123', '测试用户', '13800000005', 'test@example.com', 'other', '青铜会员', 100.00, 'active', 'r-002', NOW(), NOW()),
('u-user005', 'frozenuser', '13b9571ef3b795ead7aaadc27ecf3bb4', 'frozenSalt', '冻结用户', '13800000006', 'frozen@example.com', 'female', '青铜会员', 500.00, 'frozen', 'r-002', NOW(), NOW());

-- ============================================
-- 3. 用户收货地址表测试数据
-- ============================================
INSERT INTO user_addresses (id, user_id, receiver_name, receiver_phone, province, city, district, detail_address, is_default, create_time, update_time) VALUES
('addr-001', 'u-user001', '张三', '13800000002', '北京市', '北京市', '朝阳区', '建国路88号SOHO现代城1号楼1501', 1, NOW(), NOW()),
('addr-002', 'u-user001', '张三', '13800000002', '北京市', '北京市', '海淀区', '中关村大街1号院2号楼302', 0, NOW(), NOW()),
('addr-003', 'u-user002', '李四', '13800000003', '上海市', '上海市', '浦东新区', '陆家嘴环路1000号IFC大厦1楼', 1, NOW(), NOW()),
('addr-004', 'u-user003', '王五', '13800000004', '广东省', '深圳市', '南山区', '科技园南区高新南七道R2-B栋3楼', 1, NOW(), NOW()),
('addr-005', 'u-user004', '测试用户', '13800000005', '浙江省', '杭州市', '西湖区', '文三路398号东信大厦1403', 1, NOW(), NOW());

-- ============================================
-- 4. 商品分类表测试数据
-- ============================================
INSERT INTO category (id, name, parent_id, sort_order, status, create_time, update_time) VALUES
('cat-001', '手机数码', '0', 1, 1, NOW(), NOW()),
('cat-002', '电脑办公', '0', 2, 1, NOW(), NOW()),
('cat-003', '服装鞋帽', '0', 3, 1, NOW(), NOW()),
('cat-004', '家用电器', '0', 4, 1, NOW(), NOW()),
('cat-005', '食品生鲜', '0', 5, 1, NOW(), NOW()),
('cat-006', '智能手机', 'cat-001', 1, 1, NOW(), NOW()),
('cat-007', '平板电脑', 'cat-001', 2, 1, NOW(), NOW()),
('cat-008', '游戏手机', 'cat-001', 3, 1, NOW(), NOW()),
('cat-009', '笔记本电脑', 'cat-002', 1, 1, NOW(), NOW()),
('cat-010', '台式机', 'cat-002', 2, 1, NOW(), NOW());

-- ============================================
-- 5. 品牌表测试数据
-- ============================================
INSERT INTO brand (id, name, origin, logo, create_time, update_time) VALUES
('brand-001', '苹果', '美国', '/static/brand/apple.png', NOW(), NOW()),
('brand-002', '华为', '中国', '/static/brand/huawei.png', NOW(), NOW()),
('brand-003', '小米', '中国', '/static/brand/xiaomi.png', NOW(), NOW()),
('brand-004', '联想', '中国', '/static/brand/lenovo.png', NOW(), NOW()),
('brand-005', '戴尔', '美国', '/static/brand/dell.png', NOW(), NOW()),
('brand-006', '耐克', '美国', '/static/brand/nike.png', NOW(), NOW()),
('brand-007', '阿迪达斯', '德国', '/static/brand/adidas.png', NOW(), NOW()),
('brand-008', '美的', '中国', '/static/brand/midea.png', NOW(), NOW());

-- ============================================
-- 6. 商品主表测试数据
-- ============================================
INSERT INTO product (id, name, category_id, brand_id, brief, main_image, status, create_time, update_time) VALUES
('prod-001', 'iPhone 15 Pro Max', 'cat-006', 'brand-001', '苹果旗舰手机，A17 Pro芯片，钛金属设计', '/static/products/iphone15.jpg', 1, NOW(), NOW()),
('prod-002', '华为Mate 60 Pro', 'cat-006', 'brand-002', '华为旗舰手机，麒麟9000S芯片', '/static/products/mate60.jpg', 1, NOW(), NOW()),
('prod-003', '小米14 Ultra', 'cat-006', 'brand-003', '小米旗舰手机，骁龙8 Gen3处理器', '/static/products/xiaomi14.jpg', 1, NOW(), NOW()),
('prod-004', 'MacBook Pro 14', 'cat-009', 'brand-001', '苹果笔记本电脑，M3 Pro芯片', '/static/products/macbook14.jpg', 1, NOW(), NOW()),
('prod-005', 'ThinkPad X1 Carbon', 'cat-009', 'brand-004', '联想商务笔记本，轻薄便携', '/static/products/thinkpad.jpg', 1, NOW(), NOW()),
('prod-006', 'Nike Air Max 270', 'cat-003', 'brand-006', '耐克气垫运动鞋，舒适缓震', '/static/products/airmax.jpg', 1, NOW(), NOW()),
('prod-007', '美的变频空调', 'cat-004', 'brand-008', '美的1.5匹变频空调，智能控制', '/static/products/midea-ac.jpg', 1, NOW(), NOW()),
('prod-008', 'iPad Pro 12.9', 'cat-007', 'brand-001', '苹果平板电脑，M2芯片，全面屏设计', '/static/products/ipad-pro.jpg', 1, NOW(), NOW());

-- ============================================
-- 7. 规格表测试数据
-- ============================================
INSERT INTO specification (id, name, sort_order, create_time, update_time) VALUES
('spec-001', '颜色', 1, NOW(), NOW()),
('spec-002', '内存', 2, NOW(), NOW()),
('spec-003', '存储', 3, NOW(), NOW());

-- ============================================
-- 8. 商品SKU表测试数据
-- ============================================
INSERT INTO product_sku (id, product_id, spec_values, price, stock, warn_stock, create_time, update_time) VALUES
-- iPhone 15 Pro Max SKU
('sku-001', 'prod-001', '{"颜色":"黑色钛金属","内存":"8GB","存储":"256GB"}', 9999.00, 100, 10, NOW(), NOW()),
('sku-002', 'prod-001', '{"颜色":"白色钛金属","内存":"8GB","存储":"256GB"}', 9999.00, 80, 10, NOW(), NOW()),
('sku-003', 'prod-001', '{"颜色":"蓝色钛金属","内存":"8GB","存储":"512GB"}', 11999.00, 50, 10, NOW(), NOW()),
('sku-004', 'prod-001', '{"颜色":"原色钛金属","内存":"8GB","存储":"1TB"}', 13999.00, 30, 5, NOW(), NOW()),

-- 华为Mate 60 Pro SKU
('sku-005', 'prod-002', '{"颜色":"雅丹黑","内存":"12GB","存储":"256GB"}', 6999.00, 150, 15, NOW(), NOW()),
('sku-006', 'prod-002', '{"颜色":"雅川青","内存":"12GB","存储":"512GB"}', 7999.00, 120, 15, NOW(), NOW()),

-- 小米14 Ultra SKU
('sku-007', 'prod-003', '{"颜色":"白色","内存":"16GB","存储":"512GB"}', 6999.00, 200, 20, NOW(), NOW()),
('sku-008', 'prod-003', '{"颜色":"黑色","内存":"16GB","存储":"1TB"}', 7999.00, 100, 10, NOW(), NOW()),

-- MacBook Pro 14 SKU
('sku-009', 'prod-004', '{"颜色":"银色","内存":"18GB","存储":"512GB"}', 16999.00, 50, 5, NOW(), NOW()),
('sku-010', 'prod-004', '{"颜色":"深空黑色","内存":"36GB","存储":"1TB"}', 22999.00, 30, 3, NOW(), NOW()),

-- ThinkPad X1 Carbon SKU
('sku-011', 'prod-005', '{"颜色":"黑色","内存":"16GB","存储":"512GB"}', 9999.00, 80, 10, NOW(), NOW()),
('sku-012', 'prod-005', '{"颜色":"黑色","内存":"32GB","存储":"1TB"}', 12999.00, 40, 5, NOW(), NOW()),

-- Nike Air Max SKU
('sku-013', 'prod-006', '{"颜色":"黑色","内存":"40码"}', 899.00, 300, 30, NOW(), NOW()),
('sku-014', 'prod-006', '{"颜色":"白色","内存":"41码"}', 899.00, 250, 30, NOW(), NOW()),
('sku-015', 'prod-006', '{"颜色":"红色","内存":"42码"}', 899.00, 200, 20, NOW(), NOW()),

-- 美的空调 SKU
('sku-016', 'prod-007', '{"颜色":"白色","内存":"1.5匹"}', 2999.00, 150, 15, NOW(), NOW()),
('sku-017', 'prod-007', '{"颜色":"金色","内存":"2匹"}', 3999.00, 100, 10, NOW(), NOW()),

-- iPad Pro SKU
('sku-018', 'prod-008', '{"颜色":"深空灰","内存":"8GB","存储":"256GB"}', 9299.00, 100, 10, NOW(), NOW()),
('sku-019', 'prod-008', '{"颜色":"银色","内存":"16GB","存储":"1TB"}', 13999.00, 50, 5, NOW(), NOW());

-- ============================================
-- 9. 优惠券表测试数据
-- ============================================
INSERT INTO coupons (id, coupons_no, coupons_name, type, face_value, min_spend, total_count, sent_count, used_count, valid_start_time, valid_end_time, status, create_time, update_time) VALUES
('coupon-001', 'COUP20240001', '新人满减券', 1, 50.00, 200.00, 1000, 500, 100, '2024-01-01 00:00:00', '2025-12-31 23:59:59', 1, NOW(), NOW()),
('coupon-002', 'COUP20240002', '95折折扣券', 2, 0.95, 100.00, 2000, 1000, 200, '2024-01-01 00:00:00', '2025-12-31 23:59:59', 1, NOW(), NOW()),
('coupon-003', 'COUP20240003', '无门槛10元券', 3, 10.00, 0.00, 5000, 2000, 500, '2024-01-01 00:00:00', '2025-12-31 23:59:59', 1, NOW(), NOW()),
('coupon-004', 'COUP20240004', '手机专享券', 1, 100.00, 500.00, 500, 200, 50, '2024-01-01 00:00:00', '2025-12-31 23:59:59', 1, NOW(), NOW());

-- ============================================
-- 10. 用户优惠券表测试数据
-- ============================================
INSERT INTO user_coupons (id, coupon_id, user_id, coupon_no, status, get_time, valid_end_time, create_time, update_time) VALUES
('uc-001', 'coupon-001', 'u-user001', 'UC20240001', 0, NOW(), '2025-12-31 23:59:59', NOW(), NOW()),
('uc-002', 'coupon-002', 'u-user001', 'UC20240002', 1, NOW(), '2025-12-31 23:59:59', NOW(), NOW()),
('uc-003', 'coupon-003', 'u-user002', 'UC20240003', 0, NOW(), '2025-12-31 23:59:59', NOW(), NOW()),
('uc-004', 'coupon-004', 'u-user003', 'UC20240004', 0, NOW(), '2025-12-31 23:59:59', NOW(), NOW());

-- ============================================
-- 11. 购物车主表测试数据
-- ============================================
INSERT INTO shopping_cart (cart_id, user_id, is_active, create_time, update_time) VALUES
('cart-001', 'u-user001', 1, NOW(), NOW()),
('cart-002', 'u-user002', 1, NOW(), NOW()),
('cart-003', 'u-user003', 1, NOW(), NOW());

-- ============================================
-- 12. 购物车项表测试数据
-- ============================================
INSERT INTO shopping_cart_item (item_id, cart_id, goods_id, spec_id, buy_num, is_checked, create_time, update_time) VALUES
('sci-001', 'cart-001', 'prod-001', 'sku-001', 1, 1, NOW(), NOW()),
('sci-002', 'cart-001', 'prod-004', 'sku-009', 1, 1, NOW(), NOW()),
('sci-003', 'cart-001', 'prod-006', 'sku-013', 2, 0, NOW(), NOW()),
('sci-004', 'cart-002', 'prod-002', 'sku-005', 1, 1, NOW(), NOW()),
('sci-005', 'cart-002', 'prod-003', 'sku-007', 1, 0, NOW(), NOW()),
('sci-006', 'cart-003', 'prod-008', 'sku-018', 1, 1, NOW(), NOW());

-- ============================================
-- 13. 订单主表测试数据
-- ============================================
INSERT INTO orders (id, order_id, user_id, total_amount, actual_pay_amount, coupon_discount, member_discount, order_status, pay_status, logistics_status, payment_method, remark, receiver_name, receiver_phone, shipping_address, expire_time, pay_time, ship_time, receive_time, create_time, update_time) VALUES
('order-001', 'ORD20240608001', 'u-user001', 26998.00, 25998.00, 0.00, 1000.00, 'completed', 'paid', 'received', '余额', '尽快发货', '张三', '13800000002', '北京市朝阳区建国路88号SOHO现代城1号楼1501', DATE_ADD(NOW(), INTERVAL 30 MINUTE), NOW(), DATE_SUB(NOW(), INTERVAL 2 DAY), DATE_SUB(NOW(), INTERVAL 1 DAY), NOW(), NOW()),
('order-002', 'ORD20240608002', 'u-user002', 6999.00, 6949.00, 50.00, 0.00, 'shipped', 'paid', 'shipping', '余额', '', '李四', '13800000003', '上海市浦东新区陆家嘴环路1000号IFC大厦1楼', DATE_ADD(NOW(), INTERVAL 30 MINUTE), NOW(), NOW(), NULL, NOW(), NOW()),
('order-003', 'ORD20240608003', 'u-user003', 13999.00, 13999.00, 0.00, 0.00, 'pending', 'paid', 'waiting_ship', '余额', '开发票', '王五', '13800000004', '广东省深圳市南山区科技园南区高新南七道R2-B栋3楼', DATE_ADD(NOW(), INTERVAL 30 MINUTE), NOW(), NULL, NULL, NOW(), NOW());

-- ============================================
-- 14. 订单明细表测试数据
-- ============================================
INSERT INTO order_items (id, order_id, product_id, product_name, spec_info, product_image, quantity, total_amount, create_time, update_time) VALUES
('oi-001', 'order-001', 'prod-001', 'iPhone 15 Pro Max', '{"颜色":"黑色钛金属","内存":"8GB","存储":"256GB"}', '/static/products/iphone15.jpg', 1, 9999.00, NOW(), NOW()),
('oi-002', 'order-001', 'prod-004', 'MacBook Pro 14', '{"颜色":"银色","内存":"18GB","存储":"512GB"}', '/static/products/macbook14.jpg', 1, 16999.00, NOW(), NOW()),
('oi-003', 'order-002', 'prod-002', '华为Mate 60 Pro', '{"颜色":"雅丹黑","内存":"12GB","存储":"256GB"}', '/static/products/mate60.jpg', 1, 6999.00, NOW(), NOW()),
('oi-004', 'order-003', 'prod-008', 'iPad Pro 12.9', '{"颜色":"深空灰","内存":"8GB","存储":"256GB"}', '/static/products/ipad-pro.jpg', 1, 13999.00, NOW(), NOW());

-- ============================================
-- 15. 支付记录表测试数据
-- ============================================
INSERT INTO payments (pay_id, pay_no, order_id, user_id, pay_status, pay_amount, pay_method, pay_time, expire_time, create_time, update_time) VALUES
('pay-001', 'PAY20240608001', 'order-001', 'u-user001', '支付成功', 25998.00, '余额', NOW(), DATE_ADD(NOW(), INTERVAL 30 MINUTE), NOW(), NOW()),
('pay-002', 'PAY20240608002', 'order-002', 'u-user002', '支付成功', 6949.00, '余额', NOW(), DATE_ADD(NOW(), INTERVAL 30 MINUTE), NOW(), NOW()),
('pay-003', 'PAY20240608003', 'order-003', 'u-user003', '支付成功', 13999.00, '余额', NOW(), DATE_ADD(NOW(), INTERVAL 30 MINUTE), NOW(), NOW());

-- ============================================
-- 16. 物流表测试数据
-- ============================================
INSERT INTO logistics (logistics_id, order_id, logistics_no, logistics_status, track_info, create_time, update_time) VALUES
('log-001', 'order-001', 'SF1234567890', '已签收', '[{"status":"已签收","time":"2024-06-07 18:00:00","desc":"快件已签收，签收人：本人"},{"status":"派送中","time":"2024-06-07 12:00:00","desc":"快递员正在派送中"},{"status":"运输中","time":"2024-06-06 20:00:00","desc":"快件已到达北京分拨中心"},{"status":"已揽收","time":"2024-06-05 10:00:00","desc":"顺丰速运已收件"}]', NOW(), NOW()),
('log-002', 'order-002', 'YT9876543210', '运输中', '[{"status":"运输中","time":"2024-06-08 08:00:00","desc":"快件已发出，正在运输途中"},{"status":"已揽收","time":"2024-06-07 15:00:00","desc":"圆通速递已揽收"}]', NOW(), NOW());

-- ============================================
-- 17. 售后订单表测试数据
-- ============================================
INSERT INTO after_sales (id, order_id, user_id, product_id, after_sale_type, reason, refund_amount, refund_quantity, actual_pay_amount, audit_status, after_sale_status, shipping_address, payment_method, order_create_time, remark, create_time, update_time) VALUES
('as-001', 'order-001', 'u-user001', 'prod-004', '退货退款', '屏幕有坏点', 16999.00, 1, 16999.00, 'approved', 2, '北京市朝阳区建国路88号SOHO现代城1号楼1501', '余额', NOW(), '请尽快处理', NOW(), NOW());

-- ============================================
-- 18. 退款记录表测试数据
-- ============================================
INSERT INTO refund (refund_id, refund_no, after_sales_id, refund_status, refund_amount, refund_method, refund_time, create_time, update_time) VALUES
('refund-001', 'REF20240608001', 'as-001', '退款成功', 16999.00, '余额', NOW(), NOW(), NOW());

-- ============================================
-- 19. 退货物流表测试数据
-- ============================================
INSERT INTO return_logistics (return_logistics_id, after_sales_id, return_logistics_no, return_logistics_status, return_track_info, create_time, update_time) VALUES
('rlog-001', 'as-001', 'SF0987654321', '待发货', NULL, NOW(), NOW());

-- ============================================
-- 20. 优惠券使用日志测试数据
-- ============================================
INSERT INTO coupon_use_log (id, user_coupon_id, user_id, order_id, status, remark, create_time) VALUES
('clog-001', 'uc-002', 'u-user001', 'order-001', 1, '订单使用优惠券', NOW());
