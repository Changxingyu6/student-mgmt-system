
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ========== 商品分类 ==========

class CategoryBase(BaseModel):
    category_name: str = Field(..., min_length=1, max_length=50, description="分类名称")
    parent_id: str = "0"
    sort_order: int = 0
    icon: Optional[str] = None
    status: int = 1


class CategoryCreate(CategoryBase):
    category_name: str = Field(..., min_length=1, max_length=50, description="分类名称")
    parent_id: str = "0"
    sort_order: int = 0
    icon: Optional[str] = None
    status: int = 1


class CategoryUpdate(BaseModel):
    category_name: Optional[str] = None
    sort_order: Optional[int] = None
    icon: Optional[str] = None
    status: Optional[int] = None


class CategoryResponse(CategoryBase):
    id: str
    create_time: datetime

    class Config:
        from_attributes = True


# ========== 商品规格 ==========
class SpecBase(BaseModel):
    spec_name: str = Field(..., max_length=50)
    spec_value: str = Field(..., max_length=100)
    sort_order: int = 0


class SpecCreate(SpecBase):
    spec_name: str = Field(..., max_length=50)
    spec_value: str = Field(..., max_length=100)
    sort_order: int = 0
    stock_num: int = 0  # 该规格的初始库存
    warning_stock: Optional[int] = 10  # 该规格的预警阈值


class SpecUpdate(BaseModel):
    """更新规格（所有字段可选）"""
    spec_name: Optional[str] = Field(None, max_length=50)
    spec_value: Optional[str] = Field(None, max_length=100)
    sort_order: Optional[int] = None


class SpecResponse(SpecBase):
    id: str
    stock: Optional['StockResponse'] = None  # 关联库存


# ========== 商品库存 ==========
class StockBase(BaseModel):
    spec_id: Optional[str] = None  # 关联规格ID
    stock_num: int = 0
    lock_stock: int = 0


class StockUpdate(BaseModel):
    stock_num: Optional[int] = None
    lock_stock: Optional[int] = None


class StockResponse(StockBase):
    id: str
    spec_id: str
    update_time: datetime


# ========== 商品 ==========
class GoodsBase(BaseModel):
    goods_name: str = Field(..., min_length=1, max_length=200)
    category_id: str
    price: float = Field(..., gt=0)
    original_price: float = 0
    cost_price: float = 0
    intro: Optional[str] = None
    detail_images: Optional[str] = None
    main_image: Optional[str] = None
    brand: Optional[str] = None
    origin: Optional[str] = None
    sale_status: int = 1
    stock_warning: int = 10


class GoodsCreate(GoodsBase):
    goods_no: str = Field(..., max_length=50)
    specs: List[SpecCreate] = []  # 每个规格包含库存信息


class GoodsUpdate(BaseModel):
    goods_name: Optional[str] = None
    category_id: Optional[str] = None
    price: Optional[float] = None
    original_price: Optional[float] = None
    cost_price: Optional[float] = None
    intro: Optional[str] = None
    detail_images: Optional[str] = None
    main_image: Optional[str] = None
    brand: Optional[str] = None
    origin: Optional[str] = None
    sale_status: Optional[int] = None
    stock_warning: Optional[int] = None


class GoodsResponse(GoodsBase):
    id: str
    goods_no: str
    create_time: datetime
    update_time: datetime
    category_name: Optional[str] = None  # 冗余字段方便展示
    specs: List[SpecResponse] = []  # 规格列表（包含库存）

    class Config:
        from_attributes = True


# ========== 查询参数 ==========
class GoodsQueryParams(BaseModel):
    goods_id: Optional[str] = None
    goods_name: Optional[str] = None
    category_id: Optional[str] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    sale_status: Optional[int] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)