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
        <el-input v-model="queryId" placeholder="支付单ID" style="width: 400px" clearable />
        <el-button type="primary" @click="queryPay" style="margin-left: 8px">查询</el-button>
        <el-button @click="clearQuery" style="margin-left: 8px">清空</el-button>
        <el-button type="success" @click="loadUserPays" style="margin-left: 8px">刷新列表</el-button>
      </div>

      <!-- 支付列表表格 -->
      <el-table v-if="payList.length > 0" :data="payList" border style="width: 100%">
        <el-table-column prop="pay_id" label="支付单ID" show-overflow-tooltip />
        <el-table-column prop="order_id" label="订单ID" show-overflow-tooltip />
        <el-table-column prop="pay_amount" label="支付金额">
          <template #default="scope">¥{{ scope.row.pay_amount }}</template>
        </el-table-column>
        <el-table-column prop="pay_status" label="支付状态">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.pay_status)">{{ scope.row.pay_status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="pay_method" label="支付方式" />
        <el-table-column prop="create_time" label="创建时间">
          <template #default="scope">{{ formatDate(scope.row.create_time) }}</template>
        </el-table-column>
        <el-table-column prop="expire_time" label="过期时间">
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
          <el-input v-model="processForm.pay_id" placeholder="请输入支付单ID" />
        </el-form-item>
        <el-form-item label="用户ID" required>
          <el-input v-model="processForm.user_id" :disabled="true" />
        </el-form-item>
        <el-form-item label="支付金额" required>
          <el-input-number v-model="processForm.pay_amount" :precision="2" :min="0.01" :disabled="true" />
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

// 查询
const queryId = ref('')
const payDetail = ref(null)

const queryPay = async () => {
  if (!queryId.value) { ElMessage.warning('请输入支付单ID'); return }
  try {
    payDetail.value = await getPay(queryId.value)
  } catch (e) {
    payDetail.value = null
    ElMessage.error('未找到该支付记录')
  }
}
const clearQuery = () => { queryId.value = ''; payDetail.value = null }

// 用户支付列表
const loading = ref(false)
const payList = ref([])

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

// 立即支付
const handlePay = (payItem) => {
  activeTab.value = 'process'
  processForm.pay_id = payItem.pay_id
  processForm.user_id = payItem.user_id
  processForm.pay_amount = payItem.pay_amount
}

// 处理支付
const processing = ref(false)
const processForm = reactive({ pay_id: '', user_id: '', pay_amount: 0, pay_password: '' })

const handleProcessPay = async () => {
  if (!processForm.pay_password) {
    ElMessage.warning('请输入支付密码')
    return
  }
  processing.value = true
  try {
    const res = await processPay(processForm)
    if (res.status === 'success') {
      ElMessage.success(res.message || '支付成功')
      resetProcessForm()
      loadUserPays() // 刷新支付列表
      activeTab.value = 'list'
    } else {
      ElMessage.error('支付失败')
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || e.response?.data?.message || '支付失败')
  } finally {
    processing.value = false
  }
}

const resetProcessForm = () => {
  Object.assign(processForm, { pay_id: '', user_id: '', pay_amount: 0, pay_password: '' })
}
</script>

<style scoped>
.pay-page { padding: 20px; }
.page-title { margin-top: 0; margin-bottom: 20px; }
.toolbar { margin-bottom: 16px; }
</style>
