<template>
  <div class="users-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <el-button type="primary" @click="showLockedUsers = true">
            <el-icon><Lock /></el-icon>
            查看锁定用户
          </el-button>
        </div>
      </template>

      <!-- 用户列表表格 -->
      <el-table :data="tableData" border style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="role" label="角色" width="120">
          <template #default="{ row }">
            <el-tag :type="getRoleTagType(row.role)">
              {{ getRoleText(row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_locked" label="状态" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.is_locked" type="danger">
              <el-icon><Lock /></el-icon>
              已锁定
            </el-tag>
            <el-tag v-else type="success">
              <el-icon><Unlock /></el-icon>
              正常
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="failed_attempts" label="失败次数" width="100" />
        <el-table-column prop="lock_count" label="锁定次数" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.lock_count > 0" type="warning">
              {{ row.lock_count }}次
            </el-tag>
            <span v-else class="text-gray">无</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.is_locked"
              type="primary"
              size="small"
              @click="handleUnlock(row)"
            >
              <el-icon><Unlock /></el-icon>
              解锁
            </el-button>
            <span v-else class="text-gray">无操作</span>
          </template>
        </el-table-column>
      </el-table>

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

    <!-- 锁定用户弹窗 -->
    <el-dialog
      v-model="showLockedUsers"
      title="被锁定的用户"
      width="600px"
    >
      <el-table :data="lockedUsers" border style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="role" label="角色" width="120">
          <template #default="{ row }">
            <el-tag :type="getRoleTagType(row.role)">
              {{ getRoleText(row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lock_remaining_seconds" label="剩余锁定时间" width="150">
          <template #default="{ row }">
            {{ formatRemainingTime(row.lock_remaining_seconds) }}
          </template>
        </el-table-column>
        <el-table-column prop="failed_attempts" label="失败次数" width="100" />
        <el-table-column prop="lock_count" label="锁定次数" width="100">
          <template #default="{ row }">
            <el-tag type="warning">
              {{ row.lock_count }}次
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="handleUnlock(row)"
            >
              <el-icon><Unlock /></el-icon>
              解锁
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Lock, Unlock } from '@element-plus/icons-vue'
import { getUsers, getLockedUsers, unlockUser } from '@/api/user'

const tableData = ref([])
const lockedUsers = ref([])
const showLockedUsers = ref(false)

const pagination = reactive({
  page: 1,
  limit: 10,
  total: 0
})

const getRoleText = (role) => {
  const roleMap = {
    admin: '管理员',
    teacher: '教师',
    student: '学生'
  }
  return roleMap[role] || role
}

const getRoleTagType = (role) => {
  const typeMap = {
    admin: 'warning',
    teacher: 'primary',
    student: 'success'
  }
  return typeMap[role] || 'info'
}

const formatRemainingTime = (seconds) => {
  if (seconds <= 0) return '已过期'
  const minutes = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${minutes}分${secs}秒`
}

const loadUsers = async () => {
  try {
    const res = await getUsers(pagination.page, pagination.limit)
    tableData.value = res.data.data || []
    pagination.total = res.data.total || 0
  } catch (error) {
    console.error(error)
  }
}

const loadLockedUsers = async () => {
  try {
    const res = await getLockedUsers()
    lockedUsers.value = res.data || []
  } catch (error) {
    console.error(error)
  }
}

const handleUnlock = async (row) => {
  try {
    await ElMessageBox.confirm('确定要解锁该用户吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await unlockUser(row.id)
    ElMessage.success('解锁成功')
    loadUsers()
    loadLockedUsers()
    showLockedUsers.value = false
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
    }
  }
}

const handleSizeChange = (val) => {
  pagination.limit = val
  loadUsers()
}

const handleCurrentChange = (val) => {
  pagination.page = val
  loadUsers()
}

const openLockedDialog = () => {
  loadLockedUsers()
  showLockedUsers.value = true
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.users-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.text-gray {
  color: #999;
}
</style>
