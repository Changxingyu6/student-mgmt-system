from sqlalchemy.orm import Session
from model.goods_model import Goods, GoodsCategory, GoodsSpec, GoodsStock


# ========== 商品分类 DAO ==========
def get_category_by_id(db: Session, category_id: str):
    return db.query(GoodsCategory).filter(GoodsCategory.id == category_id).first()


def get_all_categories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(GoodsCategory).order_by(GoodsCategory.sort_order.desc()).offset(skip).limit(limit).all()


def create_category(db: Session, category: GoodsCategory):
    db.add(category)
    return category


def update_category(db: Session, category: GoodsCategory, update_data: dict):
    for key, value in update_data.items():
        setattr(category, key, value)
    return category


def delete_category(db: Session, category: GoodsCategory):
    db.delete(category)


def has_goods_in_category(db: Session, category_id: str):
    return db.query(Goods).filter(Goods.category_id == category_id).first() is not None


# ========== 商品 DAO ==========
def get_goods_by_id(db: Session, goods_id: str):
    return db.query(Goods).filter(Goods.id == goods_id).first()


def get_goods_by_no(db: Session, goods_no: str):
    return db.query(Goods).filter(Goods.goods_no == goods_no).first()


def get_goods_list(db: Session, filters: dict, skip: int = 0, limit: int = 10):
    query = db.query(Goods)

    if filters.get("goods_id"):
        query = query.filter(Goods.id == filters["goods_id"])
    if filters.get("goods_name"):
        query = query.filter(Goods.goods_name.like(f"%{filters['goods_name']}%"))
    if filters.get("category_id"):
        query = query.filter(Goods.category_id == filters["category_id"])
    if filters.get("price_min"):
        query = query.filter(Goods.price >= filters["price_min"])
    if filters.get("price_max"):
        query = query.filter(Goods.price <= filters["price_max"])
    if filters.get("sale_status") is not None:
        query = query.filter(Goods.sale_status == filters["sale_status"])

    total = query.count()
    items = query.order_by(Goods.create_time.desc()).offset(skip).limit(limit).all()
    return total, items


def create_goods(db: Session, goods: Goods):
    db.add(goods)
    return goods


def update_goods(db: Session, goods: Goods, update_data: dict):
    for key, value in update_data.items():
        setattr(goods, key, value)
    return goods


def delete_goods(db: Session, goods: Goods):
    db.delete(goods)


# ========== 商品规格 DAO ==========
def get_specs_by_goods_id(db: Session, goods_id: str):
    return db.query(GoodsSpec).filter(GoodsSpec.goods_id == goods_id).all()


def get_spec_by_id(db: Session, spec_id: str):
    return db.query(GoodsSpec).filter(GoodsSpec.id == spec_id).first()


def create_spec(db: Session, spec: GoodsSpec):
    db.add(spec)
    return spec


def create_specs_batch(db: Session, specs: list):
    db.add_all(specs)
    return specs


def delete_specs_by_goods_id(db: Session, goods_id: str):
    db.query(GoodsSpec).filter(GoodsSpec.goods_id == goods_id).delete()


# ========== 商品库存 DAO ==========
def get_stock_by_goods_id(db: Session, goods_id: str):
    """通过商品ID查询库存（查询该商品所有规格的库存）"""
    return db.query(GoodsStock).join(GoodsSpec).filter(GoodsSpec.goods_id == goods_id).all()


def get_stock_by_spec_id(db: Session, spec_id: str):
    """通过规格ID查询库存"""
    return db.query(GoodsStock).filter(GoodsStock.spec_id == spec_id).first()


def create_stock(db: Session, stock: GoodsStock):
    db.add(stock)
    return stock


def update_stock(db: Session, stock: GoodsStock, stock_num: int):
    stock.stock_num = stock_num
    return stock


def deduct_stock(db: Session, goods_id: str, quantity: int):
    """扣减库存（用于下单）- 旧版，保留兼容"""
    stock = get_stock_by_goods_id(db, goods_id)
    if not stock:
        raise ValueError("库存记录不存在")
    if stock.stock_num < quantity:
        raise ValueError(f"库存不足，当前库存：{stock.stock_num}")
    stock.stock_num -= quantity
    return stock


def get_low_stock_goods(db: Session, custom_threshold: int = None):
    """获取库存预警商品列表"""
    query = db.query(GoodsStock, GoodsSpec, Goods).join(GoodsSpec).join(Goods)
    if custom_threshold is not None:
        query = query.filter(GoodsStock.stock_num <= custom_threshold)
    else:
        query = query.filter(GoodsStock.stock_num <= GoodsStock.warning_stock)
    return query.all()