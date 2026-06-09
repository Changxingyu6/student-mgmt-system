
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from services import goods_service as service
from schema.goods_schema import (
    GoodsCreate, GoodsUpdate, GoodsResponse,
    CategoryCreate, CategoryUpdate, CategoryResponse
)
from dao import goods_dao as dao

goods_router = APIRouter(prefix="/goods", tags=["商品管理"])


# ========== 商品分类接口 ==========
#新增商品分类
@goods_router.post("/category", response_model=CategoryResponse, summary="新增分类")
def create_category(category_data: CategoryCreate, db: Session = Depends(get_db)):
    return service.create_category(db, category_data.model_dump())

#修改商品分类
@goods_router.put("/category/{category_id}", response_model=CategoryResponse, summary="修改分类")
def update_category(category_id: str, category_data: CategoryUpdate, db: Session = Depends(get_db)):
    result = service.update_category(db, category_id, category_data.model_dump(exclude_none=True))
    if not result:
        raise HTTPException(status_code=404, detail="分类不存在")
    return result

#删除商品分类
@goods_router.delete("/category/{category_id}", summary="删除分类")
def delete_category(category_id: str, db: Session = Depends(get_db)):
    try:
        success = service.delete_category(db, category_id)
        if not success:
            raise HTTPException(status_code=404, detail="分类不存在")
        return {"message": "删除成功"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

#查询商品分类
@goods_router.get("/category", summary="获取分类列表")
def list_categories(skip: int = 0, limit: int = 30, db: Session = Depends(get_db)):
    return dao.get_all_categories(db, skip, limit)


# ========== 商品接口 ==========
#添加商品
@goods_router.post("/", response_model=GoodsResponse, summary="新增商品")
def create_goods(goods_data: GoodsCreate, db: Session = Depends(get_db)):
    try:
        result = service.create_goods(db, goods_data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


#修改商品
@goods_router.put("/{goods_id}", response_model=GoodsResponse, summary="编辑商品")
def update_goods(goods_id: str, goods_data: GoodsUpdate, db: Session = Depends(get_db)):
    result = service.update_goods(db, goods_id, goods_data)
    if not result:
        raise HTTPException(status_code=404, detail="商品不存在")
    return result


#删除商品
@goods_router.delete("/{goods_id}", summary="删除商品")
def delete_goods(goods_id: str, db: Session = Depends(get_db)):
    success = service.delete_goods(db, goods_id)
    if not success:
        raise HTTPException(status_code=404, detail="商品不存在")
    return {"message": "删除成功"}

#查询商品
@goods_router.get("/{goods_id}", response_model=GoodsResponse, summary="获取商品详情")
def get_goods_detail(goods_id: str, db: Session = Depends(get_db)):
    goods = service.get_goods_detail(db, goods_id)
    if not goods:
        raise HTTPException(status_code=404, detail="商品不存在")
    return goods


@goods_router.get("/", summary="获取商品列表（支持多条件筛选）")
def list_goods(
        goods_id: Optional[str] = Query(None),
        goods_name: Optional[str] = Query(None),
        category_id: Optional[str] = Query(None),
        price_min: Optional[float] = Query(None, ge=0),
        price_max: Optional[float] = Query(None, ge=0),
        sale_status: Optional[int] = Query(None, ge=0, le=1),
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=100),
        db: Session = Depends(get_db)
):
    filters = {
        "goods_id": goods_id,
        "goods_name": goods_name,
        "category_id": category_id,
        "price_min": price_min,
        "price_max": price_max,
        "sale_status": sale_status,
    }
    # 过滤掉 None 值
    filters = {k: v for k, v in filters.items() if v is not None}

    total, items = service.get_goods_list(db, filters, page, page_size)
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items
    }


#修改库存
@goods_router.put("/{goods_id}/stock", summary="手动调整库存")
def adjust_stock(
        goods_id: str,
        delta: int = Query(..., description="调整数量，正数增加，负数减少"),
        db: Session = Depends(get_db)
):
    try:
        service.update_stock(db, goods_id, delta)
        return {"message": "库存调整成功"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

#查询库存
@goods_router.get("/stock/low", summary="库存预警列表")
def low_stock_list(custom_threshold: Optional[int] = Query(None), db: Session = Depends(get_db)):
    result = service.get_low_stock_list(db, custom_threshold)
    # 格式化返回数据
    items = []
    for stock, goods in result:
        items.append({
            "goods_id": goods.id,
            "goods_name": goods.goods_name,
            "goods_no": goods.goods_no,
            "stock_num": stock.stock_num,
            "warning_threshold": goods.stock_warning
        })
    return {"items": items, "total": len(items)}

