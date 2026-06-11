<template>
  <div class="logistics-page">
    <h2 class="page-title">{{ isAdmin ? '物流管理' : '我的物流' }}</h2>

    <!-- 物流列表 -->
    <div>
      <el-table v-if="logisticsList.length > 0" :data="logisticsList" border style="width: 100%">
        <el-table-column prop="logistics_status" label="物流状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.logistics_status)">{{ scope.row.logistics_status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="track_info" label="轨迹信息" show-overflow-tooltip />
        <el-table-column prop="create_time" label="创建时间" width="160">
          <template #default="scope">{{ formatDate(scope.row.create_time) }}</template>
        </el-table-column>
        <el-table-column prop="update_time" label="更新时间" width="160">
          <template #default="scope">{{ formatDate(scope.row.update_time) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="scope">
            <el-button 
              v-if="scope.row.logistics_status !== '已签收'" 
              size="small" 
              type="primary" 
              @click="confirmReceipt(scope.row)"
            >确认收货</el-button>
            <span v-else>-</span>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="logisticsList.length === 0 && !loading" description="暂无物流记录" />
      <el-loading v-if="loading" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getUserLogistics, confirmReceipt as confirmReceiptApi } from '@/api/logistics'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const isAdmin = computed(() => userStore.userInfo?.role === 'admin')

const loading = ref(false)
const logisticsList = ref([])

const formatDate = (d) => d ? new Date(d).toLocaleString('zh-CN', { hour12: false }) : '-'

const getStatusType = (status) => {
  const types = {
    '待发货': 'warning',
    '已揽收': 'info',
    '运输中': 'primary',
    '派送中': 'success',
    '已签收': 'success',
    '异常': 'danger'
  }
  return types[status] || 'default'
}

const loadLogistics = async () => {
  if (!userStore.userInfo?.id) {
    ElMessage.warning('请先登录')
    return
  }
  loading.value = true
  try {
    const res = await getUserLogistics(userStore.userInfo.id)
    if (res.code === 200) {
      logisticsList.value = res.data
    }
  } catch (e) {
    ElMessage.error('获取物流记录失败')
  } finally {
    loading.value = false
  }
}

const confirmReceipt = async (logistics) => {
  try {
    const res = await confirmReceiptApi(logistics.logistics_id)
    if (res.code === 200) {
      ElMessage.success('确认收货成功')
      loadLogistics() // 刷新物流列表
    } else {
      ElMessage.error(res.message || '确认收货失败')
    }
  } catch (e) {
    ElMessage.error('确认收货失败')
  }
}

onMounted(() => {
  loadLogistics()
})
</script>

<style scoped>
.logistics-page { padding: 20px; }
.page-title { margin-top: 0; margin-bottom: 20px; }
</style>
