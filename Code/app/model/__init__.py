# 数据库模型模块
# 使用 SQLAlchemy ORM 定义数据库表映射

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
    