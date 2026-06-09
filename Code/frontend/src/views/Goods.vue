<template>
  <div class="goods-page">
    <h2 class="page-title">{{ isAdmin ? '商品管理' : '商品列表' }}</h2>

    <!-- 顶部 Tab 切换 -->
    <el-tabs v-model="activeTab" @tab-change="handleTabChange">
      <el-tab-pane label="商品列表" name="list"></el-tab-pane>
      <el-tab-pane v-if="isAdmin" label="分类管理" name="category"></el-tab-pane>
      <el-tab-pane v-if="isAdmin" label="库存预警" name="stock"></el-tab-pane>
    </el-tabs>

    <!-- ============ 商品列表 ============ -->
    <div v-show="activeTab === 'list'">
      <!-- 搜索栏 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="商品名称">
          <el-input v-model="searchForm.goods_name" placeholder="请输入商品名称" clearable />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="searchForm.category_id" placeholder="全部" clearable style="width: 160px">
            <el-option
              v-for="c in categories"
              :key="c.id"
              :label="c.category_name"
              :value="c.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="价格区间">
          <el-input v-model="searchForm.price_min" placeholder="最低" style="width: 100px" clearable />
          <span style="margin: 0 8px">-</span>
          <el-input v-model="searchForm.price_max" placeholder="最高" style="width: 100px" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.sale_status" placeholder="全部" clearable style="width: 120px">
            <el-option label="在售" :value="1" />
            <el-option label="下架" :value="0" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <div class="toolbar">
        <el-button type="primary" @click="handleAddGoods">+ 新增商品</el-button>
      </div>

      <!-- 商品列表 -->
      <el-table :data="goodsList" v-loading="loading" border stripe>
        <el-table-column label="商品图" width="80">
          <template #default="{ row }">
            <el-image
              v-if="row.main_image"
              :src="row.main_image"
              :preview-src-list="[row.main_image]"
              style="width: 50px; height: 50px; border-radius: 4px"
              fit="cover"
            />
            <span v-else class="no-image">无图</span>
          </template>
        </el-table-column>
        <el-table-column prop="goods_name" label="商品名称" min-width="180" show-overflow-tooltip />
        <el-table-column prop="goods_no" label="商品编号" width="140" />
        <el-table-column label="分类" width="120">
          <template #default="{ row }">
            {{ getCategoryName(row.category_id) }}
          </template>
        </el-table-column>
        <el-table-column label="售价" width="100">
          <template #default="{ row }">¥{{ row.price }}</template>
        </el-table-column>
        <el-table-column label="原价" width="100">
          <template #default="{ row }">¥{{ row.original_price || '-' }}</template>
        </el-table-column>
        <el-table-column label="库存" width="80">
          <template #default="{ row }">{{ row.stock_num ?? 0 }}</template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.sale_status === 1 ? 'success' : 'info'">
              {{ row.sale_status === 1 ? '在售' : '下架' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="170">
          <template #default="{ row }">
            {{ formatDate(row.create_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{ row }">
            <el-button v-if="!isAdmin" size="small" type="primary" @click="handleAddToCart(row)">加入购物车</el-button>
            <template v-if="isAdmin">
              <el-button size="small" @click="handleEditGoods(row)">编辑</el-button>
              <el-button size="small" type="warning" @click="handleAdjustStock(row)">库存</el-button>
              <el-button size="small" type="danger" @click="handleDeleteGoods(row)">删除</el-button>
            </template>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.page_size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadGoodsList"
          @current-change="loadGoodsList"
        />
      </div>
    </div>

    <!-- ============ 分类管理 ============ -->
    <div v-show="activeTab === 'category'">
      <div class="toolbar">
        <el-button type="primary" @click="handleAddCategory">+ 新增分类</el-button>
      </div>

      <el-table :data="categories" v-loading="categoryLoading" border stripe>
        <el-table-column prop="category_name" label="分类名称" min-width="180" />
        <el-table-column prop="parent_id" label="父级ID" width="100" />
        <el-table-column prop="sort_order" label="排序" width="80" />
        <el-table-column prop="icon" label="图标" width="100" />
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'">
              {{ row.status === 1 ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="170">
          <template #default="{ row }">
            {{ formatDate(row.create_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleEditCategory(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDeleteCategory(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- ============ 库存预警 ============ -->
    <div v-show="activeTab === 'stock'">
      <el-form :inline="true" class="search-form">
        <el-form-item label="自定义阈值">
          <el-input v-model="stockThreshold" placeholder="留空使用商品自身阈值" style="width: 200px" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadLowStock">查询</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="lowStockList" v-loading="lowStockLoading" border stripe>
        <el-table-column prop="goods_name" label="商品名称" min-width="180" />
        <el-table-column prop="goods_no" label="商品编号" width="140" />
        <el-table-column prop="stock_num" label="当前库存" width="120">
          <template #default="{ row }">
            <el-tag type="danger">{{ row.stock_num }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="warning_threshold" label="预警阈值" width="120" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="warning" @click="handleQuickReplenish(row)">补货</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 商品编辑弹窗 -->
    <el-dialog
      v-model="goodsDialogVisible"
      :title="goodsForm.id ? '编辑商品' : '新增商品'"
      width="600px"
    >
      <el-form :model="goodsForm" label-width="100px">
        <el-form-item label="商品编号" v-if="!goodsForm.id">
          <el-input v-model="goodsForm.goods_no" placeholder="请输入商品编号" />
        </el-form-item>
        <el-form-item label="商品名称">
          <el-input v-model="goodsForm.goods_name" placeholder="请输入商品名称" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="goodsForm.category_id" placeholder="请选择分类" style="width: 100%">
            <el-option
              v-for="c in categories"
              :key="c.id"
              :label="c.category_name"
              :value="c.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="售价">
          <el-input-number v-model="goodsForm.price" :precision="2" :min="0" :step="0.01" />
        </el-form-item>
        <el-form-item label="原价">
          <el-input-number v-model="goodsForm.original_price" :precision="2" :min="0" :step="0.01" />
        </el-form-item>
        <el-form-item label="品牌">
          <el-input v-model="goodsForm.brand" placeholder="选填" />
        </el-form-item>
        <el-form-item label="产地">
          <el-input v-model="goodsForm.origin" placeholder="选填" />
        </el-form-item>
        <el-form-item label="主图URL">
          <el-input v-model="goodsForm.main_image" placeholder="选填" />
        </el-form-item>
        <el-form-item label="商品简介">
          <el-input v-model="goodsForm.intro" type="textarea" :rows="3" placeholder="选填" />
        </el-form-item>
        <el-form-item label="状态" v-if="goodsForm.id">
          <el-radio-group v-model="goodsForm.sale_status">
            <el-radio :value="1">在售</el-radio>
            <el-radio :value="0">下架</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="库存预警" v-if="!goodsForm.id">
          <el-input-number v-model="goodsForm.stock_warning" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="goodsDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveGoods">保存</el-button>
      </template>
    </el-dialog>

    <!-- 分类编辑弹窗 -->
    <el-dialog
      v-model="categoryDialogVisible"
      :title="categoryForm.id ? '编辑分类' : '新增分类'"
      width="500px"
    >
      <el-form :model="categoryForm" label-width="100px">
        <el-form-item label="分类名称">
          <el-input v-model="categoryForm.category_name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="父级ID">
          <el-input v-model="categoryForm.parent_id" placeholder="0 表示顶级" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="categoryForm.sort_order" :min="0" />
        </el-form-item>
        <el-form-item label="图标">
          <el-input v-model="categoryForm.icon" placeholder="选填" />
        </el-form-item>
        <el-form-item label="状态" v-if="categoryForm.id">
          <el-radio-group v-model="categoryForm.status">
            <el-radio :value="1">启用</el-radio>
            <el-radio :value="0">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="categoryDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveCategory">保存</el-button>
      </template>
    </el-dialog>

    <!-- 库存调整弹窗 -->
    <el-dialog v-model="stockDialogVisible" title="调整库存" width="400px">
      <el-form :model="stockForm" label-width="100px">
        <el-form-item label="商品">
          <span>{{ stockForm.goods_name }}</span>
        </el-form-item>
        <el-form-item label="规格">
          <el-select v-model="stockForm.spec_id" style="width: 100%" @change="onSpecChange">
            <el-option
              v-for="spec in stockForm.specs"
              :key="spec.id"
              :label="`${spec.spec_name}: ${spec.spec_value}`"
              :value="spec.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="当前库存">
          <span>{{ stockForm.current_stock }}</span>
        </el-form-item>
        <el-form-item label="调整数量">
          <el-input-number v-model="stockForm.delta" :step="1" />
          <div class="tip">正数增加，负数减少</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="stockDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveStock">保存</el-button>
      </template>
    </el-dialog>

    <!-- 加入购物车弹窗 -->
    <el-dialog v-model="cartDialogVisible" title="加入购物车" width="400px">
      <el-form :model="cartForm" label-width="100px">
        <el-form-item label="商品">
          <span>{{ cartForm.goods_name }}</span>
        </el-form-item>
        <el-form-item label="规格" prop="spec_id">
          <el-select v-model="cartForm.spec_id" style="width: 100%" placeholder="请选择规格" @change="onCartSpecChange">
            <el-option
              v-for="spec in cartForm.specs"
              :key="spec.id"
              :label="`${spec.spec_name}: ${spec.spec_value}`"
              :value="spec.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="数量" prop="quantity">
          <el-input-number v-model="cartForm.quantity" :step="1" :min="1" :max="cartForm.current_stock" />
        </el-form-item>
        <el-form-item label="库存">
          <span>剩余 {{ cartForm.current_stock }} 件</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="cartDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmAddToCart">确认加入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  listCategories, createCategory, updateCategory, deleteCategory,
  listGoods, getGoodsDetail, createGoods, updateGoods, deleteGoods,
  adjustStock, getLowStock
} from '@/api/goods'
import { useUserStore } from '@/stores/user'
import { addToCart } from '@/api/cart'

const userStore = useUserStore()
const isAdmin = computed(() => userStore.userInfo?.role === 'admin')

// 当前 Tab
const activeTab = ref('list')

// ============ 商品列表 ============
const loading = ref(false)
const goodsList = ref([])
const searchForm = reactive({
  goods_name: '',
  category_id: '',
  price_min: '',
  price_max: '',
  sale_status: ''
})
const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

const loadGoodsList = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      ...searchForm
    }
    // 过滤空值
    Object.keys(params).forEach(k => {
      if (params[k] === '' || params[k] === null || params[k] === undefined) {
        delete params[k]
      }
    })
    const res = await listGoods(params)
    if (res.code === 200 || res.data) {
      goodsList.value = res.items || res.data?.items || []
      pagination.total = res.total || res.data?.total || 0
    }
  } catch (e) {
    console.error('加载商品列表失败:', e)
    ElMessage.error('加载商品列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadGoodsList()
}

const handleReset = () => {
  Object.assign(searchForm, {
    goods_name: '',
    category_id: '',
    price_min: '',
    price_max: '',
    sale_status: ''
  })
  pagination.page = 1
  loadGoodsList()
}

// ============ 商品编辑 ============
const goodsDialogVisible = ref(false)
const goodsForm = reactive({
  id: '',
  goods_no: '',
  goods_name: '',
  category_id: '',
  price: 0,
  original_price: 0,
  brand: '',
  origin: '',
  main_image: '',
  intro: '',
  sale_status: 1,
  stock_warning: 10
})

const handleAddGoods = () => {
  Object.assign(goodsForm, {
    id: '',
    goods_no: '',
    goods_name: '',
    category_id: '',
    price: 0,
    original_price: 0,
    brand: '',
    origin: '',
    main_image: '',
    intro: '',
    sale_status: 1,
    stock_warning: 10
  })
  goodsDialogVisible.value = true
}

const handleEditGoods = async (row) => {
  try {
    const res = await getGoodsDetail(row.id)
    const data = res.data || res
    Object.assign(goodsForm, data)
    goodsDialogVisible.value = true
  } catch (e) {
    console.error('获取商品详情失败:', e)
    ElMessage.error('获取商品详情失败')
  }
}

const handleSaveGoods = async () => {
  if (!goodsForm.goods_name || !goodsForm.category_id || !goodsForm.price) {
    ElMessage.warning('请填写商品名称、分类和售价')
    return
  }
  try {
    if (goodsForm.id) {
      await updateGoods(goodsForm.id, {
        goods_name: goodsForm.goods_name,
        category_id: goodsForm.category_id,
        price: goodsForm.price,
        original_price: goodsForm.original_price,
        brand: goodsForm.brand,
        origin: goodsForm.origin,
        main_image: goodsForm.main_image,
        intro: goodsForm.intro,
        sale_status: goodsForm.sale_status
      })
      ElMessage.success('修改成功')
    } else {
      if (!goodsForm.goods_no) {
        ElMessage.warning('请填写商品编号')
        return
      }
      await createGoods({
        goods_no: goodsForm.goods_no,
        goods_name: goodsForm.goods_name,
        category_id: goodsForm.category_id,
        price: goodsForm.price,
        original_price: goodsForm.original_price,
        brand: goodsForm.brand,
        origin: goodsForm.origin,
        main_image: goodsForm.main_image,
        intro: goodsForm.intro,
        stock_warning: goodsForm.stock_warning
      })
      ElMessage.success('新增成功')
    }
    goodsDialogVisible.value = false
    loadGoodsList()
  } catch (e) {
    console.error('保存商品失败:', e)
    ElMessage.error(e.response?.data?.detail || e.message || '保存失败')
  }
}

const handleDeleteGoods = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除商品"${row.goods_name}"？`, '提示', { type: 'warning' })
    await deleteGoods(row.id)
    ElMessage.success('删除成功')
    loadGoodsList()
  } catch (e) {
    if (e !== 'cancel') {
      console.error('删除商品失败:', e)
      ElMessage.error('删除失败')
    }
  }
}

// ============ 加入购物车 ============
const cartDialogVisible = ref(false)
const cartForm = reactive({
  spec_id: '',
  goods_id: '',
  goods_name: '',
  quantity: 1,
  current_stock: 0,
  specs: []
})

const handleAddToCart = async (row) => {
  const userId = userStore.userInfo?.id
  if (!userId) { 
    ElMessage.warning('请先登录')
    return 
  }
  
  try {
    // 获取商品详情（包含规格信息）
    const res = await getGoodsDetail(row.id)
    const data = res.data || res
    
    // 获取规格列表
    const specs = data.specs || []
    
    if (specs.length === 0) {
      ElMessage.warning('该商品暂无规格信息')
      return
    }
    
    // 默认选择第一个规格
    const firstSpec = specs[0]
    
    Object.assign(cartForm, {
      spec_id: firstSpec.id,
      goods_id: row.id,
      goods_name: row.goods_name,
      quantity: 1,
      current_stock: firstSpec.stock?.stock_num ?? 0,
      specs: specs
    })
    cartDialogVisible.value = true
  } catch (e) {
    console.error('获取商品规格失败:', e)
    ElMessage.error('获取商品规格失败')
  }
}

const onCartSpecChange = (specId) => {
  // 切换规格时更新当前库存
  const spec = cartForm.specs.find(s => s.id === specId)
  if (spec) {
    cartForm.current_stock = spec.stock?.stock_num ?? 0
    // 如果当前数量超过新规格的库存，重置为1
    if (cartForm.quantity > cartForm.current_stock) {
      cartForm.quantity = 1
    }
  }
}

const handleConfirmAddToCart = async () => {
  if (!cartForm.spec_id) {
    ElMessage.warning('请选择规格')
    return
  }
  
  if (cartForm.quantity <= 0) {
    ElMessage.warning('请输入有效的数量')
    return
  }
  
  const userId = userStore.userInfo?.id
  try {
    const res = await addToCart(userId, cartForm.goods_id, cartForm.spec_id, cartForm.quantity)
    if (res.status === 'success') {
      ElMessage.success('已加入购物车')
      cartDialogVisible.value = false
    } else {
      ElMessage.error(res.cart_status || '加入购物车失败')
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '加入购物车失败')
  }
}

// ============ 库存调整 ============
const stockDialogVisible = ref(false)
const stockForm = reactive({
  spec_id: '',
  goods_name: '',
  goods_id: '',
  current_stock: 0,
  delta: 0,
  specs: []  // 存储商品的规格列表
})

const handleAdjustStock = async (row) => {
  try {
    // 获取商品详情（包含规格信息）
    const res = await getGoodsDetail(row.id)
    const data = res.data || res
    
    // 获取规格列表
    const specs = data.specs || []
    
    if (specs.length === 0) {
      ElMessage.warning('该商品暂无规格信息')
      return
    }
    
    // 默认选择第一个规格
    const firstSpec = specs[0]
    
    Object.assign(stockForm, {
      spec_id: firstSpec.id,
      goods_name: row.goods_name,
      goods_id: row.id,
      current_stock: firstSpec.stock?.stock_num ?? 0,
      delta: 0,
      specs: specs
    })
    stockDialogVisible.value = true
  } catch (e) {
    console.error('获取商品规格失败:', e)
    ElMessage.error('获取商品规格失败')
  }
}

const onSpecChange = (specId) => {
  // 切换规格时更新当前库存
  const spec = stockForm.specs.find(s => s.id === specId)
  if (spec) {
    stockForm.current_stock = spec.stock?.stock_num ?? 0
  }
}

const handleSaveStock = async () => {
  try {
    await adjustStock(stockForm.spec_id, stockForm.delta)
    ElMessage.success('库存调整成功')
    stockDialogVisible.value = false
    loadGoodsList()
  } catch (e) {
    console.error('库存调整失败:', e)
    ElMessage.error('库存调整失败')
  }
}

const handleQuickReplenish = (row) => {
  Object.assign(stockForm, {
    spec_id: row.spec_id,
    goods_name: row.goods_name,
    current_stock: row.stock_num,
    delta: row.warning_threshold * 5
  })
  stockDialogVisible.value = true
}

// ============ 分类管理 ============
const categoryLoading = ref(false)
const categories = ref([])

const loadCategories = async () => {
  categoryLoading.value = true
  try {
    const res = await listCategories({ skip: 0, limit: 100 })
    categories.value = res.data || res || []
  } catch (e) {
    console.error('加载分类失败:', e)
    ElMessage.error('加载分类失败')
  } finally {
    categoryLoading.value = false
  }
}

const getCategoryName = (id) => {
  const cat = categories.value.find(c => c.id === id)
  return cat ? cat.category_name : '-'
}

const categoryDialogVisible = ref(false)
const categoryForm = reactive({
  id: '',
  category_name: '',
  parent_id: '0',
  sort_order: 0,
  icon: '',
  status: 1
})

const handleAddCategory = () => {
  Object.assign(categoryForm, {
    id: '',
    category_name: '',
    parent_id: '0',
    sort_order: 0,
    icon: '',
    status: 1
  })
  categoryDialogVisible.value = true
}

const handleEditCategory = (row) => {
  Object.assign(categoryForm, row)
  categoryDialogVisible.value = true
}

const handleSaveCategory = async () => {
  if (!categoryForm.category_name) {
    ElMessage.warning('请填写分类名称')
    return
  }
  try {
    if (categoryForm.id) {
      await updateCategory(categoryForm.id, {
        category_name: categoryForm.category_name,
        sort_order: categoryForm.sort_order,
        icon: categoryForm.icon,
        status: categoryForm.status
      })
      ElMessage.success('修改成功')
    } else {
      await createCategory({
        category_name: categoryForm.category_name,
        parent_id: categoryForm.parent_id,
        sort_order: categoryForm.sort_order,
        icon: categoryForm.icon,
        status: categoryForm.status
      })
      ElMessage.success('新增成功')
    }
    categoryDialogVisible.value = false
    loadCategories()
  } catch (e) {
    console.error('保存分类失败:', e)
    ElMessage.error('保存失败')
  }
}

const handleDeleteCategory = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除分类"${row.category_name}"？`, '提示', { type: 'warning' })
    await deleteCategory(row.id)
    ElMessage.success('删除成功')
    loadCategories()
  } catch (e) {
    if (e !== 'cancel') {
      console.error('删除分类失败:', e)
      ElMessage.error(e.response?.data?.detail || '删除失败')
    }
  }
}

// ============ 库存预警 ============
const lowStockLoading = ref(false)
const lowStockList = ref([])
const stockThreshold = ref('')

const loadLowStock = async () => {
  lowStockLoading.value = true
  try {
    const res = await getLowStock(stockThreshold.value ? Number(stockThreshold.value) : undefined)
    if (res.code === 200 || res.data) {
      lowStockList.value = res.items || res.data?.items || []
    }
  } catch (e) {
    console.error('加载库存预警失败:', e)
    ElMessage.error('加载库存预警失败')
  } finally {
    lowStockLoading.value = false
  }
}

const handleTabChange = (tab) => {
  if (tab === 'list') loadGoodsList()
  else if (tab === 'category') loadCategories()
  else if (tab === 'stock') loadLowStock()
}

// 格式化日期
const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN', { hour12: false })
}

onMounted(() => {
  loadCategories()
  loadGoodsList()
})
</script>

<style scoped>
.goods-page {
  padding: 20px;
}
.page-title {
  margin-top: 0;
  margin-bottom: 20px;
}
.search-form {
  background: #f5f7fa;
  padding: 18px 18px 0 18px;
  border-radius: 4px;
  margin-bottom: 16px;
}
.toolbar {
  margin-bottom: 16px;
}
.pagination {
  margin-top: 20px;
  text-align: right;
}
.no-image {
  display: inline-block;
  width: 50px;
  height: 50px;
  line-height: 50px;
  text-align: center;
  background: #f0f0f0;
  color: #999;
  border-radius: 4px;
  font-size: 12px;
}
.tip {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}
</style>
