<template>
  <div class="refund-page">
    <h2 class="page-title">{{ isAdmin ? '退款管理' : '我的退款' }}</h2>

    <el-tabs v-model="activeTab">
      <el-tab-pane label="退款记录查询" name="query"></el-tab-pane>
      <el-tab-pane v-if="!isAdmin" label="提交退款申请" name="create"></el-tab-pane>
      <el-tab-pane v-if="isAdmin" label="更新退款状态" name="update"></el-tab-pane>
    </el-tabs>

    <!-- 查询 -->
    <div v-show="activeTab === 'query'">
      <div class="toolbar">
        <el-input v-model="refundId" placeholder="退款单ID" style="width: 400px" clearable />
        <el-button type="primary" @click="queryRefund" style="margin-left: 8px">查询</el-button>
      </div>

      <el-descriptions v-if="refundDetail" :column="2" border>
        <el-descriptions-item label="退款单ID">{{ refundDetail.id }}</el-descriptions-item>
        <el-descriptions-item label="订单ID">{{ refundDetail.order_id }}</el-descriptions-item>
        <el-descriptions-item label="用户ID">{{ refundDetail.user_id }}</el-descriptions-item>
        <el-descriptions-item label="售后单ID">{{ refundDetail.after_sales_id }}</el-descriptions-item>
        <el-descriptions-item label="退款金额">¥{{ refundDetail.refund_amount }}</el-descriptions-item>
        <el-descriptions-item label="退款状态">
          <el-tag>{{ refundDetail.refund_status }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="退款时间" :span="2">{{ formatDate(refundDetail.refund_time) }}</el-descriptions-item>
      </el-descriptions>
    </div>

    <!-- 创建 -->
    <div v-show="activeTab === 'create'">
      <el-form :model="createForm" label-width="100px" style="max-width: 500px">
        <el-form-item label="售后单ID">
          <el-input v-model="createForm.after_sales_id" />
        </el-form-item>
        <el-form-item label="订单ID">
          <el-input v-model="createForm.order_id" />
        </el-form-item>
        <el-form-item label="用户ID">
          <el-input v-model="createForm.user_id" :placeholder="userStore.userInfo?.id || '请输入用户ID'" />
        </el-form-item>
        <el-form-item label="退款金额">
          <el-input-number v-model="createForm.refund_amount" :precision="2" :min="0.01" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleCreateRefund">提交申请</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 更新 -->
    <div v-show="activeTab === 'update'">
      <el-form :model="updateForm" label-width="100px" style="max-width: 500px">
        <el-form-item label="退款单ID">
          <el-input v-model="updateForm.refund_id" />
        </el-form-item>
        <el-form-item label="退款状态">
          <el-select v-model="updateForm.refund_status" style="width: 100%">
            <el-option label="待退款" value="pending_refund" />
            <el-option label="退款中" value="refunding" />
            <el-option label="退款成功" value="refund_success" />
            <el-option label="退款失败" value="refund_failed" />
          </el-select>
        </el-form-item>
        <el-form-item label="退款时间">
          <el-date-picker v-model="updateForm.refund_time" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" style="width: 100%" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleUpdateRefund">更新</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { getRefund, createRefund, updateRefund } from '@/api/refund'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const isAdmin = computed(() => userStore.userInfo?.role === 'admin')

const activeTab = ref('query')
const formatDate = (d) => d ? new Date(d).toLocaleString('zh-CN', { hour12: false }) : '-'

// 查询
const refundId = ref('')
const refundDetail = ref(null)
const queryRefund = async () => {
  if (!refundId.value) { ElMessage.warning('请输入退款单ID'); return }
  try {
    refundDetail.value = await getRefund(refundId.value)
  } catch (e) {
    refundDetail.value = null
    ElMessage.error('未找到该退款记录')
  }
}

// 创建
const createForm = reactive({ after_sales_id: '', order_id: '', user_id: '', refund_amount: 0 })
const handleCreateRefund = async () => {
  // 普通用户自动填自己 ID
  if (!isAdmin.value && !createForm.user_id) {
    createForm.user_id = userStore.userInfo?.id || ''
  }
  try {
    const res = await createRefund(createForm)
    if (res.status === 'success') {
      ElMessage.success('提交退款申请成功')
      Object.assign(createForm, { after_sales_id: '', order_id: '', user_id: '', refund_amount: 0 })
    } else {
      ElMessage.error(res.refund_status || '提交失败')
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '提交失败')
  }
}

// 更新
const updateForm = reactive({ refund_id: '', refund_status: 'pending_refund', refund_time: '' })
const handleUpdateRefund = async () => {
  try {
    const res = await updateRefund(updateForm)
    if (res.status === 'success') {
      ElMessage.success('退款状态更新成功')
    } else {
      ElMessage.error('更新失败')
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '更新失败')
  }
}
</script>

<style scoped>
.refund-page { padding: 20px; }
.page-title { margin-top: 0; margin-bottom: 20px; }
.toolbar { margin-bottom: 16px; }
</style>
