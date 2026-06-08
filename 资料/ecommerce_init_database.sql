-- 电商管理平台 - 数据库初始化脚本
-- 在MySQL中执行此脚本创建数据库和表

-- 创建数据库
CREATE DATABASE IF NOT EXISTS ecommerce_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE ecommerce_db;

-- ========================================
-- 电商管理平台数据库表结构
-- ========================================

-- 1. 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    password VARCHAR(32) NOT NULL COMMENT '密码（MD5加密，32位）',
    salt VARCHAR(32) NOT NULL COMMENT '加密盐值',
    nickname VARCHAR(50) COMMENT '昵称',
    phone VARCHAR(20) COMMENT '手机号',
    email VARCHAR(100) COMMENT '邮箱',
    gender ENUM('male','female','other') COMMENT '性别',
    avatar VARCHAR(255) COMMENT '头像URL',
    user_level ENUM('bronze','silver','gold','platinum','diamond') DEFAULT 'bronze' COMMENT '用户等级',
    points INT DEFAULT 0 COMMENT '会员积分',
    default_address_id INT COMMENT '默认收货地址ID',
    status ENUM('active','inactive','banned') DEFAULT 'active' COMMENT '账号状态',
    is_deleted BOOLEAN DEFAULT FALSE COMMENT '逻辑删除',
    failed_attempts INT DEFAULT 0 COMMENT '连续登录失败次数',
    lock_until DATETIME COMMENT '账户锁定截止时间',
    lock_count INT DEFAULT 0 COMMENT '连续锁定次数（用于阶梯式锁定）',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_username (username),
    INDEX idx_phone (phone),
    INDEX idx_status (status),
    INDEX idx_level (user_level)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 2. 收货地址表
CREATE TABLE IF NOT EXISTS user_addresses (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '地址ID',
    user_id INT NOT NULL COMMENT '用户ID',
    receiver_name VARCHAR(50) NOT NULL COMMENT '收货人姓名',
    receiver_phone VARCHAR(20) NOT NULL COMMENT '收货人电话',
    province VARCHAR(50) COMMENT '省份',
    city VARCHAR(50) COMMENT '城市',
    district VARCHAR(50) COMMENT '区县',
    detail_address VARCHAR(255) NOT NULL COMMENT '详细地址',
    is_default BOOLEAN DEFAULT FALSE COMMENT '是否默认地址',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户收货地址表';

-- 3. 商品分类表
CREATE TABLE IF NOT EXISTS goods_categories (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '分类ID',
    parent_id INT DEFAULT 0 COMMENT '父分类ID，0为一级分类',
    category_name VARCHAR(50) NOT NULL COMMENT '分类名称',
    sort_order INT DEFAULT 0 COMMENT '排序',
    icon VARCHAR(255) COMMENT '分类图标',
    status ENUM('active','disabled') DEFAULT 'active' COMMENT '状态',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_parent_id (parent_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品分类表';

-- 4. 商品表
CREATE TABLE IF NOT EXISTS goods (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '商品ID',
    goods_no VARCHAR(50) NOT NULL UNIQUE COMMENT '商品编号',
    goods_name VARCHAR(100) NOT NULL COMMENT '商品名称',
    category_id INT COMMENT '分类ID',
    brand VARCHAR(50) COMMENT '品牌',
    origin VARCHAR(50) COMMENT '产地',
    sale_price DECIMAL(10,2) NOT NULL COMMENT '售价',
    original_price DECIMAL(10,2) COMMENT '原价',
    cost_price DECIMAL(10,2) COMMENT '成本价',
    description TEXT COMMENT '商品简介',
    main_image VARCHAR(255) COMMENT '主图',
    detail_images TEXT COMMENT '详情图（JSON数组）',
    stock INT DEFAULT 0 COMMENT '库存数量',
    stock_warning INT DEFAULT 10 COMMENT '预警库存',
    status ENUM('on_sale','off_sale') DEFAULT 'on_sale' COMMENT '上架状态',
    is_deleted BOOLEAN DEFAULT FALSE COMMENT '逻辑删除',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (category_id) REFERENCES goods_categories(id),
    INDEX idx_category (category_id),
    INDEX idx_status (status),
    INDEX idx_stock (stock)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品表';

-- 5. 商品规格表
CREATE TABLE IF NOT EXISTS goods_specs (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '规格ID',
    goods_id INT NOT NULL COMMENT '商品ID',
    spec_name VARCHAR(50) NOT NULL COMMENT '规格名称（如：颜色）',
    spec_value VARCHAR(50) NOT NULL COMMENT '规格值（如：红色）',
    stock INT DEFAULT 0 COMMENT '该规格库存',
    price_diff DECIMAL(10,2) DEFAULT 0 COMMENT '价格差异',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (goods_id) REFERENCES goods(id) ON DELETE CASCADE,
    INDEX idx_goods_id (goods_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品规格表';

-- 6. 订单表
CREATE TABLE IF NOT EXISTS orders (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '订单ID',
    order_no VARCHAR(50) NOT NULL UNIQUE COMMENT '订单编号',
    user_id INT NOT NULL COMMENT '用户ID',
    total_amount DECIMAL(10,2) NOT NULL COMMENT '订单总金额',
    pay_amount DECIMAL(10,2) COMMENT '实付金额',
    coupon_id INT COMMENT '使用的优惠券ID',
    coupon_discount DECIMAL(10,2) DEFAULT 0 COMMENT '优惠券抵扣金额',
    receiver_name VARCHAR(50) NOT NULL COMMENT '收货人姓名',
    receiver_phone VARCHAR(20) NOT NULL COMMENT '收货人电话',
    receiver_address VARCHAR(255) NOT NULL COMMENT '收货地址',
    order_status ENUM('pending','confirmed','shipped','received','completed','cancelled','closed') DEFAULT 'pending' COMMENT '订单状态',
    pay_status ENUM('unpaid','paid','refunded') DEFAULT 'unpaid' COMMENT '支付状态',
    logistics_status ENUM('unshipped','shipped','signed') DEFAULT 'unshipped' COMMENT '物流状态',
    remark VARCHAR(255) COMMENT '订单备注',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '下单时间',
    paid_at DATETIME COMMENT '支付时间',
    shipped_at DATETIME COMMENT '发货时间',
    received_at DATETIME COMMENT '签收时间',
    completed_at DATETIME COMMENT '完成时间',
    is_deleted BOOLEAN DEFAULT FALSE COMMENT '逻辑删除',
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_id (user_id),
    INDEX idx_order_no (order_no),
    INDEX idx_status (order_status),
    INDEX idx_pay_status (pay_status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单表';

-- 7. 订单商品明细表
CREATE TABLE IF NOT EXISTS order_items (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '明细ID',
    order_id INT NOT NULL COMMENT '订单ID',
    goods_id INT NOT NULL COMMENT '商品ID',
    goods_name VARCHAR(100) NOT NULL COMMENT '商品名称（快照）',
    goods_image VARCHAR(255) COMMENT '商品图片（快照）',
    spec_info VARCHAR(255) COMMENT '规格信息（快照）',
    price DECIMAL(10,2) NOT NULL COMMENT '商品单价（快照）',
    quantity INT NOT NULL COMMENT '购买数量',
    subtotal DECIMAL(10,2) NOT NULL COMMENT '小计金额',
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    INDEX idx_order_id (order_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单商品明细表';

-- 8. 售后订单表
CREATE TABLE IF NOT EXISTS after_sales (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '售后ID',
    order_id INT NOT NULL COMMENT '订单ID',
    order_no VARCHAR(50) NOT NULL COMMENT '关联订单编号',
    user_id INT NOT NULL COMMENT '用户ID',
    type ENUM('refund','return','exchange') NOT NULL COMMENT '售后类型',
    reason VARCHAR(255) COMMENT '售后原因',
    refund_amount DECIMAL(10,2) COMMENT '退款金额',
    status ENUM('pending','approved','rejected','completed') DEFAULT 'pending' COMMENT '审核状态',
    remark VARCHAR(255) COMMENT '备注',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_order_id (order_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='售后订单表';

-- 9. 购物车表
CREATE TABLE IF NOT EXISTS cart (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '购物车ID',
    user_id INT NOT NULL COMMENT '用户ID',
    goods_id INT NOT NULL COMMENT '商品ID',
    spec_id INT COMMENT '规格ID',
    quantity INT NOT NULL COMMENT '购买数量',
    is_selected BOOLEAN DEFAULT TRUE COMMENT '是否选中',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (goods_id) REFERENCES goods(id),
    UNIQUE KEY uk_user_goods (user_id, goods_id, spec_id),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='购物车表';

-- 10. 支付记录表
CREATE TABLE IF NOT EXISTS payments (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '支付ID',
    payment_no VARCHAR(50) NOT NULL UNIQUE COMMENT '支付单号',
    order_id INT NOT NULL COMMENT '订单ID',
    order_no VARCHAR(50) NOT NULL COMMENT '关联订单编号',
    amount DECIMAL(10,2) NOT NULL COMMENT '支付金额',
    pay_method ENUM('wechat','alipay','bank_card','balance') NOT NULL COMMENT '支付方式',
    pay_status ENUM('pending','success','failed','refunded') DEFAULT 'pending' COMMENT '支付状态',
    transaction_id VARCHAR(100) COMMENT '第三方交易流水号',
    paid_at DATETIME COMMENT '支付时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (order_id) REFERENCES orders(id),
    INDEX idx_order_id (order_id),
    INDEX idx_payment_no (payment_no),
    INDEX idx_status (pay_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='支付记录表';

-- 11. 物流信息表
CREATE TABLE IF NOT EXISTS logistics (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '物流ID',
    order_id INT NOT NULL COMMENT '订单ID',
    order_no VARCHAR(50) NOT NULL COMMENT '关联订单编号',
    logistics_company VARCHAR(50) COMMENT '物流公司',
    logistics_no VARCHAR(50) COMMENT '物流单号',
    shipped_at DATETIME COMMENT '发货时间',
    signed_at DATETIME COMMENT '签收时间',
    tracking_info TEXT COMMENT '物流轨迹（JSON）',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (order_id) REFERENCES orders(id),
    INDEX idx_order_id (order_id),
    INDEX idx_logistics_no (logistics_no)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='物流信息表';

-- 12. 优惠券表
CREATE TABLE IF NOT EXISTS coupons (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '优惠券ID',
    coupon_no VARCHAR(50) NOT NULL UNIQUE COMMENT '券编号',
    coupon_name VARCHAR(100) NOT NULL COMMENT '券名称',
    face_value DECIMAL(10,2) NOT NULL COMMENT '面额',
    min_amount DECIMAL(10,2) DEFAULT 0 COMMENT '使用门槛',
    valid_days INT COMMENT '有效天数',
    total_count INT NOT NULL COMMENT '发放总量',
    received_count INT DEFAULT 0 COMMENT '已领数量',
    used_count INT DEFAULT 0 COMMENT '已用数量',
    status ENUM('active','disabled') DEFAULT 'active' COMMENT '使用状态',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    expired_at DATETIME COMMENT '过期时间',
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='优惠券表';

-- 13. 用户优惠券关联表
CREATE TABLE IF NOT EXISTS user_coupons (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'ID',
    user_id INT NOT NULL COMMENT '用户ID',
    coupon_id INT NOT NULL COMMENT '优惠券ID',
    status ENUM('unused','used','expired') DEFAULT 'unused' COMMENT '使用状态',
    received_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '领取时间',
    used_at DATETIME COMMENT '使用时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (coupon_id) REFERENCES coupons(id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户优惠券关联表';

-- 14. 营销活动表
CREATE TABLE IF NOT EXISTS activities (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '活动ID',
    activity_name VARCHAR(100) NOT NULL COMMENT '活动名称',
    type ENUM('discount','flash_sale','full_reduction') NOT NULL COMMENT '活动类型',
    discount_value DECIMAL(10,2) COMMENT '优惠力度（折扣或满减金额）',
    min_amount DECIMAL(10,2) COMMENT '满减门槛',
    start_time DATETIME NOT NULL COMMENT '活动开始时间',
    end_time DATETIME NOT NULL COMMENT '活动结束时间',
    status ENUM('active','inactive','ended') DEFAULT 'inactive' COMMENT '活动状态',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_status (status),
    INDEX idx_time (start_time, end_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='营销活动表';

-- 15. 活动商品关联表
CREATE TABLE IF NOT EXISTS activity_goods (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'ID',
    activity_id INT NOT NULL COMMENT '活动ID',
    goods_id INT NOT NULL COMMENT '商品ID',
    activity_price DECIMAL(10,2) COMMENT '活动价',
    stock_limit INT COMMENT '库存限制',
    FOREIGN KEY (activity_id) REFERENCES activities(id) ON DELETE CASCADE,
    FOREIGN KEY (goods_id) REFERENCES goods(id),
    UNIQUE KEY uk_activity_goods (activity_id, goods_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='活动商品关联表';

-- ========================================
-- 电商管理平台测试数据
-- ========================================

-- 用户认证数据（密码均为：123456）
-- 密码使用 MD5 加密，加密方式：MD5(salt + password)
INSERT INTO users (username, password, salt, nickname, phone, email, gender, user_level, points, status) VALUES
-- 管理员账户 MD5('abc123' + '123456') = MD5('abc123123456')
('admin', 'a6f70dedd698be90addd35abe38d3876', 'abc123', '管理员', '13800138000', 'admin@ecommerce.com', 'male', 'platinum', 10000, 'active'),
-- 普通用户账户
('user1', '163697b928e71fcdac9576a17093b9db', 'def456', '张三', '13800138001', 'zhangsan@ecommerce.com', 'male', 'gold', 5000, 'active'),
('user2', '66dca3e50d4b0383891fc43001994941', 'ghi789', '李四', '13800138002', 'lisi@ecommerce.com', 'female', 'silver', 2000, 'active'),
('user3', 'e39a0cbe42c2953627e5005617d1c8aa', 'jkl012', '王五', '13800138003', 'wangwu@ecommerce.com', 'male', 'bronze', 500, 'active');

-- 商品分类数据
INSERT INTO goods_categories (parent_id, category_name, sort_order, icon, status) VALUES
(0, '电子产品', 1, 'electronics', 'active'),
(0, '服装鞋帽', 2, 'clothing', 'active'),
(0, '食品饮料', 3, 'food', 'active'),
(1, '手机', 1, 'phone', 'active'),
(1, '电脑', 2, 'computer', 'active'),
(2, '男装', 1, 'men', 'active'),
(2, '女装', 2, 'women', 'active');

-- 商品数据
INSERT INTO goods (goods_no, goods_name, category_id, brand, origin, sale_price, original_price, cost_price, description, main_image, stock, stock_warning, status) VALUES
('G001', 'iPhone 15 Pro', 4, 'Apple', '中国', 7999.00, 8999.00, 6500.00, '苹果最新旗舰手机', 'https://example.com/iphone15.jpg', 100, 10, 'on_sale'),
('G002', 'MacBook Pro', 5, 'Apple', '中国', 12999.00, 14999.00, 10000.00, '苹果专业笔记本电脑', 'https://example.com/macbook.jpg', 50, 5, 'on_sale'),
('G003', '男士T恤', 6, 'Uniqlo', '中国', 99.00, 129.00, 50.00, '纯棉舒适T恤', 'https://example.com/tshirt.jpg', 200, 20, 'on_sale'),
('G004', '女士连衣裙', 7, 'Zara', '西班牙', 299.00, 399.00, 150.00, '时尚连衣裙', 'https://example.com/dress.jpg', 150, 15, 'on_sale'),
('G005', '进口牛奶', 3, '德亚', '德国', 69.00, 79.00, 45.00, '德国进口全脂牛奶', 'https://example.com/milk.jpg', 500, 50, 'on_sale');

-- 优惠券数据
INSERT INTO coupons (coupon_no, coupon_name, face_value, min_amount, valid_days, total_count, status, expired_at) VALUES
('CP001', '新人优惠券', 50.00, 200.00, 30, 1000, 'active', DATE_ADD(NOW(), INTERVAL 30 DAY)),
('CP002', '满减优惠券', 100.00, 500.00, 60, 500, 'active', DATE_ADD(NOW(), INTERVAL 60 DAY)),
('CP003', '限时优惠券', 200.00, 1000.00, 7, 200, 'active', DATE_ADD(NOW(), INTERVAL 7 DAY));

-- 营销活动数据
INSERT INTO activities (activity_name, type, discount_value, min_amount, start_time, end_time, status) VALUES
('618大促', 'full_reduction', 100.00, 500.00, '2024-06-01 00:00:00', '2024-06-18 23:59:59', 'ended'),
('双11狂欢', 'full_reduction', 200.00, 1000.00, '2024-11-01 00:00:00', '2024-11-11 23:59:59', 'inactive'),
('限时秒杀', 'flash_sale', 0.80, 0.00, '2024-06-08 10:00:00', '2024-06-08 12:00:00', 'active');

-- MD5 加密说明：
-- 加密算法：MD5(salt + password)
-- 例如：MD5('abc123' + '123456') = MD5('abc123123456') = 'a6f70dedd698be90addd35abe38d3876'