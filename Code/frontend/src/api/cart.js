import request from './request'

// 获取购物车
export function getCart(userId) {
  return request({
    url: '/shopping-cart/',
    method: 'get',
    params: { user_id: userId }
  })
}

// 添加商品到购物车
export function addToCart(userId, goodsId, specId = null, buyNum = 1) {
  return request({
    url: '/shopping-cart/add',
    method: 'post',
    params: { user_id: userId, goods_id: goodsId, spec_id: specId, buy_num: buyNum }
  })
}

// 更新购物车商品
export function updateCartItem(itemId, userId, buyNum = null, isChecked = null) {
  return request({
    url: `/shopping-cart/item/${itemId}`,
    method: 'put',
    params: { user_id: userId, buy_num: buyNum, is_checked: isChecked }
  })
}

// 删除购物车商品
export function deleteCartItem(itemId, userId) {
  return request({
    url: `/shopping-cart/item/${itemId}`,
    method: 'delete',
    params: { user_id: userId }
  })
}

// 获取购物车所有商品
export function getCartItems(userId) {
  return request({
    url: '/shopping-cart/items',
    method: 'get',
    params: { user_id: userId }
  })
}

// 计算购物车总金额
export function getCartTotal(userId) {
  return request({
    url: '/shopping-cart/total',
    method: 'get',
    params: { user_id: userId }
  })
}