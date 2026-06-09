import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey, Index, VARCHAR, DECIMAL
from sqlalchemy.orm import declarative_base, relationship
from model import Base
from database import engine



# 辅助函数：生成UUID字符串
def gen_uuid():
    return str(uuid.uuid4())


class GoodsCategory(Base):
    """商品分类表"""
    __tablename__ = "goods_category"

    id = Column(VARCHAR(50), primary_key=True, default=gen_uuid)
    category_name = Column(String(50), nullable=False, comment="分类名称")
    parent_id = Column(String(50), default="0", comment="父分类ID，0表示一级分类")
    sort_order = Column(Integer, default=0, comment="排序值，越大越靠前")
    icon = Column(String(200), comment="分类图标URL")
    status = Column(Integer, default=1, comment="状态：1启用，0禁用")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")

    # 索引优化
    __table_args__ = (
        Index('idx_parent_id', 'parent_id'),
        Index('idx_status', 'status'),
    )

    # 关联商品表（一对多）
    goods_list = relationship("Goods", back_populates="category")


class Goods(Base):
    """商品表"""
    __tablename__ = "goods"

    id = Column(VARCHAR(50), primary_key=True, default=gen_uuid)
    goods_no = Column(String(50), nullable=False, unique=True, comment="商品编号")
    goods_name = Column(String(200), nullable=False, comment="商品名称")
    category_id = Column(VARCHAR(50), ForeignKey("goods_category.id"), nullable=False, comment="分类ID")
    price = Column(DECIMAL(10, 2), nullable=False, default=0, comment="售价")
    original_price = Column(Float, default=0, comment="原价")
    cost_price = Column(Float, default=0, comment="成本价")
    intro = Column(String(500), comment="商品简介")
    detail_images = Column(Text, comment="详情图（JSON数组）")
    main_image = Column(String(200), comment="主图URL")
    brand = Column(String(50), comment="品牌")
    origin = Column(String(50), comment="产地")
    sale_status = Column(Integer, default=1, comment="上架状态：1上架，0下架")
    stock_warning = Column(Integer, default=10, comment="预警库存")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 索引优化
    __table_args__ = (
        Index('idx_goods_no', 'goods_no'),
        Index('idx_category_id', 'category_id'),
        Index('idx_sale_status', 'sale_status'),
        Index('idx_price', 'price'),
    )

    # 关联分类表
    category = relationship("GoodsCategory", back_populates="goods_list")
    # 关联规格表
    specs = relationship("GoodsSpec", back_populates="goods", cascade="all, delete-orphan")


class GoodsSpec(Base):
    """商品规格表"""
    __tablename__ = "goods_spec"

    id = Column(VARCHAR(50), primary_key=True, default=gen_uuid)
    goods_id = Column(VARCHAR(50), ForeignKey("goods.id"), nullable=False, comment="商品ID")
    spec_name = Column(String(50), nullable=False, comment="规格名称，如颜色、尺寸")
    spec_value = Column(String(100), nullable=False, comment="规格值，如红色、XL")
    sort_order = Column(Integer, default=0, comment="排序值")

    # 索引优化
    __table_args__ = (
        Index('idx_goods_id', 'goods_id'),
        Index('uix_goods_spec', 'goods_id', 'spec_name', 'spec_value', unique=True),
    )

    # 关联商品表
    goods = relationship("Goods", back_populates="specs")
    # 关联库存表（一对一）
    stock = relationship("GoodsStock", back_populates="spec", uselist=False, cascade="all, delete-orphan")


class GoodsStock(Base):
    """商品库存表（按规格存储）"""
    __tablename__ = "goods_stock"

    id = Column(String(50), primary_key=True, default=gen_uuid)
    spec_id = Column(String(50), ForeignKey("goods_spec.id"), nullable=False, unique=True, comment="规格ID")
    stock_num = Column(Integer, default=0, comment="库存数量")
    warning_stock = Column(Integer, default=10, comment="预警库存")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    __table_args__ = (
        Index('idx_spec_id', 'spec_id'),
    )

    # 关联规格表
    spec = relationship("GoodsSpec", back_populates="stock")


# Base.metadata.create_all(engine)