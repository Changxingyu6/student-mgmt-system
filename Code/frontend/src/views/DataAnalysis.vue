<template>
  <div class="data-analysis">
    <el-tabs v-model="activeTab" @tab-change="onTabChange">
      <!-- ============ 用户分析 ============ -->
      <el-tab-pane label="用户分析" name="user">
        <div class="toolbar">
          <el-button type="primary" :icon="Refresh" @click="loadUserData">刷新数据</el-button>
        </div>

        <el-row :gutter="20" class="stat-row">
          <el-col :span="8">
            <el-card>
              <el-statistic title="当周新增用户" :value="userData.weekly_new_users">
                <template #suffix>人</template>
              </el-statistic>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card>
              <el-statistic title="当月新增用户" :value="userData.monthly_new_users">
                <template #suffix>人</template>
              </el-statistic>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card>
              <el-statistic title="总用户" :value="userLevelData.total_users">
                <template #suffix>人</template>
              </el-statistic>
            </el-card>
          </el-col>
        </el-row>

        <el-card class="chart-card">
          <template #header>会员等级分布</template>
          <div ref="userLevelChartRef" class="chart-container"></div>
        </el-card>
      </el-tab-pane>

      <!-- ============ 商品分析 ============ -->
      <el-tab-pane label="商品分析" name="goods">
        <div class="toolbar">
          <el-button type="primary" :icon="Refresh" @click="loadGoodsData">刷新数据</el-button>
        </div>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-card>
              <template #header>销量前 20 商品</template>
              <div ref="topSellingChartRef" class="chart-container"></div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card>
              <template #header>商品分类统计</template>
              <div ref="categoryChartRef" class="chart-container"></div>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>

      <!-- ============ 订单分析 ============ -->
      <el-tab-pane label="订单分析" name="order">
        <div class="toolbar">
          <el-radio-group v-model="orderPeriod" @change="loadOrderData">
            <el-radio-button label="day">按日</el-radio-button>
            <el-radio-button label="week">按周</el-radio-button>
            <el-radio-button label="month">按月</el-radio-button>
          </el-radio-group>
          <el-button type="primary" :icon="Refresh" @click="loadOrderData">刷新数据</el-button>
        </div>

        <el-card>
          <template #header>订单趋势（{{ orderPeriodText }}）</template>
          <div ref="orderChartRef" class="chart-container-tall"></div>
        </el-card>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-card>
              <template #header>支付方式分布</template>
              <div ref="paymentChartRef" class="chart-container"></div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card>
              <template #header>订单汇总</template>
              <el-descriptions :column="1" border>
                <el-descriptions-item label="统计周期">{{ orderData.period_type }}</el-descriptions-item>
                <el-descriptions-item label="总订单数">{{ orderData.total_orders }}</el-descriptions-item>
                <el-descriptions-item label="总成交金额">¥{{ orderData.total_amount }}</el-descriptions-item>
                <el-descriptions-item label="平均退款率">{{ orderData.avg_refund_ratio }}%</el-descriptions-item>
                <el-descriptions-item label="更新时间">{{ orderData.update_time }}</el-descriptions-item>
              </el-descriptions>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>

      <!-- ============ 营销分析 ============ -->
      <el-tab-pane label="营销分析" name="marketing">
        <div class="toolbar">
          <el-button type="primary" :icon="Refresh" @click="loadMarketingData">刷新数据</el-button>
        </div>

        <el-card>
          <template #header>优惠券统计</template>
          <el-table :data="couponStats" border>
            <el-table-column prop="coupon_name" label="名称" min-width="200" />
            <el-table-column prop="type_name" label="类型" width="100" />
            <el-table-column prop="face_value" label="面值" width="100">
              <template #default="{ row }">
                <span v-if="row.type === 1">¥{{ row.face_value }}</span>
                <span v-else-if="row.type === 2">{{ row.face_value * 10 }}折</span>
                <span v-else>¥{{ row.face_value }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="min_spend" label="使用门槛" width="100">
              <template #default="{ row }">¥{{ row.min_spend }}</template>
            </el-table-column>
            <el-table-column prop="total_count" label="总发行" width="100" />
            <el-table-column prop="sent_count" label="已领取" width="100" />
            <el-table-column prop="used_count" label="已使用" width="100" />
            <el-table-column prop="remaining_count" label="剩余" width="100" />
            <el-table-column label="核销率" width="200">
              <template #default="{ row }">
                <el-progress :percentage="row.use_rate" :color="getProgressColor(row.use_rate)" />
              </template>
            </el-table-column>
          </el-table>
          <div class="summary">
            <span>共 {{ couponSummary.total_coupons }} 种优惠券，</span>
            <span>发放 {{ couponSummary.total_sent }} 张，</span>
            <span>使用 {{ couponSummary.total_used }} 张，</span>
            <span>综合核销率 <el-tag type="success">{{ couponSummary.overall_use_rate }}%</el-tag></span>
          </div>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import {
  getWeeklyNewUsers,
  getMonthlyNewUsers,
  getUserLevelStatistics,
  getTopSellingGoods,
  getCategoryStatistics,
  getLowStockGoods,
  getOrderStatistics,
  getPaymentStatistics,
  getOverdueUnpaidOrders,
  getLongTimeUnshippedOrders,
  getCouponStatistics,
  getActivityStatistics
} from '@/api/dataAnalysis'

// ========== 状态 ==========
const activeTab = ref('user')
const orderPeriod = ref('day')
const orderPeriodText = computed(() => ({ day: '按日', week: '按周', month: '按月' })[orderPeriod.value])

// 数据
const userData = reactive({ weekly_new_users: 0, monthly_new_users: 0 })
const userLevelData = reactive({ level_statistics: [], total_users: 0 })
const topSellingList = ref([])
const categoryList = ref([])
const lowStockList = ref([])
const orderData = reactive({ period_type: '', order_statistics: [], total_orders: 0, total_amount: 0, avg_refund_ratio: 0, update_time: '' })
const paymentList = ref([])
const overdueList = ref([])
const unshippedList = ref([])
const couponStats = ref([])
const couponSummary = reactive({ total_coupons: 0, total_sent: 0, total_used: 0, overall_use_rate: 0 })
const activityStats = ref([])
const activitySummary = reactive({ total_activities: 0, ongoing_count: 0, upcoming_count: 0, ended_count: 0 })

// ECharts 实例
let userLevelChart = null
let topSellingChart = null
let categoryChart = null
let orderChart = null
let paymentChart = null
const userLevelChartRef = ref(null)
const topSellingChartRef = ref(null)
const categoryChartRef = ref(null)
const orderChartRef = ref(null)
const paymentChartRef = ref(null)

// ========== 加载方法 ==========
const loadUserData = async () => {
  try {
    const [weekly, monthly, level] = await Promise.all([
      getWeeklyNewUsers(),
      getMonthlyNewUsers(),
      getUserLevelStatistics()
    ])
    userData.weekly_new_users = weekly?.data?.weekly_new_users ?? 0
    userData.monthly_new_users = monthly?.data?.monthly_new_users ?? 0
    const lvl = level?.data || {}
    userLevelData.level_statistics = lvl.level_statistics || []
    userLevelData.total_users = lvl.total_users ?? 0
    await nextTick()
    renderUserLevelChart()
  } catch (e) {
    console.error('加载用户数据失败', e)
  }
}

const loadGoodsData = async () => {
  try {
    const [top, cat, low] = await Promise.all([
      getTopSellingGoods(20),
      getCategoryStatistics(),
      getLowStockGoods()
    ])
    topSellingList.value = top?.data?.top_selling_goods || []
    categoryList.value = cat?.data?.category_statistics || []
    lowStockList.value = low?.data?.low_stock_goods || []
    await nextTick()
    renderTopSellingChart()
    renderCategoryChart()
  } catch (e) {
    console.error('加载商品数据失败', e)
  }
}

const loadOrderData = async () => {
  try {
    const [ord, pay, overdue, unshipped] = await Promise.all([
      getOrderStatistics(orderPeriod.value),
      getPaymentStatistics(),
      getOverdueUnpaidOrders(24),
      getLongTimeUnshippedOrders(48)
    ])
    const o = ord?.data || {}
    orderData.period_type = o.period_type || ''
    orderData.order_statistics = o.order_statistics || []
    orderData.total_orders = o.total_orders ?? 0
    orderData.total_amount = o.total_amount ?? 0
    orderData.avg_refund_ratio = o.avg_refund_ratio ?? 0
    orderData.update_time = o.update_time || ''
    paymentList.value = pay?.data?.payment_statistics || []
    overdueList.value = overdue?.data?.overdue_orders || []
    unshippedList.value = unshipped?.data?.unshipped_orders || []
    await nextTick()
    renderOrderChart()
    renderPaymentChart()
  } catch (e) {
    console.error('加载订单数据失败', e)
  }
}

const loadMarketingData = async () => {
  try {
    const [coupon, activity] = await Promise.all([
      getCouponStatistics(),
      getActivityStatistics()
    ])
    couponStats.value = coupon?.data?.coupon_statistics || []
    couponSummary.total_coupons = coupon?.data?.total_coupons ?? 0
    couponSummary.total_sent = coupon?.data?.total_sent ?? 0
    couponSummary.total_used = coupon?.data?.total_used ?? 0
    couponSummary.overall_use_rate = coupon?.data?.overall_use_rate ?? 0
    activityStats.value = activity?.data?.activity_statistics || []
    activitySummary.total_activities = activity?.data?.total_activities ?? 0
    activitySummary.ongoing_count = activity?.data?.ongoing_count ?? 0
    activitySummary.upcoming_count = activity?.data?.upcoming_count ?? 0
    activitySummary.ended_count = activity?.data?.ended_count ?? 0
  } catch (e) {
    console.error('加载营销数据失败', e)
  }
}

const onTabChange = (name) => {
  if (name === 'user') loadUserData()
  else if (name === 'goods') loadGoodsData()
  else if (name === 'order') loadOrderData()
  else if (name === 'marketing') loadMarketingData()
}

// ========== 图表渲染 ==========
const renderUserLevelChart = () => {
  if (!userLevelChartRef.value) return
  if (!userLevelChart) userLevelChart = echarts.init(userLevelChartRef.value)
  const data = (userLevelData.level_statistics || []).map(i => ({ name: i.level, value: i.count }))
  userLevelChart.setOption({
    tooltip: { trigger: 'item' },
    legend: { bottom: 0 },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data,
      label: { formatter: '{b}\n{c}人 ({d}%)' }
    }]
  })
}

const renderTopSellingChart = () => {
  if (!topSellingChartRef.value) return
  if (!topSellingChart) topSellingChart = echarts.init(topSellingChartRef.value)
  const sorted = [...topSellingList.value].slice(0, 20).reverse()
  const names = sorted.map(i => i.goods_name)
  const values = sorted.map(i => i.sales_volume)
  topSellingChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: 100, right: 30, top: 30, bottom: 30 },
    xAxis: { type: 'value' },
    yAxis: { type: 'category', data: names, axisLabel: { width: 90, overflow: 'truncate' } },
    series: [{
      type: 'bar',
      data: values,
      itemStyle: { color: '#409eff' },
      label: { show: true, position: 'right' }
    }]
  })
}

const renderCategoryChart = () => {
  if (!categoryChartRef.value) return
  if (!categoryChart) categoryChart = echarts.init(categoryChartRef.value)
  const data = categoryList.value.map(i => ({ name: i.category_name, value: i.goods_count }))
  categoryChart.setOption({
    tooltip: { trigger: 'item' },
    legend: { bottom: 0, type: 'scroll' },
    series: [{
      type: 'pie',
      radius: '60%',
      data,
      label: { formatter: '{b}\n{c}件' }
    }]
  })
}

const renderOrderChart = () => {
  if (!orderChartRef.value) return
  if (!orderChart) orderChart = echarts.init(orderChartRef.value)
  const list = orderData.order_statistics || []
  // 后端 ORDER BY period DESC，需要反转才能按时间正序显示
  const data = [...list].reverse()
  const periods = data.map(i => i.period)
  const totalOrders = data.map(i => i.total_orders)
  const totalAmount = data.map(i => i.total_amount)
  orderChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['订单数', '成交金额'] },
    grid: { left: 60, right: 60, top: 50, bottom: 40 },
    xAxis: { type: 'category', data: periods },
    yAxis: [
      { type: 'value', name: '订单数' },
      { type: 'value', name: '金额(元)' }
    ],
    series: [
      { name: '订单数', type: 'line', data: totalOrders, smooth: true, itemStyle: { color: '#409eff' } },
      { name: '成交金额', type: 'line', yAxisIndex: 1, data: totalAmount, smooth: true, itemStyle: { color: '#67c23a' } }
    ]
  })
}

const renderPaymentChart = () => {
  if (!paymentChartRef.value) return
  if (!paymentChart) paymentChart = echarts.init(paymentChartRef.value)
  const data = paymentList.value.map(i => ({ name: i.payment_method, value: i.total_amount }))
  paymentChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}<br/>¥{c} ({d}%)' },
    legend: { bottom: 0 },
    series: [{
      type: 'pie',
      radius: ['30%', '70%'],
      roseType: 'area',
      data,
      label: { formatter: '{b}\n¥{c}' }
    }]
  })
}

// 窗口缩放
const handleResize = () => {
  userLevelChart?.resize()
  topSellingChart?.resize()
  categoryChart?.resize()
  orderChart?.resize()
  paymentChart?.resize()
}

// ========== 辅助 ==========
const getProgressColor = (rate) => {
  if (rate >= 50) return '#67c23a'
  if (rate >= 20) return '#e6a23c'
  return '#f56c6c'
}

const getActivityTagType = (status) => {
  if (status === '进行中') return 'success'
  if (status === '未开始') return 'info'
  if (status === '已结束') return 'warning'
  return ''
}

// ========== 生命周期 ==========
onMounted(() => {
  loadUserData()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  userLevelChart?.dispose()
  topSellingChart?.dispose()
  categoryChart?.dispose()
  orderChart?.dispose()
  paymentChart?.dispose()
})
</script>

<style scoped>
.data-analysis {
  padding: 20px;
}
.toolbar {
  margin-bottom: 16px;
  display: flex;
  gap: 12px;
  align-items: center;
}
.stat-row {
  margin-bottom: 16px;
}
.chart-card,
.table-card {
  margin-top: 16px;
}
.chart-container {
  width: 100%;
  height: 360px;
}
.chart-container-tall {
  width: 100%;
  height: 420px;
}
.summary {
  margin-top: 12px;
  padding: 8px 12px;
  color: #606266;
  font-size: 14px;
  display: flex;
  gap: 12px;
  align-items: center;
}
</style>
