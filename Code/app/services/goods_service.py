
import uuid
from sqlalchemy.orm import Session
from dao import goods_dao as dao
from model.goods_model import Goods, GoodsSpec, GoodsStock
from schema.goods_schema import GoodsCreate, GoodsUpdate, StockBase
from model.goods_model import GoodsCategory

# ========== 商品分类 Service ==========
def create_category(db: Session, category_data: dict):
    category = GoodsCategory(**category_data)
    return dao.create_category(db, category)


def update_category(db: Session, category_id: str, update_data: dict):
    category = dao.get_category_by_id(db, category_id)
    if not category:
        return None
    return dao.update_category(db, category, update_data)


def delete_category(db: Session, category_id: str):
    category = dao.get_category_by_id(db, category_id)
    if not category:
        return False
    if dao.has_goods_in_category(db, category_id):
        raise ValueError("该分类下存在商品，无法删除")
    dao.delete_category(db, category)
    return True


# ========== 商品 Service ==========
def create_goods(db: Session, goods_data: GoodsCreate):
    # 1. 检查商品编号是否已存在
    exist = dao.get_goods_by_no(db, goods_data.goods_no)
    if exist:
        raise ValueError(f"商品编号 {goods_data.goods_no} 已存在")

    # 2. 创建商品主体
    goods = Goods(
        id=str(uuid.uuid4()),
        goods_no=goods_data.goods_no,
        goods_name=goods_data.goods_name,
        category_id=goods_data.category_id,
        price=goods_data.price,
        original_price=goods_data.original_price,
        cost_price=goods_data.cost_price,
        intro=goods_data.intro,
        detail_images=goods_data.detail_images,
        main_image=goods_data.main_image,
        brand=goods_data.brand,
        origin=goods_data.origin,
        sale_status=goods_data.sale_status,
        stock_warning=goods_data.stock_warning,
    )
    goods = dao.create_goods(db, goods)

    # 3. 创建规格
    specs = []
    for spec_data in goods_data.specs:
        spec = GoodsSpec(
            id=str(uuid.uuid4()),
            goods_id=goods.id,
            spec_name=spec_data.spec_name,
            spec_value=spec_data.spec_value,
            sort_order=spec_data.sort_order,
        )
        specs.append(spec)
    if specs:
        dao.create_specs_batch(db, specs)

    # 4. 创建库存
    stock = GoodsStock(
        id=str(uuid.uuid4()),
        goods_id=goods.id,
        stock_num=goods_data.stock.stock_num,
        lock_stock=goods_data.stock.lock_stock,
    )
    dao.create_stock(db, stock)

    return goods


def update_goods(db: Session, goods_id: str, update_data: GoodsUpdate):
    goods = dao.get_goods_by_id(db, goods_id)
    if not goods:
        return None
    # 过滤掉 None 值
    update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
    return dao.update_goods(db, goods, update_dict)


def delete_goods(db: Session, goods_id: str):
    goods = dao.get_goods_by_id(db, goods_id)
    if not goods:
        return False
    dao.delete_goods(db, goods)
    return True


def get_goods_detail(db: Session, goods_id: str):
    return dao.get_goods_by_id(db, goods_id)


def get_goods_list(db: Session, filters: dict, page: int = 1, page_size: int = 10):
    skip = (page - 1) * page_size
    return dao.get_goods_list(db, filters, skip, page_size)


def update_stock(db: Session, goods_id: str, delta: int):
    """手动调整库存（正数增加，负数减少）"""
    stock = dao.get_stock_by_goods_id(db, goods_id)
    if not stock:
        raise ValueError("商品库存不存在")

    new_stock = stock.stock_num + delta
    if new_stock < 0:
        raise ValueError("库存不足")

    dao.update_stock(db, stock, stock_num=new_stock)
    return True


def get_low_stock_list(db: Session, custom_threshold: int = None):
    """获取库存预警商品列表"""
    return dao.get_low_stock_goods(db, custom_threshold)