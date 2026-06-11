<template>
  <div class="pay-page">
    <h2 class="page-title">{{ isAdmin ? '支付管理' : '我的支付' }}</h2>

    <el-tabs v-model="activeTab">
      <el-tab-pane label="支付记录" name="list"></el-tab-pane>
      <el-tab-pane v-if="!isAdmin" label="处理支付" name="process"></el-tab-pane>
    </el-tabs>

    <!-- 支付记录列表 -->
    <div v-show="activeTab === 'list'">
      <div class="toolbar">
        <el-select v-model="filters.pay_status" placeholder="支付状态" style="width: 150px" clearable>
          <el-option label="待支付" value="待支付" />
          <el-option label="支付成功" value="支付成功" />
          <el-option label="支付失败" value="支付失败" />
          <el-option label="已关闭" value="已关闭" />
        </el-select>
        <el-date-picker v-model="filters.start_time" type="date" placeholder="开始时间" style="width: 150px" />
        <el-date-picker v-model="filters.end_time" type="date" placeholder="结束时间" style="width: 150px" />
        <el-button type="primary" @click="queryPay" style="margin-left: 8px">查询</el-button>
        <el-button @click="clearQuery" style="margin-left: 8px">清空</el-button>
        <el-button type="success" @click="loadUserPays" style="margin-left: 8px">刷新列表</el-button>
      </div>

      <!-- 支付列表表格 -->
      <el-table v-if="payList.length > 0" :data="payList" border style="width: 100%">
        <el-table-column prop="pay_amount" label="支付金额" width="120">
          <template #default="scope">¥{{ scope.row.pay_amount }}</template>
        </el-table-column>
        <el-table-column prop="pay_status" label="支付状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.pay_status)">{{ scope.row.pay_status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="pay_method" label="支付方式" width="100" />
        <el-table-column prop="create_time" label="创建时间" width="150">
          <template #default="scope">{{ formatDate(scope.row.create_time) }}</template>
        </el-table-column>
        <el-table-column prop="expire_time" label="过期时间" width="150">
          <template #default="scope">{{ formatDate(scope.row.expire_time) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="scope">
            <el-button 
              v-if="scope.row.pay_status === '待支付'" 
              size="small" 
              type="primary" 
              @click="handlePay(scope.row)"
            >立即支付</el-button>
            <span v-else>-</span>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="payList.length === 0 && !loading" description="暂无支付记录" />
      <el-loading v-if="loading" />
    </div>

    <!-- 处理支付 -->
    <div v-show="activeTab === 'process'">
      <el-form :model="processForm" label-width="120px" style="max-width: 600px">
        <el-form-item label="支付单ID" required>
          <el-input v-model="processForm.pay_id" placeholder="请从支付记录中选择" :disabled="true" />
        </el-form-item>
        <el-form-item label="用户ID" required>
          <el-input v-model="processForm.user_id" :disabled="true" />
        </el-form-item>
        <el-form-item label="支付金额" required>
          <el-input-number v-model="processForm.pay_amount" :precision="2" :min="0.01" :disabled="true" />
        </el-form-item>
        <el-form-item label="可用优惠券">
          <el-select v-model="processForm.coupon_id" placeholder="请选择优惠券（可选）">
            <el-option label="不使用优惠券" value="" />
            <el-option 
              v-for="coupon in availableCoupons" 
              :key="coupon.id" 
              :label="`${coupon.coupons_name}（满${coupon.min_spend}减${coupon.face_value}）`" 
              :value="coupon.id" 
              :disabled="processForm.pay_amount < coupon.min_spend"
            />
          </el-select>
          <div v-if="selectedCoupon" style="margin-top: 8px; color: #67c23a;">
            使用优惠券后应付: ¥{{ finalPayAmount.toFixed(2) }}
          </div>
        </el-form-item>
        <el-form-item label="支付密码" required>
          <el-input v-model="processForm.pay_password" type="password" show-password placeholder="请输入支付密码" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleProcessPay" :loading="processing">确认支付</el-button>
          <el-button @click="resetProcessForm" style="margin-left: 8px">重置</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getPay, processPay, getUserPays } from '@/api/pay'
import { getUserCoupons } from '@/api/coupon'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const isAdmin = computed(() => userStore.userInfo?.role === 'admin')

const activeTab = ref('list')
const formatDate = (d) => d ? new Date(d).toLocaleString('zh-CN', { hour12: false }) : '-'

// 获取状态标签类型
const getStatusType = (status) => {
  const types = {
    '待支付': 'warning',
    '支付成功': 'success',
    '支付失败': 'danger',
    '已关闭': 'info'
  }
  return types[status] || 'default'
}

// 查询筛选条件
const filters = reactive({
  order_no: '',
  pay_status: '',
  pay_method: '',
  start_time: '',
  end_time: ''
})

// 用户支付列表
const loading = ref(false)
const payList = ref([])

const queryPay = async () => {
  loading.value = true
  try {
    const res = await getUserPays(userStore.userInfo.id, filters)
    if (res.data) {
      payList.value = res.data
    }
  } catch (e) {
    ElMessage.error('查询支付记录失败')
  } finally {
    loading.value = false
  }
}

const clearQuery = () => {
  Object.assign(filters, {
    order_no: '',
    pay_status: '',
    pay_method: '',
    start_time: '',
    end_time: ''
  })
  loadUserPays()
}

const loadUserPays = async () => {
  if (!userStore.userInfo?.id) {
    ElMessage.warning('请先登录')
    return
  }
  loading.value = true
  try {
    const res = await getUserPays(userStore.userInfo.id)
    if (res.data) {
      payList.value = res.data
    }
  } catch (e) {
    ElMessage.error('获取支付记录失败')
  } finally {
    loading.value = false
  }
}

// 页面加载时获取列表
onMounted(() => {
  loadUserPays()
})

// 用户优惠券列表
const availableCoupons = ref([])

const loadUserCoupons = async () => {
  if (!userStore.userInfo?.id) return
  try {
    const res = await getUserCoupons(userStore.userInfo.id)
    if (res.data && res.data.items) {
      // 只显示已领取（未使用）的优惠券，状态码为1
      availableCoupons.value = res.data.items.filter(c => c.status === 1)
    }
  } catch (e) {
    console.error('获取优惠券失败', e)
  }
}

// 立即支付
const handlePay = (payItem) => {
  activeTab.value = 'process'
  processForm.pay_id = payItem.pay_id
  processForm.user_id = payItem.user_id
  processForm.pay_amount = payItem.pay_amount
  // 加载可用优惠券
  loadUserCoupons()
}

// 处理支付
const processing = ref(false)
const processForm = reactive({ pay_id: '', user_id: '', pay_amount: 0, pay_password: '', coupon_id: '' })

// 选中的优惠券
const selectedCoupon = computed(() => {
  if (!processForm.coupon_id) return null
  return availableCoupons.value.find(c => c.id === processForm.coupon_id)
})

// 最终支付金额
const finalPayAmount = computed(() => {
  let amount = processForm.pay_amount || 0
  if (selectedCoupon.value) {
    amount -= selectedCoupon.value.face_value || 0
  }
  return Math.max(0, amount)
})

const handleProcessPay = async () => {
  if (!processForm.pay_password) {
    ElMessage.warning('请输入支付密码')
    return
  }
  processing.value = true
  try {
    const res = await processPay(processForm)
    if (res.code === 200) {
      ElMessage.success(res.message || '支付成功')
      resetProcessForm()
      loadUserPays() // 刷新支付列表
      activeTab.value = 'list'
    } else {
      ElMessage.error(res.message || '支付失败')
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || e.response?.data?.message || '支付失败')
  } finally {
    processing.value = false
  }
}

const resetProcessForm = () => {
  Object.assign(processForm, { pay_id: '', user_id: '', pay_amount: 0, pay_password: '', coupon_id: '' })
  availableCoupons.value = []
}
</script>

<style scoped>
.pay-page { padding: 20px; }
.page-title { margin-top: 0; margin-bottom: 20px; }
.toolbar { margin-bottom: 16px; }
</style>
