<template>
  <div class="goods-page">
    <h2 class="page-title">{{ isAdmin ? '商品管理' : '商品列表' }}</h2>

    <!-- 顶部 Tab 切换 -->
    <el-tabs v-model="activeTab" @tab-change="handleTabChange">
      <el-tab-pane label="商品列表" name="list"></el-tab-pane>
      <el-tab-pane v-if="isAdmin" label="分类管理" name="category"></el-tab-pane>
      <el-tab-pane v-if="isAdmin" label="规格管理" name="spec"></el-tab-pane>
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
        <el-button v-if="isAdmin" type="primary" @click="handleAddGoods">+ 新增商品</el-button>
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
          :page-sizes="[5, 10, 20, 50]"
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

    <!-- ============ 规格管理 ============ -->
    <div v-show="activeTab === 'spec'">
      <el-form :inline="true" class="search-form">
        <el-form-item label="选择商品">
          <el-select v-model="specFilterGoodsId" placeholder="请选择商品" filterable clearable style="width: 280px" @change="loadSpecList">
            <el-option v-for="g in goodsList" :key="g.id" :label="g.goods_name" :value="g.id" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :disabled="!specFilterGoodsId" @click="handleAddSpec">+ 新增规格</el-button>
        </el-form-item>
        <el-form-item>
          <el-button :disabled="!specFilterGoodsId" @click="loadSpecList">刷新</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="specList" v-loading="specLoading" border stripe>
        <el-table-column prop="spec_name" label="规格名" width="140" />
        <el-table-column prop="spec_value" label="规格值" />
        <el-table-column label="库存" width="100">
          <template #default="{ row }">{{ row.stock?.stock_num ?? 0 }}</template>
        </el-table-column>
        <el-table-column label="预警阈值" width="100">
          <template #default="{ row }">{{ row.stock?.warning_stock ?? '-' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openSpecDialog(row)">调整库存</el-button>
            <el-button size="small" type="danger" @click="handleDeleteSpec(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 规格编辑弹窗（规格信息只读，仅可调整库存与阈值） -->
      <el-dialog v-model="specDialogVisible" title="调整库存与阈值" width="480px">
        <el-form :model="specForm" label-width="90px">
          <!-- 区块 1：规格信息（只读） -->
          <div class="form-section-title">规格信息</div>
          <el-form-item label="规格名">
            <el-input v-model="specForm.spec_name" disabled />
          </el-form-item>
          <el-form-item label="规格值">
            <el-input v-model="specForm.spec_value" disabled />
          </el-form-item>

          <el-divider />

          <!-- 区块 2：库存与阈值（可编辑） -->
          <div class="form-section-title">库存与阈值</div>
          <el-form-item label="当前库存">
            <el-input-number v-model="specForm.stock_num" :min="0" :max="99999" />
          </el-form-item>
          <el-form-item label="预警阈值">
            <el-input-number v-model="specForm.warning_stock" :min="0" :max="9999" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="specDialogVisible = false">取消</el-button>
          <el-button type="success" @click="handleSaveStockOnly" :disabled="!specForm.id">保存</el-button>
        </template>
      </el-dialog>

      <!-- 新增规格弹窗 -->
      <el-dialog v-model="addSpecDialogVisible" title="新增规格" width="480px">
        <el-form :model="addSpecForm" label-width="90px">
          <el-form-item label="规格名">
            <el-input v-model="addSpecForm.spec_name" placeholder="如：颜色 / 尺寸" />
          </el-form-item>
          <el-form-item label="规格值">
            <el-input v-model="addSpecForm.spec_value" placeholder="如：黑色 / 256GB" />
          </el-form-item>
          <el-form-item label="当前库存">
            <el-input-number v-model="addSpecForm.stock_num" :min="0" :max="99999" />
          </el-form-item>
          <el-form-item label="预警阈值">
            <el-input-number v-model="addSpecForm.warning_stock" :min="0" :max="9999" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="addSpecDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitAddSpec">保存</el-button>
        </template>
      </el-dialog>
    </div>

    <!-- ============ 库存预警 ============ -->
    <div v-show="activeTab === 'stock'">
      <el-table :data="lowStockList" v-loading="lowStockLoading" border stripe>
        <el-table-column prop="goods_name" label="商品名称" min-width="160" show-overflow-tooltip />
        <el-table-column prop="goods_no" label="商品编号" width="140" />
        <el-table-column prop="spec_name" label="规格名" width="100" />
        <el-table-column prop="spec_value" label="规格值" width="120" show-overflow-tooltip />
        <el-table-column prop="stock_num" label="当前库存" width="100">
          <template #default="{ row }">
            <el-tag type="danger">{{ row.stock_num }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="warning_threshold" label="预警阈值" width="100" />
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
        <el-form-item label="库存预警" v-if="!goodsForm.id" style="display: none;">
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
          <!-- 固定规格（库存预警的补货）用纯文本 -->
          <span v-if="stockForm.fixed">
            {{ stockForm.spec_name }}: {{ stockForm.spec_value }}
          </span>
          <!-- 多规格（商品列表的库存调整）用下拉 -->
          <el-select
            v-else
            v-model="stockForm.spec_id"
            style="width: 100%"
            @change="onSpecChange"
          >
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
  adjustStock, getLowStock,
  listGoodsSpecs, createGoodsSpec, updateGoodsSpec, deleteGoodsSpec,
  setSpecStockInfo
} from '@/api/goods'
import { useUserStore } from '@/stores/user'
import { addToCart } from '@/api/cart'

const userStore = useUserStore()
const isAdmin = computed(() => userStore.userInfo?.role === 'admin')

// 当前 Tab
const activeTab = ref('list')

// ============ 规格管理 ============
const specFilterGoodsId = ref('')
const specList = ref([])
const specLoading = ref(false)
const specDialogVisible = ref(false)
const specForm = reactive({
  id: '',
  goods_id: '',
  spec_name: '',
  spec_value: '',
  stock_num: 0,
  warning_stock: 10,
  // 编辑模式下保存原始值，用于判断是否变化
  _origStockNum: 0,
  _origWarningStock: 10
})

// 新增规格弹窗
const addSpecDialogVisible = ref(false)
const addSpecForm = reactive({
  spec_name: '',
  spec_value: '',
  stock_num: 0,
  warning_stock: 10
})

const resetAddSpecForm = () => {
  addSpecForm.spec_name = ''
  addSpecForm.spec_value = ''
  addSpecForm.stock_num = 0
  addSpecForm.warning_stock = 10
}

const handleAddSpec = () => {
  if (!specFilterGoodsId.value) {
    ElMessage.warning('请先选择商品')
    return
  }
  resetAddSpecForm()
  addSpecDialogVisible.value = true
}

const submitAddSpec = async () => {
  if (!addSpecForm.spec_name || !addSpecForm.spec_value) {
    ElMessage.warning('请填写规格名和规格值')
    return
  }
  try {
    // 1) 创建规格（只传规格名 + 规格值）
    const createRes = await createGoodsSpec(specFilterGoodsId.value, {
      spec_name: addSpecForm.spec_name,
      spec_value: addSpecForm.spec_value
    })
    // 2) 后端若返回 spec_id，则用 setSpecStockInfo 设置库存与阈值
    const newSpecId = createRes?.id || createRes?.data?.id
    if (newSpecId) {
      try {
        await setSpecStockInfo(newSpecId, addSpecForm.stock_num, addSpecForm.warning_stock)
      } catch (stockErr) {
        console.warn('设置库存失败（不影响规格创建）:', stockErr)
      }
    }
    ElMessage.success('规格新增成功')
    addSpecDialogVisible.value = false
    loadSpecList()
  } catch (e) {
    console.error('新增规格失败:', e)
    ElMessage.error(e.response?.data?.detail || '新增规格失败')
  }
}

const loadSpecList = async () => {
  if (!specFilterGoodsId.value) {
    specList.value = []
    return
  }
  specLoading.value = true
  try {
    const res = await listGoodsSpecs(specFilterGoodsId.value)
    specList.value = res.items || res.data?.items || []
  } catch (e) {
    console.error('加载规格失败:', e)
    ElMessage.error('加载规格失败')
  } finally {
    specLoading.value = false
  }
}

const openSpecDialog = (row) => {
  // 弹窗只用于调整库存和阈值，规格名/规格值只读
  const stockNum = row.stock?.stock_num ?? 0
  const warningStock = row.stock?.warning_stock ?? 10
  specForm.id = row.id
  specForm.goods_id = row.goods_id
  specForm.spec_name = row.spec_name
  specForm.spec_value = row.spec_value
  specForm.stock_num = stockNum
  specForm.warning_stock = warningStock
  specForm._origStockNum = stockNum
  specForm._origWarningStock = warningStock
  specDialogVisible.value = true
}

// 只保存库存/预警阈值
const handleSaveStockOnly = async () => {
  if (!specForm.id) {
    ElMessage.warning('请先保存规格')
    return
  }
  if (specForm.stock_num === specForm._origStockNum &&
      specForm.warning_stock === specForm._origWarningStock) {
    ElMessage.info('库存和阈值未变化，无需保存')
    return
  }
  try {
    await setSpecStockInfo(specForm.id, specForm.stock_num, specForm.warning_stock)
    // 更新原始值
    specForm._origStockNum = specForm.stock_num
    specForm._origWarningStock = specForm.warning_stock
    ElMessage.success('库存更新成功')
    specDialogVisible.value = false
    loadSpecList()
  } catch (e) {
    console.error('保存库存失败:', e)
    ElMessage.error(e.response?.data?.detail || '保存库存失败')
  }
}

const handleDeleteSpec = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除规格 "${row.spec_name}: ${row.spec_value}" 吗？该操作会同时删除对应库存。`,
      '提示', { type: 'warning' }
    )
    await deleteGoodsSpec(row.id)
    ElMessage.success('规格删除成功')
    loadSpecList()
  } catch (e) {
    if (e !== 'cancel') {
      console.error('删除规格失败:', e)
      ElMessage.error('删除规格失败')
    }
  }
}

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
  page_size: 5,
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
    if (res.code === 200) {
      ElMessage.success('已加入购物车')
      cartDialogVisible.value = false
    } else {
      ElMessage.error(res.message || '加入购物车失败')
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
  // 库存预警 Tab 的补货：规格固定为当前预警规格，不提供下拉选择
  Object.assign(stockForm, {
    spec_id: row.spec_id,
    goods_name: row.goods_name,
    spec_name: row.spec_name || '',
    spec_value: row.spec_value || '',
    current_stock: row.stock_num,
    delta: row.warning_threshold * 5,
    specs: []
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

const loadLowStock = async () => {
  lowStockLoading.value = true
  try {
    // 后端按 stock_num <= warning_stock 过滤，此处不传自定义阈值
    const res = await getLowStock()
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
  else if (tab === 'spec') loadGoodsList()
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
.form-section-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}
.form-section-tip {
  font-size: 12px;
  font-weight: normal;
  color: #909399;
  margin-left: 6px;
}
</style>
