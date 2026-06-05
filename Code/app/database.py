"""
数据库连接模块
使用 SQLAlchemy ORM 管理数据库连接和会话
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from dotenv import load_dotenv
import os
from pathlib import Path

# 获取当前文件所在目录（app/）
APP_DIR = Path(__file__).resolve().parent

# 加载环境变量（从 app/.env 文件）
load_dotenv(APP_DIR / ".env")

# 创建数据库引擎
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}?charset=utf8mb4"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False  # 设置为 True 可以打印 SQL 语句，方便调试
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    依赖注入：获取数据库会话
    使用方式：db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        if db.is_connected():
            db.close()
