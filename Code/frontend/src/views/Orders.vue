<template>
  <div class="orders-page">
    <h2 class="page-title">{{ isAdmin ? '订单管理' : '我的订单' }}</h2>

    <!-- 筛选栏 -->
    <div class="toolbar" style="margin-bottom: 16px;">
      <el-select v-model="filters.order_status" placeholder="订单状态" style="width: 120px" clearable>
        <el-option label="待支付" value="pending" />
        <el-option label="已支付" value="paid" />
        <el-option label="已发货" value="shipped" />
        <el-option label="已完成" value="completed" />
        <el-option label="已取消" value="cancelled" />
      </el-select>
      <el-select v-model="filters.pay_status" placeholder="支付状态" style="width: 120px" clearable>
        <el-option label="待支付" value="unpaid" />
        <el-option label="已支付" value="paid" />
        <el-option label="已退款" value="refunded" />
      </el-select>
      <el-select v-model="filters.logistics_status" placeholder="物流状态" style="width: 120px" clearable>
        <el-option label="待发货" value="waiting_ship" />
        <el-option label="已发货" value="shipped" />
        <el-option label="运输中" value="in_transit" />
        <el-option label="派送中" value="delivering" />
        <el-option label="已签收" value="delivered" />
      </el-select>
      <el-date-picker v-model="filters.start_time" type="date" placeholder="开始时间" style="width: 150px" />
      <el-date-picker v-model="filters.end_time" type="date" placeholder="结束时间" style="width: 150px" />
      <el-button type="primary" @click="queryOrders" style="margin-left: 8px">查询</el-button>
      <el-button @click="clearFilters" style="margin-left: 8px">清空</el-button>
      <el-button type="success" @click="loadOrders" style="margin-left: 8px">刷新列表</el-button>
    </div>

    <!-- 订单列表 -->
    <div>
      <el-table v-if="orderList.length > 0" :data="orderList" border style="width: 100%">
        <el-table-column prop="order_id" label="订单编号" width="200" show-overflow-tooltip />
        <el-table-column prop="total_amount" label="订单金额" width="120">
          <template #default="scope">¥{{ scope.row.total_amount }}</template>
        </el-table-column>
        <el-table-column prop="order_status" label="订单状态" width="100">
          <template #default="scope">
            <el-tag :type="getOrderStatusType(scope.row.order_status)">{{ getOrderStatusText(scope.row.order_status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="pay_status" label="支付状态" width="100">
          <template #default="scope">
            <el-tag :type="getPayStatusType(scope.row.pay_status)">{{ getPayStatusText(scope.row.pay_status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="logistics_status" label="物流状态" width="100">
          <template #default="scope">
            <el-tag :type="getLogisticsStatusType(scope.row.logistics_status)">{{ getLogisticsStatusText(scope.row.logistics_status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="160" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="scope">
            <el-button type="primary" size="small" @click="viewOrder(scope.row)">详细</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="orderList.length === 0 && !loading" description="暂无订单记录" />
      <el-loading v-if="loading" />
    </div>

    <!-- 订单详情弹窗 -->
    <el-dialog title="订单详情" v-model="showDetail" width="800px">
      <div v-if="currentOrder">
        <!-- 订单基本信息 -->
        <el-descriptions :column="2" border>
          <el-descriptions-item label="订单编号">{{ currentOrder.order_id }}</el-descriptions-item>
          <el-descriptions-item label="订单金额">¥{{ currentOrder.total_amount }}</el-descriptions-item>
          <el-descriptions-item label="订单状态">
            <el-tag :type="getOrderStatusType(currentOrder.order_status)">{{ getOrderStatusText(currentOrder.order_status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="支付状态">
            <el-tag :type="getPayStatusType(currentOrder.pay_status)">{{ getPayStatusText(currentOrder.pay_status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="物流状态">
            <el-tag :type="getLogisticsStatusType(currentOrder.logistics_status)">{{ getLogisticsStatusText(currentOrder.logistics_status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="支付方式">{{ currentOrder.payment_method || '余额' }}</el-descriptions-item>
          <el-descriptions-item label="收货人">{{ currentOrder.receiver_name }}</el-descriptions-item>
          <el-descriptions-item label="联系电话">{{ currentOrder.receiver_phone }}</el-descriptions-item>
          <el-descriptions-item label="收货地址" :span="2">{{ currentOrder.shipping_address }}</el-descriptions-item>
          <el-descriptions-item label="创建时间" :span="2">{{ currentOrder.create_time }}</el-descriptions-item>
        </el-descriptions>

        <!-- 商品明细表格 -->
        <el-divider>商品明细</el-divider>
        <el-table :data="orderItems" border style="margin-top: 16px;">
          <el-table-column prop="product_name" label="商品名称" />
          <el-table-column prop="spec_info" label="规格" />
          <el-table-column label="单价" width="100">
            <template #default="scope">¥{{ scope.row.price }}</template>
          </el-table-column>
          <el-table-column prop="quantity" label="数量" width="80" />
          <el-table-column label="小计" width="100">
            <template #default="scope">¥{{ (scope.row.price * scope.row.quantity).toFixed(2) }}</template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getUserOrders, getOrderItems } from './../api/order'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const isAdmin = computed(() => userStore.userInfo?.role === 'admin')

const loading = ref(false)
const orderList = ref([])
const showDetail = ref(false)
const currentOrder = ref(null)
const orderItems = ref([])

// 筛选条件
const filters = reactive({
  order_id: '',
  order_status: '',
  pay_status: '',
  logistics_status: '',
  start_time: '',
  end_time: ''
})

const getOrderStatusType = (status) => {
  const types = {
    'pending': 'warning',
    'paid': 'success',
    'shipped': 'primary',
    'completed': 'success',
    'cancelled': 'danger'
  }
  return types[status] || 'default'
}

const getOrderStatusText = (status) => {
  const texts = {
    'pending': '待支付',
    'paid': '已支付',
    'shipped': '已发货',
    'completed': '已完成',
    'cancelled': '已取消'
  }
  return texts[status] || status
}

const getPayStatusType = (status) => {
  const types = {
    'unpaid': 'warning',
    'paid': 'success',
    'refunded': 'danger'
  }
  return types[status] || 'default'
}

const getPayStatusText = (status) => {
  const texts = {
    'unpaid': '待支付',
    'paid': '已支付',
    'refunded': '已退款'
  }
  return texts[status] || status
}

const getLogisticsStatusType = (status) => {
  const types = {
    'waiting_ship': 'warning',
    'shipped': 'primary',
    'in_transit': 'info',
    'delivering': 'info',
    'delivered': 'success'
  }
  return types[status] || 'default'
}

const getLogisticsStatusText = (status) => {
  const texts = {
    'waiting_ship': '待发货',
    'shipped': '已发货',
    'in_transit': '运输中',
    'delivering': '派送中',
    'delivered': '已签收'
  }
  return texts[status] || status
}

const loadOrders = async () => {
  if (!userStore.userInfo?.id) {
    ElMessage.warning('请先登录')
    return
  }
  loading.value = true
  try {
    const res = await getUserOrders(userStore.userInfo.id)
    if (res.code === 200) {
      orderList.value = res.data
    }
  } catch (e) {
    ElMessage.error('获取订单列表失败')
  } finally {
    loading.value = false
  }
}

const queryOrders = async () => {
  if (!userStore.userInfo?.id) {
    ElMessage.warning('请先登录')
    return
  }
  loading.value = true
  try {
    const res = await getUserOrders(userStore.userInfo.id, filters)
    if (res.code === 200) {
      orderList.value = res.data
    }
  } catch (e) {
    ElMessage.error('查询订单失败')
  } finally {
    loading.value = false
  }
}

const clearFilters = () => {
  Object.assign(filters, {
    order_id: '',
    order_status: '',
    pay_status: '',
    logistics_status: '',
    start_time: '',
    end_time: ''
  })
  loadOrders()
}

const viewOrder = async (order) => {
  currentOrder.value = order
  orderItems.value = []
  showDetail.value = true
  
  // 加载订单明细
  try {
    const res = await getOrderItems(order.order_id)
    if (res.code === 200) {
      orderItems.value = res.data
    }
  } catch (e) {
    ElMessage.error('获取订单明细失败')
  }
}

onMounted(() => {
  loadOrders()
})
</script>

<style scoped>
.orders-page { padding: 20px; }
.page-title { margin-top: 0; margin-bottom: 20px; }
</style>
