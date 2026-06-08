<template>
  <div class="logs-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>日志管理</span>
        </div>
      </template>

      <!-- 日志类型切换 -->
      <el-tabs v-model="activeTab" @tab-change="loadLogs">
        <el-tab-pane label="登录日志" name="login">
          <el-table :data="tableData" border style="width: 100%">
            <el-table-column prop="id" label="ID" width="280" />
            <el-table-column prop="username" label="用户名" width="150" />
            <el-table-column prop="ip_address" label="IP地址" width="150" />
            <el-table-column prop="login_type" label="登录方式" width="120" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'success' ? 'success' : 'danger'">
                  {{ row.status === 'success' ? '成功' : '失败' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="error_message" label="错误信息" />
            <el-table-column prop="login_time" label="登录时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.login_time) }}
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="操作日志" name="operation">
          <el-table :data="tableData" border style="width: 100%">
            <el-table-column prop="id" label="ID" width="280" />
            <el-table-column prop="username" label="用户名" width="150" />
            <el-table-column prop="module" label="模块" width="120" />
            <el-table-column prop="action" label="操作" width="120" />
            <el-table-column prop="description" label="描述" />
            <el-table-column prop="ip_address" label="IP地址" width="150" />
            <el-table-column prop="operation_time" label="操作时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.operation_time) }}
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.limit"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getLoginLogs, getOperationLogs } from '@/api/log'

const activeTab = ref('login')
const tableData = ref([])

const pagination = reactive({
  page: 1,
  limit: 10,
  total: 0
})

const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleString('zh-CN')
}

const loadLogs = async () => {
  try {
    const params = {
      page: pagination.page,
      limit: pagination.limit
    }
    if (activeTab.value === 'login') {
      const res = await getLoginLogs(params)
      tableData.value = res.data?.data || []
      pagination.total = res.data?.total || 0
    } else {
      const res = await getOperationLogs(params)
      tableData.value = res.data?.data || []
      pagination.total = res.data?.total || 0
    }
  } catch (error) {
    console.error(error)
  }
}

const handleSizeChange = (val) => {
  pagination.limit = val
  loadLogs()
}

const handleCurrentChange = (val) => {
  pagination.page = val
  loadLogs()
}

onMounted(() => {
  loadLogs()
})
</script>

<style scoped>
.logs-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>