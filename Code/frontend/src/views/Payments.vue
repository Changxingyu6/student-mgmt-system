<template>
  <div class="pay-page">
    <h2 class="page-title">{{ isAdmin ? '支付管理' : '我的支付' }}</h2>

    <el-tabs v-model="activeTab">
      <el-tab-pane label="支付记录" name="list"></el-tab-pane>
      <el-tab-pane label="发起支付" name="create"></el-tab-pane>
      <el-tab-pane v-if="!isAdmin" label="处理支付" name="process"></el-tab-pane>
    </el-tabs>

    <!-- 支付记录列表（无后端列表接口，这里仅展示操作） -->
    <div v-show="activeTab === 'list'">
      <div class="toolbar">
        <el-input v-model="queryId" placeholder="支付单ID" style="width: 400px" clearable />
        <el-button type="primary" @click="queryPay" style="margin-left: 8px">查询</el-button>
        <el-button @click="clearQuery" style="margin-left: 8px">清空</el-button>
      </div>

      <el-descriptions v-if="payDetail" :column="2" border>
        <el-descriptions-item label="支付单ID">{{ payDetail.id }}</el-descriptions-item>
        <el-descriptions-item label="订单ID">{{ payDetail.order_id }}</el-descriptions-item>
        <el-descriptions-item label="用户ID">{{ payDetail.user_id }}</el-descriptions-item>
        <el-descriptions-item label="支付金额">¥{{ payDetail.pay_amount }}</el-descriptions-item>
        <el-descriptions-item label="支付状态">
          <el-tag>{{ payDetail.pay_status }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="是否异常">{{ payDetail.is_abnormal }}</el-descriptions-item>
        <el-descriptions-item label="支付时间" :span="2">{{ formatDate(payDetail.pay_time) }}</el-descriptions-item>
      </el-descriptions>

      <el-empty v-if="!payDetail && !queryLoading" description="输入支付单ID查询" />
    </div>

    <!-- 发起支付 -->
    <div v-show="activeTab === 'create'">
      <el-form :model="createForm" label-width="100px" style="max-width: 500px">
        <el-form-item label="订单ID">
          <el-input v-model="createForm.order_id" placeholder="UUID" />
        </el-form-item>
        <el-form-item label="用户ID">
          <el-input v-model="createForm.user_id" />
        </el-form-item>
        <el-form-item label="支付金额">
          <el-input-number v-model="createForm.pay_amount" :precision="2" :min="0.01" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleCreatePay">提交</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 处理支付 -->
    <div v-show="activeTab === 'process'">
      <el-form :model="processForm" label-width="100px" style="max-width: 500px">
        <el-form-item label="支付单ID">
          <el-input v-model="processForm.pay_id" />
        </el-form-item>
        <el-form-item label="用户ID">
          <el-input v-model="processForm.user_id" />
        </el-form-item>
        <el-form-item label="支付金额">
          <el-input-number v-model="processForm.pay_amount" :precision="2" :min="0.01" />
        </el-form-item>
        <el-form-item label="支付密码">
          <el-input v-model="processForm.pay_password" type="password" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleProcessPay">确认支付</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { getPay, createPay, processPay } from '@/api/pay'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const isAdmin = computed(() => userStore.userInfo?.role === 'admin')

const activeTab = ref('list')
const formatDate = (d) => d ? new Date(d).toLocaleString('zh-CN', { hour12: false }) : '-'

// 查询
const queryId = ref('')
const queryLoading = ref(false)
const payDetail = ref(null)

const queryPay = async () => {
  if (!queryId.value) { ElMessage.warning('请输入支付单ID'); return }
  queryLoading.value = true
  try {
    payDetail.value = await getPay(queryId.value)
  } catch (e) {
    payDetail.value = null
    ElMessage.error('未找到该支付记录')
  } finally {
    queryLoading.value = false
  }
}
const clearQuery = () => { queryId.value = ''; payDetail.value = null }

// 创建
const createForm = reactive({ order_id: '', user_id: '', pay_amount: 0 })
const handleCreatePay = async () => {
  try {
    const res = await createPay(createForm)
    if (res.status === 'success') {
      ElMessage.success('提交支付记录成功')
      Object.assign(createForm, { order_id: '', user_id: '', pay_amount: 0 })
    } else {
      ElMessage.error('提交失败')
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '提交失败')
  }
}

// 处理
const processForm = reactive({ pay_id: '', user_id: '', pay_amount: 0, pay_password: '' })
const handleProcessPay = async () => {
  try {
    const res = await processPay(processForm)
    if (res.status === 'success') {
      ElMessage.success(res.message || '支付成功')
      Object.assign(processForm, { pay_id: '', user_id: '', pay_amount: 0, pay_password: '' })
    } else {
      ElMessage.error('支付失败')
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '支付失败')
  }
}
</script>

<style scoped>
.pay-page { padding: 20px; }
.page-title { margin-top: 0; margin-bottom: 20px; }
.toolbar { margin-bottom: 16px; }
</style>
