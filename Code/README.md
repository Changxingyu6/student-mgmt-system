# 电商管理平台

基于 FastAPI 的电商管理平台，采用三层架构（Controller-Service-DAO），使用 SQLAlchemy ORM 进行数据库操作。

## 📋 功能模块

- **用户管理** - 用户信息增删改查、等级管理、积分管理
- **商品管理** - 商品信息管理、分类管理、规格管理、库存管理
- **订单管理** - 订单创建、状态流转、售后管理
- **购物车管理** - 购物车增删改查
- **支付管理** - 支付记录、支付状态管理
- **物流管理** - 物流信息录入、轨迹追踪
- **营销活动** - 优惠券管理、满减活动、限时秒杀
- **数据统计** - 用户统计、商品统计、订单统计、营销统计
- **用户认证** - JWT Token 认证

## 🛠️ 技术栈

- **框架**: FastAPI 0.104.1
- **数据库**: MySQL 8.0+
- **ORM**: SQLAlchemy 2.0
- **数据验证**: Pydantic 2.0
- **认证**: PyJWT
- **服务器**: Uvicorn
- **架构模式**: 三层架构（Controller-Service-DAO）

## 🚀 快速开始

### 环境要求

- Python 3.10+
- MySQL 8.0+

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置数据库

1. 创建数据库：
```sql
CREATE DATABASE ecommerce_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. 导入数据表：
```bash
mysql -u root -p ecommerce_db < ../资料/ecommerce_init_database.sql
```

3. 修改 `.env` 文件：
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=ecommerce_db
SECRET_KEY=your_secret_key
```

### 运行项目

```bash
cd Code
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 访问接口文档

启动后访问 `http://localhost:8000/docs` 查看 Swagger 文档。

## 📁 项目结构

```
ecommerce-platform/
├── Code/
│   ├── app/
│   │   ├── main.py           # 主入口
│   │   ├── config.py         # 配置文件
│   │   ├── database.py       # 数据库连接
│   │   ├── deps.py           # 依赖注入定义（公共依赖）
│   │   │
│   │   ├── api/              # API 路由层（Controller）
│   │   │   ├── users.py      # 用户路由
│   │   │   ├── goods.py      # 商品路由
│   │   │   ├── orders.py     # 订单路由
│   │   │   └── __init__.py
│   │   │
│   │   ├── services/         # 业务逻辑层（Service）
│   │   │   ├── user.py
│   │   │   ├── goods.py
│   │   │   ├── order.py
│   │   │   └── activity.py
│   │   │
│   │   ├── dao/              # 数据访问层（DAO）
│   │   │   ├── user.py
│   │   │   ├── goods.py
│   │   │   └── order.py
│   │   │
│   │   ├── model/            # SQLAlchemy 模型
│   │   │   ├── __init__.py   # BaseModel 基类（含 create_dt, update_dt）
│   │   │   ├── user.py
│   │   │   ├── goods.py
│   │   │   └── order.py
│   │   │
│   │   ├── scheme/           # Pydantic 数据验证
│   │   │   ├── user.py
│   │   │   ├── goods.py
│   │   │   └── order.py
│   │   │
│   │   └── utils/            # 工具函数
│   │       └── __init__.py
│   ├── requirements.txt      # 依赖列表
│   └── README.md            # 项目说明
├── frontend/                 # Vue3 前端项目
├── 资料/                    # 文档资料
│   ├── pdf_content.txt
│   ├── ecommerce_init_database.sql
│   ├── 开发规范.md
│   ├── 分工清单.md
│   ├── GitHub入门指南.md
│   ├── ER图说明.md
│   └── 电商管理平台业务逻辑.md
└── .gitignore
```

## 🏗️ 架构说明

### 三层架构职责

1. **API 路由层（api/）**
   - 接收 HTTP 请求
   - 参数验证（通过 Pydantic）
   - 调用 Service 层
   - 返回响应

2. **业务逻辑层（services/）**
   - 业务规则验证
   - 事务处理
   - 错误处理
   - 依赖注入数据库
   - 调用 DAO 层

3. **数据访问层（dao/）**
   - 数据库 CRUD 操作
   - 使用 SQLAlchemy ORM
   - 无业务逻辑

### 依赖注入

使用 FastAPI 的 `Depends` 实现依赖注入：

```python
# Service 层注入数据库
def get_all_users(
    page: int = 1,
    db: Session = Depends(get_database)
):
    users = user_dao.get_users(db, page)
    return users
```

### 用户认证

使用 JWT Token 认证：

```python
# 需要认证的路由
router = APIRouter(dependencies=[Depends(get_current_user)])

# 请求头格式
# Authorization: Bearer <token>
```

## 👥 团队分工

| 成员 | 负责模块 | 需要创建的文件 |
|------|---------|---------------|
| **组长** | 项目框架 + 文档 | ✅ 已完成 |
| A | 用户管理 | `dao/user.py`<br>`services/user.py`<br>`api/users.py` |
| B | 商品管理 | `dao/goods.py`<br>`services/goods.py`<br>`api/goods.py` |
| C | 订单管理 | `dao/order.py`<br>`services/order.py`<br>`api/orders.py` |
| D | 营销活动 | `dao/activity.py`<br>`services/activity.py`<br>`api/activities.py` |
| E | 数据统计 + 支付物流 | `api/statistics.py`<br>`api/payments.py`<br>`api/logistics.py` |

## 📝 API 接口

### 用户认证接口

| 方法 | 路径 | 描述 | 是否需要认证 |
|------|------|------|-------------|
| POST | /users/login | 用户登录 | ❌ |
| POST | /users/register | 用户注册 | ❌ |
| GET | /users/me | 获取当前用户 | ✅ |
| PUT | /users/me | 更新个人信息 | ✅ |

### 用户管理

| 方法 | 路径 | 描述 | 是否需要认证 |
|------|------|------|-------------|
| GET | /users | 获取用户列表 | ✅（管理员） |
| GET | /users/locked | 获取锁定用户 | ✅（管理员） |
| POST | /users/{user_id}/unlock | 解锁用户 | ✅（管理员） |

### 商品管理

| 方法 | 路径 | 描述 | 是否需要认证 |
|------|------|------|-------------|
| GET | /goods | 获取商品列表 | ✅ |
| POST | /goods | 创建商品 | ✅ |
| GET | /goods/{id} | 获取单个商品 | ✅ |
| PUT | /goods/{id} | 更新商品信息 | ✅ |
| DELETE | /goods/{id} | 删除商品 | ✅ |

### 订单管理

| 方法 | 路径 | 描述 | 是否需要认证 |
|------|------|------|-------------|
| GET | /orders | 获取订单列表 | ✅ |
| POST | /orders | 创建订单 | ✅ |
| GET | /orders/{id} | 获取订单详情 | ✅ |
| PUT | /orders/{id} | 更新订单状态 | ✅ |

## 📄 开发指南

### 开发新模块的步骤

1. **创建 Model**（数据库模型）
   - 在 `model/` 创建文件
   - 继承 `BaseModel`（自动获得 create_dt, update_dt）
   - 定义字段映射

2. **创建 Scheme**（数据验证）
   - 在 `scheme/` 创建文件
   - 定义 Pydantic 模型
   - 用于请求/响应验证

3. **创建 DAO**（数据访问层）
   - 在 `dao/` 创建文件
   - 实现 CRUD 函数
   - 使用 SQLAlchemy ORM

4. **创建 Service**（业务逻辑层）
   - 在 `services/` 创建文件
   - 依赖注入数据库（Depends(get_database)）
   - 调用 DAO 层
   - 添加业务验证

5. **创建 API 路由**（控制层）
   - 在 `api/` 创建文件
   - 定义路由和参数
   - 调用 Service 层（Depends(service_function)）

### 示例代码

参考现有实现：`model/user.py`、`scheme/user.py`、`dao/user.py`、`services/user.py`、`api/users.py`

## 📄 相关文档

- 需求文档：`资料/pdf_content.txt`
- 数据库设计：`资料/ecommerce_init_database.sql`
- 业务逻辑：`资料/电商管理平台业务逻辑.md`
- 开发规范：`资料/开发规范.md`
- 分工清单：`资料/分工清单.md`
- ER 图说明：`资料/ER图说明.md`
- GitHub 指南：`资料/GitHub入门指南.md`

## 📌 代码规范

- 遵循 PEP 8 规范
- 使用 4 个空格缩进
- 函数和变量使用下划线命名
- 类名使用大驼峰命名
- 使用 SQLAlchemy ORM，禁止拼接 SQL
- 所有数据库操作必须通过依赖注入获取连接
- Model 继承 `BaseModel` 自动获得 `create_dt` 和 `update_dt` 字段

## 🔐 测试账户

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | 123456 | 管理员 |
| user1 | 123456 | 普通用户 |
| user2 | 123456 | 普通用户 |

## 📜 许可证

MIT License