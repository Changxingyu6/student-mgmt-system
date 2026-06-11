import request from './request'

// ============ 商品分类 ============
// 获取分类列表
export function listCategories(params) {
  return request({
    url: '/goods/category',
    method: 'get',
    params
  })
}

// 新增分类
export function createCategory(data) {
  return request({
    url: '/goods/category',
    method: 'post',
    data
  })
}

// 修改分类
export function updateCategory(categoryId, data) {
  return request({
    url: `/goods/category/${categoryId}`,
    method: 'put',
    data
  })
}

// 删除分类
export function deleteCategory(categoryId) {
  return request({
    url: `/goods/category/${categoryId}`,
    method: 'delete'
  })
}

// ============ 商品 ============
// 获取商品列表
export function listGoods(params) {
  return request({
    url: '/goods/',
    method: 'get',
    params
  })
}

// 获取商品详情
export function getGoodsDetail(goodsId) {
  return request({
    url: `/goods/${goodsId}`,
    method: 'get'
  })
}

// 新增商品
export function createGoods(data) {
  return request({
    url: '/goods/',
    method: 'post',
    data
  })
}

// 修改商品
export function updateGoods(goodsId, data) {
  return request({
    url: `/goods/${goodsId}`,
    method: 'put',
    data
  })
}

// 删除商品
export function deleteGoods(goodsId) {
  return request({
    url: `/goods/${goodsId}`,
    method: 'delete'
  })
}

// ============ 库存 ============
// 调整库存（按规格）
export function adjustStock(specId, delta) {
  return request({
    url: `/goods/spec/${specId}/stock`,
    method: 'put',
    params: { delta }
  })
}

// 库存预警列表
export function getLowStock(threshold) {
  return request({
    url: '/goods/stock/low',
    method: 'get',
    params: threshold ? { custom_threshold: threshold } : {}
  })
}

// ============ 商品规格 ============
// 获取商品规格列表
export function listGoodsSpecs(goodsId) {
  return request({
    url: `/goods/${goodsId}/spec`,
    method: 'get'
  })
}

// 为商品新增规格
export function createGoodsSpec(goodsId, data) {
  return request({
    url: `/goods/${goodsId}/spec`,
    method: 'post',
    data
  })
}

// 更新规格
export function updateGoodsSpec(specId, data) {
  return request({
    url: `/goods/spec/${specId}`,
    method: 'put',
    data
  })
}

// 删除规格
export function deleteGoodsSpec(specId) {
  return request({
    url: `/goods/spec/${specId}`,
    method: 'delete'
  })
}

// 直接设置规格库存和阈值（绝对值）
export function setSpecStockInfo(specId, stockNum, warningStock) {
  return request({
    url: `/goods/spec/${specId}/stock-info`,
    method: 'put',
    params: { stock_num: stockNum, warning_stock: warningStock }
  })
}
