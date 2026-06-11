<template>
  <div class="cart-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>购物车</span>
          <el-button type="danger" @click="handleClearSelected">
            删除选中
          </el-button>
        </div>
      </template>

      <!-- 购物车列表 -->
      <el-table 
        :data="cartItems" 
        border 
        style="width: 100%" 
        @selection-change="handleSelectionChange"
        ref="tableRef"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="goods_name" label="商品名称" width="200" />
        <el-table-column prop="spec_name" label="规格" width="150" />
        <el-table-column prop="price" label="单价" width="120">
          <template #default="{ row }">
            ¥{{ row.price }}
          </template>
        </el-table-column>
        <el-table-column prop="buy_num" label="数量" width="150">
          <template #default="{ row }">
            <el-input-number v-model="row.buy_num" :min="1" :max="99" size="small" @change="handleUpdateNum(row)" />
          </template>
        </el-table-column>
        <el-table-column label="小计" width="120">
          <template #default="{ row }">
            ¥{{ (row.price * row.buy_num).toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column label="选中" width="80">
          <template #default="{ row }">
            <el-switch v-model="row.is_checked" @change="handleSwitchChange(row)" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="danger" size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 总计 -->
      <div class="cart-footer">
        <div class="total-info">
          <span>已选 {{ selectedCount }} 件商品</span>
          <span class="total-price">总计: ¥{{ totalPrice.toFixed(2) }}</span>
        </div>
        <el-button type="primary" size="large" @click="handleCheckout">
          结算
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getCart, updateCartItem, deleteCartItem } from '@/api/cart'
import { createOrderFromCart } from '@/api/order'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const cartItems = ref([])
const selectedItems = ref([])
const tableRef = ref(null)

const selectedCount = computed(() => selectedItems.value.length)
const totalPrice = computed(() => {
  return selectedItems.value.reduce((sum, item) => sum + item.price * item.buy_num, 0)
})

const loadCart = async () => {
  try {
    const userId = userStore.userInfo?.id
    if (!userId) return
    const res = await getCart(userId)
    cartItems.value = res.data?.items || []
    
    // 等待DOM更新后，初始化多选框状态
    await nextTick()
    if (tableRef.value) {
      cartItems.value.forEach(item => {
        if (item.is_checked) {
          tableRef.value.toggleRowSelection(item, true)
        }
      })
    }
  } catch (error) {
    console.error('加载购物车失败:', error)
  }
}

const handleSelectionChange = (selection) => {
  selectedItems.value = selection
}

const handleUpdateNum = async (row) => {
  try {
    const userId = userStore.userInfo?.id
    await updateCartItem(row.item_id, userId, row.buy_num, null)
    ElMessage.success('更新成功')
  } catch (error) {
    console.error(error)
    loadCart()
  }
}

const handleSwitchChange = async (row) => {
  try {
    const userId = userStore.userInfo?.id
    await updateCartItem(row.item_id, userId, null, row.is_checked)
    
    // 同步多选框状态
    await nextTick()
    if (tableRef.value) {
      tableRef.value.toggleRowSelection(row, row.is_checked)
    }
  } catch (error) {
    console.error(error)
    // 失败时恢复原状态
    row.is_checked = !row.is_checked
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该商品吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    const userId = userStore.userInfo?.id
    await deleteCartItem(row.item_id, userId)
    ElMessage.success('删除成功')
    loadCart()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
    }
  }
}

const handleClearSelected = async () => {
  if (selectedItems.value.length === 0) {
    ElMessage.warning('请先选择商品')
    return
  }
  try {
    await ElMessageBox.confirm('确定要删除选中的商品吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    const userId = userStore.userInfo?.id
    for (const item of selectedItems.value) {
      await deleteCartItem(item.item_id, userId)
    }
    ElMessage.success('删除成功')
    loadCart()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
    }
  }
}

const handleCheckout = async () => {
  if (selectedItems.value.length === 0) {
    ElMessage.warning('请先选择商品')
    return
  }
  try {
    // 获取默认收货地址
    const addressInfo = {
      name: '默认收货人',
      phone: '13800138000',
      address: '默认收货地址'
    }
    const res = await createOrderFromCart(addressInfo)
    
    ElMessage.success('订单创建成功')
    loadCart()  // 刷新购物车
  } catch (error) {
    console.error('创建订单失败:', error)
    ElMessage.error(error.response?.data?.message || '创建订单失败')
  }
}

onMounted(() => {
  loadCart()
})
</script>

<style scoped>
.cart-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.cart-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
  padding: 20px;
  background: #f5f5f5;
}

.total-info {
  display: flex;
  gap: 20px;
}

.total-price {
  font-size: 20px;
  font-weight: bold;
  color: #f56c6c;
}
</style>
