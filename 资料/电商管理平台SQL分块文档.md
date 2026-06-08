# 电商管理平台 - SQL 模块分块文档

---

## 一、用户管理模块

### 1.1 用户表 `users`

```sql
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
    lock_count INT DEFAULT 0 COMMENT '连续锁定次数',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';
```

### 1.2 收货地址表 `user_addresses`

```sql
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
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户收货地址表';
```

---

## 二、商品管理模块

### 2.1 商品分类表 `goods_categories`

```sql
CREATE TABLE IF NOT EXISTS goods_categories (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '分类ID',
    parent_id INT DEFAULT 0 COMMENT '父分类ID，0为一级分类',
    category_name VARCHAR(50) NOT NULL COMMENT '分类名称',
    sort_order INT DEFAULT 0 COMMENT '排序',
    icon VARCHAR(255) COMMENT '分类图标',
    status ENUM('active','disabled') DEFAULT 'active' COMMENT '状态',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品分类表';
```

### 2.2 商品表 `goods`

```sql
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
    FOREIGN KEY (category_id) REFERENCES goods_categories(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品表';
```

### 2.3 商品规格表 `goods_specs`

```sql
CREATE TABLE IF NOT EXISTS goods_specs (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '规格ID',
    goods_id INT NOT NULL COMMENT '商品ID',
    spec_name VARCHAR(50) NOT NULL COMMENT '规格名称（如：颜色）',
    spec_value VARCHAR(50) NOT NULL COMMENT '规格值（如：红色）',
    stock INT DEFAULT 0 COMMENT '该规格库存',
    price_diff DECIMAL(10,2) DEFAULT 0 COMMENT '价格差异',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (goods_id) REFERENCES goods(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品规格表';
```

---

## 三、订单管理模块

### 3.1 订单表 `orders`

```sql
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
    FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单表';
```

### 3.2 订单商品明细表 `order_items`

```sql
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
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单商品明细表';
```

### 3.3 售后订单表 `after_sales`

```sql
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
    FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='售后订单表';
```

---

## 四、购物车管理模块

### 4.1 购物车表 `cart`

```sql
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
    UNIQUE KEY uk_user_goods (user_id, goods_id, spec_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='购物车表';
```

---

## 五、支付&物流管理模块

### 5.1 支付记录表 `payments`

```sql
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
    FOREIGN KEY (order_id) REFERENCES orders(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='支付记录表';
```

### 5.2 物流信息表 `logistics`

```sql
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
    FOREIGN KEY (order_id) REFERENCES orders(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='物流信息表';
```

---

## 六、营销活动管理模块

### 6.1 优惠券表 `coupons`

```sql
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
    expired_at DATETIME COMMENT '过期时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='优惠券表';
```

### 6.2 用户优惠券关联表 `user_coupons`

```sql
CREATE TABLE IF NOT EXISTS user_coupons (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'ID',
    user_id INT NOT NULL COMMENT '用户ID',
    coupon_id INT NOT NULL COMMENT '优惠券ID',
    status ENUM('unused','used','expired') DEFAULT 'unused' COMMENT '使用状态',
    received_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '领取时间',
    used_at DATETIME COMMENT '使用时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (coupon_id) REFERENCES coupons(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户优惠券关联表';
```

### 6.3 营销活动表 `activities`

```sql
CREATE TABLE IF NOT EXISTS activities (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '活动ID',
    activity_name VARCHAR(100) NOT NULL COMMENT '活动名称',
    type ENUM('discount','flash_sale','full_reduction') NOT NULL COMMENT '活动类型',
    discount_value DECIMAL(10,2) COMMENT '优惠力度（折扣或满减金额）',
    min_amount DECIMAL(10,2) COMMENT '满减门槛',
    start_time DATETIME NOT NULL COMMENT '活动开始时间',
    end_time DATETIME NOT NULL COMMENT '活动结束时间',
    status ENUM('active','inactive','ended') DEFAULT 'inactive' COMMENT '活动状态',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='营销活动表';
```

### 6.4 活动商品关联表 `activity_goods`

```sql
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

---

## 七、店铺管理模块

### 7.1 店铺表 `shops`

```sql
CREATE TABLE IF NOT EXISTS shops (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '店铺ID',
    shop_name VARCHAR(100) NOT NULL COMMENT '店铺名称',
    shop_no VARCHAR(50) NOT NULL UNIQUE COMMENT '店铺编号',
    owner_id INT NOT NULL COMMENT '店主用户ID',
    logo VARCHAR(255) COMMENT '店铺Logo',
    banner VARCHAR(255) COMMENT '店铺横幅',
    description TEXT COMMENT '店铺简介',
    status ENUM('active','closed','suspended') DEFAULT 'active' COMMENT '店铺状态',
    rating DECIMAL(2,1) DEFAULT 5.0 COMMENT '店铺评分',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (owner_id) REFERENCES users(id),
    INDEX idx_owner_id (owner_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='店铺表';
```

### 7.2 店铺商品关联表 `shop_goods`

```sql
CREATE TABLE IF NOT EXISTS shop_goods (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'ID',
    shop_id INT NOT NULL COMMENT '店铺ID',
    goods_id INT NOT NULL COMMENT '商品ID',
    sort_order INT DEFAULT 0 COMMENT '排序',
    is_featured BOOLEAN DEFAULT FALSE COMMENT '是否推荐',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (shop_id) REFERENCES shops(id) ON DELETE CASCADE,
    FOREIGN KEY (goods_id) REFERENCES goods(id),
    UNIQUE KEY uk_shop_goods (shop_id, goods_id),
    INDEX idx_shop_id (shop_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='店铺商品关联表';
```

---

## 八、供应商管理模块

### 8.1 供应商表 `suppliers`

```sql
CREATE TABLE IF NOT EXISTS suppliers (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '供应商ID',
    supplier_name VARCHAR(100) NOT NULL COMMENT '供应商名称',
    supplier_no VARCHAR(50) NOT NULL UNIQUE COMMENT '供应商编号',
    contact_name VARCHAR(50) COMMENT '联系人',
    contact_phone VARCHAR(20) COMMENT '联系电话',
    contact_email VARCHAR(100) COMMENT '联系邮箱',
    address VARCHAR(255) COMMENT '地址',
    bank_account VARCHAR(50) COMMENT '银行账户',
    tax_no VARCHAR(50) COMMENT '税号',
    status ENUM('active','inactive') DEFAULT 'active' COMMENT '状态',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_supplier_no (supplier_no),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='供应商表';
```

### 8.2 供应商商品关联表 `supplier_goods`

```sql
CREATE TABLE IF NOT EXISTS supplier_goods (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'ID',
    supplier_id INT NOT NULL COMMENT '供应商ID',
    goods_id INT NOT NULL COMMENT '商品ID',
    supply_price DECIMAL(10,2) NOT NULL COMMENT '供货价格',
    min_order INT DEFAULT 1 COMMENT '起订量',
    delivery_days INT DEFAULT 3 COMMENT '交货天数',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE CASCADE,
    FOREIGN KEY (goods_id) REFERENCES goods(id),
    UNIQUE KEY uk_supplier_goods (supplier_id, goods_id),
    INDEX idx_supplier_id (supplier_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='供应商商品关联表';
```

---

## 九、角色权限管理模块

### 9.1 角色表 `roles`

```sql
CREATE TABLE IF NOT EXISTS roles (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '角色ID',
    role_name VARCHAR(50) NOT NULL UNIQUE COMMENT '角色名称',
    description VARCHAR(255) COMMENT '角色描述',
    status ENUM('active','disabled') DEFAULT 'active' COMMENT '状态',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_role_name (role_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色表';
```

### 9.2 权限表 `permissions`

```sql
CREATE TABLE IF NOT EXISTS permissions (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '权限ID',
    permission_code VARCHAR(50) NOT NULL UNIQUE COMMENT '权限代码',
    permission_name VARCHAR(100) NOT NULL COMMENT '权限名称',
    module VARCHAR(50) COMMENT '所属模块',
    action VARCHAR(50) COMMENT '操作类型',
    description VARCHAR(255) COMMENT '权限描述',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_permission_code (permission_code),
    INDEX idx_module (module)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='权限表';
```

### 9.3 角色权限关联表 `role_permissions`

```sql
CREATE TABLE IF NOT EXISTS role_permissions (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'ID',
    role_id INT NOT NULL COMMENT '角色ID',
    permission_id INT NOT NULL COMMENT '权限ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id),
    UNIQUE KEY uk_role_permission (role_id, permission_id),
    INDEX idx_role_id (role_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色权限关联表';
```

### 9.4 用户角色关联表 `user_roles`

```sql
CREATE TABLE IF NOT EXISTS user_roles (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'ID',
    user_id INT NOT NULL COMMENT '用户ID',
    role_id INT NOT NULL COMMENT '角色ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id),
    UNIQUE KEY uk_user_role (user_id, role_id),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户角色关联表';
```

---

## 十、日志管理模块

### 10.1 登录日志表 `login_logs`

```sql
CREATE TABLE IF NOT EXISTS login_logs (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'ID',
    user_id INT COMMENT '用户ID（登录成功时记录）',
    username VARCHAR(50) COMMENT '登录用户名',
    ip_address VARCHAR(50) COMMENT '登录IP',
    user_agent VARCHAR(255) COMMENT '浏览器信息',
    login_type ENUM('password','sms','wechat','alipay') DEFAULT 'password' COMMENT '登录方式',
    status ENUM('success','failed') COMMENT '登录状态',
    error_message VARCHAR(255) COMMENT '错误信息',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '登录时间',
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='登录日志表';
```

### 10.2 操作日志表 `operation_logs`

```sql
CREATE TABLE IF NOT EXISTS operation_logs (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'ID',
    user_id INT NOT NULL COMMENT '操作用户ID',
    username VARCHAR(50) COMMENT '操作用户名',
    module VARCHAR(50) COMMENT '操作模块',
    action VARCHAR(50) COMMENT '操作类型',
    target_id INT COMMENT '操作对象ID',
    target_name VARCHAR(255) COMMENT '操作对象名称',
    before_data TEXT COMMENT '操作前数据（JSON）',
    after_data TEXT COMMENT '操作后数据（JSON）',
    ip_address VARCHAR(50) COMMENT '操作IP',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
    INDEX idx_user_id (user_id),
    INDEX idx_module (module),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='操作日志表';
```

---

## 十一、索引汇总

### 11.1 用户管理模块索引

| 表名 | 索引名称 | 索引字段 | 类型 |
|------|---------|---------|------|
| users | PRIMARY | id | 主键 |
| users | idx_username | username | 普通索引 |
| users | idx_phone | phone | 普通索引 |
| users | idx_status | status | 普通索引 |
| users | idx_level | user_level | 普通索引 |
| user_addresses | PRIMARY | id | 主键 |
| user_addresses | idx_user_id | user_id | 普通索引 |
| user_addresses | uk_user_default | user_id, is_default | 唯一索引 |

### 11.2 商品管理模块索引

| 表名 | 索引名称 | 索引字段 | 类型 |
|------|---------|---------|------|
| goods_categories | PRIMARY | id | 主键 |
| goods_categories | idx_parent_id | parent_id | 普通索引 |
| goods_categories | idx_status | status | 普通索引 |
| goods | PRIMARY | id | 主键 |
| goods | uk_goods_no | goods_no | 唯一索引 |
| goods | idx_category | category_id | 普通索引 |
| goods | idx_status | status | 普通索引 |
| goods | idx_stock | stock | 普通索引 |
| goods_specs | PRIMARY | id | 主键 |
| goods_specs | idx_goods_id | goods_id | 普通索引 |
| goods_specs | uk_goods_spec | goods_id, spec_name, spec_value | 唯一索引 |

### 11.3 订单管理模块索引

| 表名 | 索引名称 | 索引字段 | 类型 |
|------|---------|---------|------|
| orders | PRIMARY | id | 主键 |
| orders | uk_order_no | order_no | 唯一索引 |
| orders | idx_user_id | user_id | 普通索引 |
| orders | idx_status | order_status | 普通索引 |
| orders | idx_pay_status | pay_status | 普通索引 |
| orders | idx_created_at | created_at | 普通索引 |
| order_items | PRIMARY | id | 主键 |
| order_items | idx_order_id | order_id | 普通索引 |
| after_sales | PRIMARY | id | 主键 |
| after_sales | idx_order_id | order_id | 普通索引 |
| after_sales | idx_status | status | 普通索引 |

### 11.4 购物车模块索引

| 表名 | 索引名称 | 索引字段 | 类型 |
|------|---------|---------|------|
| cart | PRIMARY | id | 主键 |
| cart | uk_user_goods | user_id, goods_id, spec_id | 唯一索引 |
| cart | idx_user_id | user_id | 普通索引 |

### 11.5 支付&物流模块索引

| 表名 | 索引名称 | 索引字段 | 类型 |
|------|---------|---------|------|
| payments | PRIMARY | id | 主键 |
| payments | uk_payment_no | payment_no | 唯一索引 |
| payments | idx_order_id | order_id | 普通索引 |
| payments | idx_status | pay_status | 普通索引 |
| logistics | PRIMARY | id | 主键 |
| logistics | idx_order_id | order_id | 普通索引 |
| logistics | idx_logistics_no | logistics_no | 普通索引 |

### 11.6 营销活动模块索引

| 表名 | 索引名称 | 索引字段 | 类型 |
|------|---------|---------|------|
| coupons | PRIMARY | id | 主键 |
| coupons | uk_coupon_no | coupon_no | 唯一索引 |
| coupons | idx_status | status | 普通索引 |
| user_coupons | PRIMARY | id | 主键 |
| user_coupons | idx_user_id | user_id | 普通索引 |
| user_coupons | idx_status | status | 普通索引 |
| activities | PRIMARY | id | 主键 |
| activities | idx_status | status | 普通索引 |
| activities | idx_time | start_time, end_time | 普通索引 |
| activity_goods | PRIMARY | id | 主键 |
| activity_goods | uk_activity_goods | activity_id, goods_id | 唯一索引 |

### 11.7 店铺管理模块索引

| 表名 | 索引名称 | 索引字段 | 类型 |
|------|---------|---------|------|
| shops | PRIMARY | id | 主键 |
| shops | uk_shop_no | shop_no | 唯一索引 |
| shops | idx_owner_id | owner_id | 普通索引 |
| shops | idx_status | status | 普通索引 |
| shop_goods | PRIMARY | id | 主键 |
| shop_goods | uk_shop_goods | shop_id, goods_id | 唯一索引 |
| shop_goods | idx_shop_id | shop_id | 普通索引 |

### 11.8 供应商管理模块索引

| 表名 | 索引名称 | 索引字段 | 类型 |
|------|---------|---------|------|
| suppliers | PRIMARY | id | 主键 |
| suppliers | uk_supplier_no | supplier_no | 唯一索引 |
| suppliers | idx_status | status | 普通索引 |
| supplier_goods | PRIMARY | id | 主键 |
| supplier_goods | uk_supplier_goods | supplier_id, goods_id | 唯一索引 |
| supplier_goods | idx_supplier_id | supplier_id | 普通索引 |

### 11.9 角色权限模块索引

| 表名 | 索引名称 | 索引字段 | 类型 |
|------|---------|---------|------|
| roles | PRIMARY | id | 主键 |
| roles | uk_role_name | role_name | 唯一索引 |
| permissions | PRIMARY | id | 主键 |
| permissions | uk_permission_code | permission_code | 唯一索引 |
| permissions | idx_module | module | 普通索引 |
| role_permissions | PRIMARY | id | 主键 |
| role_permissions | uk_role_permission | role_id, permission_id | 唯一索引 |
| user_roles | PRIMARY | id | 主键 |
| user_roles | uk_user_role | user_id, role_id | 唯一索引 |

### 11.10 日志管理模块索引

| 表名 | 索引名称 | 索引字段 | 类型 |
|------|---------|---------|------|
| login_logs | PRIMARY | id | 主键 |
| login_logs | idx_user_id | user_id | 普通索引 |
| login_logs | idx_created_at | created_at | 普通索引 |
| operation_logs | PRIMARY | id | 主键 |
| operation_logs | idx_user_id | user_id | 普通索引 |
| operation_logs | idx_module | module | 普通索引 |
| operation_logs | idx_created_at | created_at | 普通索引 |

---

## 十二、外键关系图

```
users ──────────┬──→ user_addresses (user_id)
                ├──→ cart (user_id)
                ├──→ orders (user_id)
                ├──→ after_sales (user_id)
                ├──→ user_coupons (user_id)
                ├──→ user_roles (user_id)
                └──→ shops (owner_id)

goods_categories ──→ goods (category_id)

goods ─────────┬──→ goods_specs (goods_id)
               ├──→ cart (goods_id)
               ├──→ order_items (goods_id)
               ├──→ activity_goods (goods_id)
               ├──→ shop_goods (goods_id)
               └──→ supplier_goods (goods_id)

orders ────────┬──→ order_items (order_id)
               ├──→ after_sales (order_id)
               ├──→ payments (order_id)
               └──→ logistics (order_id)

coupons ───────→ user_coupons (coupon_id)

activities ────→ activity_goods (activity_id)

shops ─────────→ shop_goods (shop_id)

suppliers ─────→ supplier_goods (supplier_id)

roles ─────────┬──→ role_permissions (role_id)
               └──→ user_roles (role_id)

permissions ───→ role_permissions (permission_id)
```

---

## 十三、数据库初始化命令

```bash
# 创建数据库
mysql -u root -p -e "CREATE DATABASE ecommerce_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 导入数据表
mysql -u root -p ecommerce_db < ecommerce_init_database.sql

# 查看所有表
mysql -u root -p ecommerce_db -e "SHOW TABLES;"
```