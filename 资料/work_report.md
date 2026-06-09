
# 后端开发工作汇报

---

## 一、用户管理模块

### 1.1 功能概述
- 用户注册与登录
- 用户信息管理
- 密码安全策略（MD5加盐加密）
- 阶梯式登录锁定机制

### 1.2 核心代码 - 用户模型

```python
# app/model/user.py
class User(Base):
    __tablename__ = "users"

    id = Column(String(50), primary_key=True, index=True, comment="用户ID（UUID）")
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    password = Column(String(32), nullable=False, comment="密码（MD5加密，32位）")
    salt = Column(String(32), nullable=False, comment="加密盐值")
    pay_password = Column(String(32), comment="支付密码（MD5加密）")
    nickname = Column(String(50), comment="昵称")
    phone = Column(String(20), comment="手机号")
    email = Column(String(100), comment="邮箱")
    gender = Column(Enum('male', 'female', 'other'), comment="性别")
    avatar = Column(String(255), comment="头像URL")
    user_level = Column(Enum('青铜会员', '白银会员', '黄金会员'), default='青铜会员', comment="用户等级")
    points = Column(Integer, default=0, comment="会员积分")
    balance = Column(DECIMAL(10, 2), default=0.00, comment="用户余额")
    discount_rate = Column(DECIMAL(5, 2), default=1.00, comment="优惠折扣率")
    status = Column(Enum('active', 'inactive', 'banned'), default='active', comment="账号状态")
    failed_attempts = Column(Integer, default=0, comment="连续登录失败次数")
    lock_until = Column(DateTime, comment="账户锁定截止时间")
    lock_count = Column(Integer, default=0, comment="连续锁定次数")
    role_id = Column(String(50), ForeignKey("roles.id"), default='r-002', comment="角色ID")
```

### 1.3 核心代码 - 登录锁定逻辑

```python
# app/services/user_service.py
# 登录失败限制配置（从环境变量读取）
MAX_FAILED_ATTEMPTS = int(os.getenv("MAX_FAILED_ATTEMPTS", "5"))
# 阶梯式锁定时间配置（分钟），逗号分隔：第1次锁定时长,第2次锁定时长,...
LOCK_DURATIONS = [int(x) for x in os.getenv("LOCK_DURATIONS", "5,15,30,60,120").split(",")]

def get_lock_duration_by_count(lock_count: int) -> int:
    """根据锁定次数获取对应的锁定时长（分钟）"""
    index = min(lock_count - 1, len(LOCK_DURATIONS) - 1)
    return LOCK_DURATIONS[index]

def login_for_access_token(username: str, password: str, db: Session, ip_address: str = "") -> dict:
    """用户登录获取token"""
    if check_user_locked(db, username):
        remaining_seconds = get_lock_remaining_time(db, username)
        remaining_minutes = (remaining_seconds // 60) + 1
        raise HTTPException(status_code=401, detail=f"账户已被锁定，请{remaining_minutes}分钟后再试")
    
    user = authenticate_user(username, password, db)
    
    if not user:
        user_repo.increment_failed_attempts(db, username)
        db_user = user_repo.get_user_with_lock_status(db, username)
        failed_count = db_user.failed_attempts if db_user else 0
        
        if failed_count >= MAX_FAILED_ATTEMPTS:
            current_lock_count = (db_user.lock_count or 0) + 1
            lock_duration = get_lock_duration_by_count(current_lock_count)
            user_repo.lock_user(db, username, lock_duration)
```

---

## 二、角色权限模块

### 2.1 功能概述
- 角色CRUD管理
- 用户角色分配
- 基于角色的访问控制（RBAC）

### 2.2 核心代码 - 角色模型

```python
# app/model/role.py
class Role(Base):
    __tablename__ = "roles"

    id = Column(String(50), primary_key=True, index=True, comment="角色ID（UUID）")
    role_name = Column(String(50), unique=True, nullable=False, index=True, comment="角色名称")
    description = Column(String(255), comment="角色描述")
    status = Column(Enum('active', 'inactive'), default='active', comment="状态")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
```

### 2.3 核心代码 - 权限装饰器

```python
# app/utils/decorators.py
def require_roles(allowed_roles: list = None):
    """
    角色权限装饰器（从中间件获取用户信息）
    
    使用规则：
    - 不写装饰器：所有已认证用户都能访问
    - @require_roles()：只有 admin 能访问
    - @require_roles(["manager"])：admin + manager
    - @require_roles(["user"])：admin + user
    """
    if allowed_roles is None:
        allowed_roles = []

    def decorator(func):
        @wraps(func)
        def wrapper(*args, request: Request = None, **kwargs):
            current_user = getattr(request.state, 'user', None)
            
            if not current_user:
                raise HTTPException(status_code=401, detail="未认证，请先登录")
            
            user_role = current_user.get("role", "")
            
            # admin 默认拥有所有权限
            if user_role == "admin":
                return func(*args, request=request, **kwargs)
            
            # 如果装饰器不传参数，只有 admin 能访问
            if not allowed_roles:
                raise HTTPException(status_code=403, detail="权限不足，需要管理员权限")
            
            if user_role not in allowed_roles:
                raise HTTPException(status_code=403, detail=f"权限不足，需要角色: {', '.join(allowed_roles)}")
            
            return func(*args, request=request, **kwargs)
        return wrapper
    return decorator
```

---

## 三、JWT认证系统

### 3.1 功能概述
- Token生成与验证
- 认证中间件
- 无状态身份验证

### 3.2 核心代码 - JWT工具函数

```python
# app/utils/jwt_utils.py
def create_access_token(data: dict) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "iat": datetime.utcnow(),  # 签发时间（UTC）
        "exp": expire
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """解析 Token，返回 payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="认证令牌已过期")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="认证令牌无效")
```

### 3.3 核心代码 - 认证中间件

```python
# app/main.py
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """JWT 认证中间件"""
    # 白名单路径
    WHITELIST = ["/users/login", "/users/register", "/docs", "/redoc"]
    
    if any(request.url.path.startswith(path) for path in WHITELIST):
        return await call_next(request)
    
    # 获取 Token
    token = None
    if "Authorization" in request.headers:
        auth_header = request.headers["Authorization"]
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
    
    if not token:
        return JSONResponse(status_code=401, content={"code": 401, "message": "未授权，请先登录"})
    
    # 验证 Token
    try:
        payload = decode_access_token(token)
        request.state.user = {
            "id": payload.get("user_id"),
            "username": payload.get("username"),
            "role": payload.get("role", "user")
        }
    except Exception as e:
        logger.error(f"Token 验证失败: {str(e)}")
        return JSONResponse(status_code=401, content={"code": 401, "message": "Token 验证失败"})
    
    return await call_next(request)
```

---

## 四、日志系统

### 4.1 功能概述
- 应用日志记录（按日期生成文件）
- 登录日志管理
- 操作日志审计

### 4.2 核心代码 - 日志配置

```python
# app/utils/logger.py
class LoggerConfig:
    """日志配置类"""
    
    @staticmethod
    def get_today_log_filename(prefix: str) -> str:
        """获取当日日志文件名，格式：YYYYMMDD_prefix.log"""
        today = datetime.now().strftime("%Y%m%d")
        return f"{today}_{prefix}.log"
    
    @staticmethod
    def configure_logging():
        """配置日志系统"""
        logger = logging.getLogger("app")
        logger.setLevel(logging.DEBUG)
        
        # 应用日志文件处理器
        app_log_path = LOG_DIR / LoggerConfig.get_today_log_filename("app")
        app_file_handler = logging.FileHandler(str(app_log_path), encoding="utf-8")
        app_file_handler.setLevel(logging.DEBUG)
        
        # 错误日志文件处理器
        error_log_path = LOG_DIR / LoggerConfig.get_today_log_filename("error")
        error_file_handler = logging.FileHandler(str(error_log_path), encoding="utf-8")
        error_file_handler.setLevel(logging.ERROR)
        
        logger.addHandler(app_file_handler)
        logger.addHandler(error_file_handler)
        return logger
```

### 4.3 核心代码 - 登录日志服务

```python
# app/services/log_service.py
class LoginLogService:
    """登录日志服务"""

    @staticmethod
    def log_login(db: Session, username: str, ip_address: str, user_agent: str = "",
                 login_type: str = "password", status: str = "success",
                 user_id: int = None, error_message: str = ""):
        """记录登录日志"""
        try:
            create_login_log(
                db,
                user_id=user_id,
                username=username,
                ip_address=ip_address,
                user_agent=user_agent,
                login_type=login_type,
                status=status,
                error_message=error_message
            )
            logger.info(f"登录日志记录成功 - 用户: {username} - 状态: {status}")
        except Exception as e:
            logger.error(f"记录登录日志失败: {str(e)}")
```

---

## 五、AI服务模块

### 5.1 功能概述
- 集成火山引擎方舟 DeepSeek 模型 API
- 支持流式/非流式响应

### 5.2 核心代码 - AI服务

```python
# app/services/ai_service.py
def chat_with_ai_stream(messages: list):
    """与AI对话（流式响应生成器）"""
    base_url = os.environ.get("ARK_BASE_URL")
    api_key = os.environ.get("ARK_API_KEY")
    model = os.environ.get("ARK_MODEL")
    
    # 转换消息格式
    input_content = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        
        if role == "user":
            input_content.append({
                "role": "user",
                "content": [{"type": "input_text", "text": content}]
            })
        elif role == "assistant":
            input_content.append({
                "role": "assistant",
                "content": [{"type": "output_text", "text": content}]
            })
    
    url = f"{base_url}/responses"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    payload = {"model": model, "stream": True, "input": input_content}
    
    response = requests.post(url, headers=headers, json=payload, stream=True)
    response.raise_for_status()
    
    for line in response.iter_lines():
        if line and line_str.startswith('data: '):
            data_str = line_str[6:]
            data = json.loads(data_str)
            # 处理流式响应...
```

---

## 六、技术架构

### 6.1 三层架构设计

```
┌─────────────────────────────────────────┐
│              API 层                     │
│ user_api.py | role_api.py | ai_api.py   │
├─────────────────────────────────────────┤
│            Service 层                   │
│ user_service.py | role_service.py       │
├─────────────────────────────────────────┤
│              DAO 层                     │
│   user_dao.py | role_dao.py | log.py    │
├─────────────────────────────────────────┤
│            Model 层                     │
│    user.py | role.py | log.py           │
├─────────────────────────────────────────┤
│              数据库                      │
│           MySQL + SQLAlchemy            │
└─────────────────────────────────────────┘
```

### 6.2 安全体系

| 安全机制 | 实现方式 |
|---------|---------|
| 密码加密 | MD5加盐 |
| 登录锁定 | 阶梯式锁定（5/15/30/60/120分钟） |
| 身份认证 | JWT Token（30分钟过期） |
| 权限控制 | 角色装饰器 @require_roles |

---

## 七、个人贡献总结

1. **用户管理模块**：完整实现用户注册、登录、信息管理、阶梯式登录锁定
2. **角色权限模块**：设计并实现RBAC角色权限系统，包括角色CRUD和权限装饰器
3. **JWT认证系统**：构建无状态认证中间件，支持白名单配置
4. **日志系统**：建立系统化日志记录机制，按日期生成日志文件
5. **AI服务模块**：集成火山引擎方舟模型API，支持流式响应
6. **架构设计**：设计三层架构（API→Service→DAO）和代码规范
