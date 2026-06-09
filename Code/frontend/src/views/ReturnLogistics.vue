<template>
  <div class="return-page">
    <h2 class="page-title">{{ isAdmin ? '退货物流管理' : '我的退货物流' }}</h2>

    <el-tabs v-model="activeTab">
      <el-tab-pane label="退货物流查询" name="query"></el-tab-pane>
      <el-tab-pane v-if="isAdmin" label="创建退货物流" name="create"></el-tab-pane>
      <el-tab-pane v-if="isAdmin" label="更新退货物流" name="update"></el-tab-pane>
    </el-tabs>

    <!-- 查询 -->
    <div v-show="activeTab === 'query'">
      <el-radio-group v-model="queryType" style="margin-bottom: 16px">
        <el-radio-button value="id">按退货物流ID</el-radio-button>
        <el-radio-button value="after">按售后单ID</el-radio-button>
      </el-radio-group>

      <div class="toolbar">
        <el-input v-model="queryId" :placeholder="queryType === 'id' ? '退货物流单ID' : '售后单ID'" style="width: 400px" clearable />
        <el-button type="primary" @click="queryReturn" style="margin-left: 8px">查询</el-button>
      </div>

      <el-descriptions v-if="detail" :column="2" border>
        <el-descriptions-item label="退货物流ID">{{ detail.id || '-' }}</el-descriptions-item>
        <el-descriptions-item label="售后单ID">{{ detail.after_sales_id }}</el-descriptions-item>
        <el-descriptions-item label="订单ID">{{ detail.order_id }}</el-descriptions-item>
        <el-descriptions-item label="状态" :span="2">
          <el-tag>{{ detail.return_logistics_status || detail.status }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="退货轨迹" :span="2">{{ detail.return_track_info || '-' }}</el-descriptions-item>
      </el-descriptions>
    </div>

    <!-- 创建 -->
    <div v-show="activeTab === 'create'">
      <el-form :model="createForm" label-width="120px" style="max-width: 500px">
        <el-form-item label="售后单ID">
          <el-input v-model="createForm.after_sales_id" />
        </el-form-item>
        <el-form-item label="订单ID">
          <el-input v-model="createForm.order_id" />
        </el-form-item>
        <el-form-item label="退货物流状态">
          <el-select v-model="createForm.return_logistics_status" style="width: 100%">
            <el-option label="待发货" value="to_be_shipped" />
            <el-option label="已揽收" value="collected" />
            <el-option label="运输中" value="in_transit" />
            <el-option label="派送中" value="out_for_delivery" />
            <el-option label="已签收" value="signed" />
            <el-option label="异常" value="abnormal" />
          </el-select>
        </el-form-item>
        <el-form-item label="退货轨迹">
          <el-input v-model="createForm.return_track_info" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleCreate">创建</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 更新 -->
    <div v-show="activeTab === 'update'">
      <el-form :model="updateForm" label-width="120px" style="max-width: 500px">
        <el-form-item label="退货物流单ID">
          <el-input v-model="updateForm.return_logistics_id" />
        </el-form-item>
        <el-form-item label="退货物流状态">
          <el-select v-model="updateForm.return_logistics_status" style="width: 100%">
            <el-option label="待发货" value="to_be_shipped" />
            <el-option label="已揽收" value="collected" />
            <el-option label="运输中" value="in_transit" />
            <el-option label="派送中" value="out_for_delivery" />
            <el-option label="已签收" value="signed" />
            <el-option label="异常" value="abnormal" />
          </el-select>
        </el-form-item>
        <el-form-item label="退货轨迹">
          <el-input v-model="updateForm.return_track_info" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleUpdate">更新</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { getReturnLogistics, getReturnLogisticsByAfterSales, createReturnLogistics, updateReturnLogistics } from '@/api/returnLogistics'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const isAdmin = computed(() => userStore.userInfo?.role === 'admin')

const activeTab = ref('query')
const queryType = ref('id')
const queryId = ref('')
const detail = ref(null)

const queryReturn = async () => {
  if (!queryId.value) { ElMessage.warning('请输入ID'); return }
  try {
    detail.value = queryType.value === 'id'
      ? await getReturnLogistics(queryId.value)
      : await getReturnLogisticsByAfterSales(queryId.value)
  } catch (e) {
    detail.value = null
    ElMessage.error('未找到该退货物流记录')
  }
}

const createForm = reactive({
  after_sales_id: '', order_id: '',
  return_logistics_status: 'to_be_shipped', return_track_info: ''
})
const handleCreate = async () => {
  try {
    const res = await createReturnLogistics(createForm)
    if (res.status === 'success') {
      ElMessage.success('创建退货物流记录成功')
      Object.assign(createForm, { after_sales_id: '', order_id: '', return_logistics_status: 'to_be_shipped', return_track_info: '' })
    } else {
      ElMessage.error(res.return_logistics_status || '创建失败')
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '创建失败')
  }
}

const updateForm = reactive({ return_logistics_id: '', return_logistics_status: 'in_transit', return_track_info: '' })
const handleUpdate = async () => {
  try {
    const res = await updateReturnLogistics(updateForm)
    if (res.status === 'success') {
      ElMessage.success('退货物流状态更新成功')
    } else {
      ElMessage.error(res.return_logistics_status || '更新失败')
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '更新失败')
  }
}
</script>

<style scoped>
.return-page { padding: 20px; }
.page-title { margin-top: 0; margin-bottom: 20px; }
.toolbar { margin-bottom: 16px; }
</style>
