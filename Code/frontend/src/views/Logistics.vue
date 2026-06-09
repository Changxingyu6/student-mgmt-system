<template>
  <div class="logistics-page">
    <h2 class="page-title">{{ isAdmin ? '物流管理' : '我的物流' }}</h2>

    <el-tabs v-model="activeTab">
      <el-tab-pane label="物流查询" name="query"></el-tab-pane>
      <el-tab-pane v-if="isAdmin" label="创建物流" name="create"></el-tab-pane>
      <el-tab-pane v-if="isAdmin" label="更新物流" name="update"></el-tab-pane>
    </el-tabs>

    <!-- 查询 -->
    <div v-show="activeTab === 'query'">
      <el-radio-group v-model="queryType" style="margin-bottom: 16px">
        <el-radio-button value="id">按物流ID</el-radio-button>
        <el-radio-button value="order">按订单ID</el-radio-button>
      </el-radio-group>

      <div class="toolbar">
        <el-input v-model="queryId" :placeholder="queryType === 'id' ? '物流单ID' : '订单ID'" style="width: 400px" clearable />
        <el-button type="primary" @click="queryLogistics" style="margin-left: 8px">查询</el-button>
      </div>

      <el-descriptions v-if="logisticsDetail" :column="2" border>
        <el-descriptions-item label="物流ID">{{ logisticsDetail.id || '-' }}</el-descriptions-item>
        <el-descriptions-item label="订单ID">{{ logisticsDetail.order_id }}</el-descriptions-item>
        <el-descriptions-item label="状态" :span="2">
          <el-tag>{{ logisticsDetail.logistics_status || logisticsDetail.status }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="轨迹信息" :span="2">{{ logisticsDetail.track_info || '-' }}</el-descriptions-item>
      </el-descriptions>
    </div>

    <!-- 创建 -->
    <div v-show="activeTab === 'create'">
      <el-form :model="createForm" label-width="100px" style="max-width: 500px">
        <el-form-item label="订单ID">
          <el-input v-model="createForm.order_id" />
        </el-form-item>
        <el-form-item label="物流单ID">
          <el-input v-model="createForm.logistics_id" />
        </el-form-item>
        <el-form-item label="物流状态">
          <el-select v-model="createForm.logistics_status" style="width: 100%">
            <el-option label="待发货" value="to_be_shipped" />
            <el-option label="已揽收" value="collected" />
            <el-option label="运输中" value="in_transit" />
            <el-option label="派送中" value="out_for_delivery" />
            <el-option label="已签收" value="signed" />
            <el-option label="异常" value="abnormal" />
          </el-select>
        </el-form-item>
        <el-form-item label="轨迹信息">
          <el-input v-model="createForm.track_info" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleCreate">创建</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 更新 -->
    <div v-show="activeTab === 'update'">
      <el-form :model="updateForm" label-width="100px" style="max-width: 500px">
        <el-form-item label="物流单ID">
          <el-input v-model="updateForm.logistics_id" />
        </el-form-item>
        <el-form-item label="物流状态">
          <el-select v-model="updateForm.logistics_status" style="width: 100%">
            <el-option label="待发货" value="to_be_shipped" />
            <el-option label="已揽收" value="collected" />
            <el-option label="运输中" value="in_transit" />
            <el-option label="派送中" value="out_for_delivery" />
            <el-option label="已签收" value="signed" />
            <el-option label="异常" value="abnormal" />
          </el-select>
        </el-form-item>
        <el-form-item label="轨迹信息">
          <el-input v-model="updateForm.track_info" type="textarea" :rows="3" />
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
import { getLogistics, getLogisticsByOrder, createLogistics, updateLogistics } from '@/api/logistics'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const isAdmin = computed(() => userStore.userInfo?.role === 'admin')

const activeTab = ref('query')
const queryType = ref('id')
const queryId = ref('')
const logisticsDetail = ref(null)

const queryLogistics = async () => {
  if (!queryId.value) { ElMessage.warning('请输入ID'); return }
  try {
    logisticsDetail.value = queryType.value === 'id'
      ? await getLogistics(queryId.value)
      : await getLogisticsByOrder(queryId.value)
  } catch (e) {
    logisticsDetail.value = null
    ElMessage.error('未找到该物流记录')
  }
}

const createForm = reactive({
  order_id: '', logistics_id: '',
  logistics_status: 'to_be_shipped', track_info: ''
})
const handleCreate = async () => {
  try {
    const res = await createLogistics(createForm)
    if (res.status === 'success') {
      ElMessage.success('创建物流记录成功')
      Object.assign(createForm, { order_id: '', logistics_id: '', logistics_status: 'to_be_shipped', track_info: '' })
    } else {
      ElMessage.error(res.logistics_status || '创建失败')
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '创建失败')
  }
}

const updateForm = reactive({ logistics_id: '', logistics_status: 'in_transit', track_info: '' })
const handleUpdate = async () => {
  try {
    const res = await updateLogistics(updateForm)
    if (res.status === 'success') {
      ElMessage.success('物流状态更新成功')
    } else {
      ElMessage.error(res.logistics_status || '更新失败')
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '更新失败')
  }
}
</script>

<style scoped>
.logistics-page { padding: 20px; }
.page-title { margin-top: 0; margin-bottom: 20px; }
.toolbar { margin-bottom: 16px; }
</style>
