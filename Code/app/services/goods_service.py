
import uuid
from sqlalchemy.orm import Session
from dao import goods_dao as dao
from model.goods_model import Goods, GoodsSpec, GoodsStock
from schema.goods_schema import GoodsCreate, GoodsUpdate, StockBase, SpecCreate, SpecUpdate
from model.goods_model import GoodsCategory

# ========== 商品分类 Service ==========
def create_category(db: Session, category_data: dict):
    category = GoodsCategory(**category_data)
    result = dao.create_category(db, category)
    db.commit()
    return result


def update_category(db: Session, category_id: str, update_data: dict):
    category = dao.get_category_by_id(db, category_id)
    if not category:
        return None
    result = dao.update_category(db, category, update_data)
    db.commit()
    return result


def delete_category(db: Session, category_id: str):
    category = dao.get_category_by_id(db, category_id)
    if not category:
        return False
    if dao.has_goods_in_category(db, category_id):
        raise ValueError("该分类下存在商品，无法删除")
    dao.delete_category(db, category)
    db.commit()
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

    # 3. 创建规格和对应库存（库存关联到规格）
    for spec_data in goods_data.specs:
        # 创建规格
        spec = GoodsSpec(
            id=str(uuid.uuid4()),
            goods_id=goods.id,
            spec_name=spec_data.spec_name,
            spec_value=spec_data.spec_value,
            sort_order=spec_data.sort_order,
        )
        spec = dao.create_spec(db, spec)

        # 创建该规格的库存
        stock = GoodsStock(
            id=str(uuid.uuid4()),
            spec_id=spec.id,
            stock_num=spec_data.stock_num,
            warning_stock=goods_data.stock_warning,
        )
        dao.create_stock(db, stock)

    db.commit()
    return goods


def update_goods(db: Session, goods_id: str, update_data: GoodsUpdate):
    goods = dao.get_goods_by_id(db, goods_id)
    if not goods:
        return None
    # 过滤掉 None 值
    update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
    result = dao.update_goods(db, goods, update_dict)
    db.commit()
    return result


def delete_goods(db: Session, goods_id: str):
    goods = dao.get_goods_by_id(db, goods_id)
    if not goods:
        return False
    dao.delete_goods(db, goods)
    db.commit()
    return True


def get_goods_detail(db: Session, goods_id: str):
    goods = dao.get_goods_by_id(db, goods_id)
    if not goods:
        return None
    
    # 获取商品的规格列表
    specs = dao.get_specs_by_goods_id(db, goods_id)
    
    # 将商品对象转换为字典，并添加规格信息
    goods_dict = goods.__dict__.copy()
    goods_dict.pop('_sa_instance_state', None)
    
    # 处理规格和库存信息
    specs_list = []
    for spec in specs:
        spec_dict = spec.__dict__.copy()
        spec_dict.pop('_sa_instance_state', None)
        
        # 获取规格对应的库存
        stock = dao.get_stock_by_spec_id(db, spec.id)
        if stock:
            stock_dict = stock.__dict__.copy()
            stock_dict.pop('_sa_instance_state', None)
            spec_dict['stock'] = stock_dict
        else:
            spec_dict['stock'] = None
        
        specs_list.append(spec_dict)
    
    goods_dict['specs'] = specs_list
    return goods_dict


def get_goods_list(db: Session, filters: dict, page: int = 1, page_size: int = 10):
    skip = (page - 1) * page_size
    total, goods_list = dao.get_goods_list(db, filters, skip, page_size)
    
    # 遍历每个商品，获取库存信息
    items = []
    for goods in goods_list:
        goods_dict = goods.__dict__.copy()
        goods_dict.pop('_sa_instance_state', None)
        
        # 获取商品的所有规格
        specs = dao.get_specs_by_goods_id(db, goods.id)
        
        # 汇总所有规格的库存，并计算平均预警阈值
        total_stock = 0
        total_warning_stock = 0
        stock_count = 0
        for spec in specs:
            stock = dao.get_stock_by_spec_id(db, spec.id)
            if stock:
                total_stock += stock.stock_num
                total_warning_stock += stock.warning_stock
                stock_count += 1
        
        goods_dict['stock_num'] = total_stock
        # 使用库存表中的预警阈值（取所有规格的平均值，如果没有库存则使用商品表的默认值）
        if stock_count > 0:
            goods_dict['warning_threshold'] = total_warning_stock // stock_count
        else:
            goods_dict['warning_threshold'] = goods.stock_warning
        items.append(goods_dict)
    
    return total, items


def update_stock(db: Session, spec_id: str, delta: int):
    """手动调整库存（正数增加，负数减少）"""
    stock = dao.get_stock_by_spec_id(db, spec_id)
    if not stock:
        raise ValueError("规格库存不存在")

    new_stock = stock.stock_num + delta
    if new_stock < 0:
        raise ValueError("库存不足")

    dao.update_stock(db, stock, stock_num=new_stock)
    db.commit()
    return True


def get_low_stock_list(db: Session, custom_threshold: int = None):
    """获取库存预警商品列表"""
    return dao.get_low_stock_goods(db, custom_threshold)


def deduct_stock_by_spec(db: Session, spec_id: str, quantity: int):
    """扣减库存（用于下单）"""
    stock = dao.get_stock_by_spec_id(db, spec_id)
    if not stock:
        raise ValueError("规格库存不存在")
    if stock.stock_num < quantity:
        raise ValueError(f"库存不足，当前库存：{stock.stock_num}")
    stock.stock_num -= quantity
    db.commit()
    return stock


# ========== 规格管理 Service ==========
def get_specs_by_goods_id(db: Session, goods_id: str):
    """获取商品的所有规格"""
    return dao.get_specs_by_goods_id(db, goods_id)


def create_spec(db: Session, goods_id: str, spec_data: SpecCreate):
    """为商品新增一个规格，并创建对应库存"""
    goods = dao.get_goods_by_id(db, goods_id)
    if not goods:
        return None
    spec = GoodsSpec(
        id=str(uuid.uuid4()),
        goods_id=goods_id,
        spec_name=spec_data.spec_name,
        spec_value=spec_data.spec_value,
        sort_order=spec_data.sort_order,
    )
    spec = dao.create_spec(db, spec)
    stock = GoodsStock(
        id=str(uuid.uuid4()),
        spec_id=spec.id,
        stock_num=spec_data.stock_num,
        warning_stock=spec_data.warning_stock or 10,
    )
    dao.create_stock(db, stock)
    db.commit()
    return spec


def update_spec(db: Session, spec_id: str, spec_data: SpecUpdate):
    """更新规格信息"""
    spec = dao.get_spec_by_id(db, spec_id)
    if not spec:
        return None
    update_dict = {k: v for k, v in spec_data.model_dump().items() if v is not None}
    result = dao.update_spec(db, spec, update_dict)
    db.commit()
    return result


def delete_spec(db: Session, spec_id: str):
    """删除规格及其库存"""
    spec = dao.get_spec_by_id(db, spec_id)
    if not spec:
        return False
    stock = dao.get_stock_by_spec_id(db, spec_id)
    if stock:
        dao.delete_stock(db, stock)
    dao.delete_spec(db, spec)
    db.commit()
    return True


def set_stock_info(db: Session, spec_id: str, stock_num: int, warning_stock: int):
    """直接设置规格的库存和预警阈值（绝对值覆盖）"""
    if stock_num < 0:
        raise ValueError("库存数不能小于 0")
    if warning_stock < 0:
        raise ValueError("预警阈值不能小于 0")
    stock = dao.get_stock_by_spec_id(db, spec_id)
    if not stock:
        raise ValueError("规格库存不存在")
    dao.update_stock(db, stock, stock_num=stock_num, warning_stock=warning_stock)
    db.commit()
    return True