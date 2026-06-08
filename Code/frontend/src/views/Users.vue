<template>
  <div class="users-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <div class="header-buttons">
            <el-button type="primary" @click="showCreateDialog">
              <el-icon><Plus /></el-icon>
              新增用户
            </el-button>
            <el-button type="warning" @click="showLockedUsers = true">
              <el-icon><Lock /></el-icon>
              查看锁定用户
            </el-button>
          </div>
        </div>
      </template>

      <!-- 状态筛选 -->
      <el-radio-group v-model="statusFilter" @change="loadUsers" style="margin-bottom: 20px">
        <el-radio-button value="">全部</el-radio-button>
        <el-radio-button value="active">活跃</el-radio-button>
        <el-radio-button value="frozen">冻结</el-radio-button>
        <el-radio-button value="locked">锁定</el-radio-button>
      </el-radio-group>

      <!-- 用户列表表格 -->
      <el-table :data="tableData" border style="width: 100%">
        <el-table-column prop="id" label="ID" width="280" />
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="nickname" label="昵称" width="150" />
        <el-table-column prop="user_level" label="等级" width="120">
          <template #default="{ row }">
            <el-tag :type="getLevelTagType(row.user_level)">
              {{ row.user_level }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="balance" label="余额" width="120">
          <template #default="{ row }">
            ¥{{ row.balance }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.status === 'frozen'" type="info">冻结</el-tag>
            <el-tag v-else-if="row.is_locked" type="danger">锁定</el-tag>
            <el-tag v-else type="success">正常</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="showEditDialog(row)">
              编辑
            </el-button>
            <el-button v-if="row.is_locked" type="success" size="small" @click="handleUnlock(row)">
              解锁
            </el-button>
            <el-button v-if="row.status === 'frozen'" type="success" size="small" @click="handleUnfreeze(row)">
              解冻
            </el-button>
            <el-button v-if="row.status === 'active' && !row.is_locked" type="warning" size="small" @click="handleFreeze(row)">
              冻结
            </el-button>
            <el-button type="success" size="small" @click="showRechargeDialog(row)">
              充值
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">
              删除
            </el-button>
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

    <!-- 创建/编辑用户弹窗 -->
    <el-dialog v-model="showUserDialog" :title="isEdit ? '编辑用户' : '新增用户'" width="500px">
      <el-form :model="userForm" label-width="100px">
        <el-form-item label="用户名">
          <el-input v-model="userForm.username" :disabled="isEdit" />
        </el-form-item>
        <el-form-item v-if="!isEdit" label="密码">
          <el-input v-model="userForm.password" type="password" />
        </el-form-item>
        <el-form-item label="昵称">
          <el-input v-model="userForm.nickname" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="userForm.phone" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="userForm.email" />
        </el-form-item>
        <el-form-item label="用户等级">
          <el-select v-model="userForm.user_level">
            <el-option label="青铜会员" value="青铜会员" />
            <el-option label="白银会员" value="白银会员" />
            <el-option label="黄金会员" value="黄金会员" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="!isEdit" label="初始余额">
          <el-input-number v-model="userForm.balance" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item v-if="!isEdit" label="状态">
          <el-select v-model="userForm.status">
            <el-option label="活跃" value="active" />
            <el-option label="冻结" value="frozen" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showUserDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSaveUser">保存</el-button>
      </template>
    </el-dialog>

    <!-- 充值弹窗 -->
    <el-dialog v-model="showRecharge" title="充值余额" width="400px">
      <el-form :model="rechargeForm" label-width="100px">
        <el-form-item label="充值金额">
          <el-input-number v-model="rechargeForm.amount" :min="0.01" :precision="2" />
        </el-form-item>
        <el-form-item label="充值原因">
          <el-input v-model="rechargeForm.reason" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRecharge = false">取消</el-button>
        <el-button type="primary" @click="handleRecharge">确认充值</el-button>
      </template>
    </el-dialog>

    <!-- 锁定用户弹窗 -->
    <el-dialog v-model="showLockedUsers" title="被锁定的用户" width="800px">
      <el-table :data="lockedUsers" border style="width: 100%">
        <el-table-column prop="id" label="ID" width="280" />
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="nickname" label="昵称" width="150" />
        <el-table-column prop="failed_attempts" label="失败次数" width="100" />
        <el-table-column prop="lock_count" label="锁定次数" width="100">
          <template #default="{ row }">
            <el-tag type="warning">{{ row.lock_count }}次</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleUnlock(row)">
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
import { Plus, Lock } from '@element-plus/icons-vue'
import { getUsers, getLockedUsers, unlockUser, freezeUser, unfreezeUser, createUser, updateUser, deleteUser, rechargeBalance } from '@/api/user'

const tableData = ref([])
const lockedUsers = ref([])
const showLockedUsers = ref(false)
const showUserDialog = ref(false)
const showRecharge = ref(false)
const isEdit = ref(false)
const currentUserId = ref('')
const statusFilter = ref('')

const pagination = reactive({
  page: 1,
  limit: 10,
  total: 0
})

const userForm = reactive({
  username: '',
  password: '',
  nickname: '',
  phone: '',
  email: '',
  user_level: '青铜会员',
  balance: 0,
  status: 'active'
})

const rechargeForm = reactive({
  amount: 0,
  reason: ''
})

const getLevelTagType = (level) => {
  const typeMap = {
    '青铜会员': 'info',
    '白银会员': 'primary',
    '黄金会员': 'warning'
  }
  return typeMap[level] || 'info'
}

const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleString('zh-CN')
}

const loadUsers = async () => {
  try {
    const res = await getUsers(pagination.page, pagination.limit)
    let users = res.data.data || []
    // 根据状态筛选
    if (statusFilter.value) {
      if (statusFilter.value === 'locked') {
        users = users.filter(u => u.is_locked)
      } else {
        users = users.filter(u => u.status === statusFilter.value && !u.is_locked)
      }
    }
    tableData.value = users
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

const showCreateDialog = () => {
  isEdit.value = false
  Object.assign(userForm, {
    username: '',
    password: '',
    nickname: '',
    phone: '',
    email: '',
    user_level: '青铜会员',
    balance: 0,
    status: 'active'
  })
  showUserDialog.value = true
}

const showEditDialog = (row) => {
  isEdit.value = true
  currentUserId.value = row.id
  Object.assign(userForm, {
    username: row.username,
    nickname: row.nickname,
    phone: row.phone,
    email: row.email,
    user_level: row.user_level
  })
  showUserDialog.value = true
}

const handleSaveUser = async () => {
  try {
    if (isEdit.value) {
      await updateUser(currentUserId.value, userForm)
      ElMessage.success('更新成功')
    } else {
      await createUser(userForm)
      ElMessage.success('创建成功')
    }
    showUserDialog.value = false
    loadUsers()
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

const handleFreeze = async (row) => {
  try {
    await ElMessageBox.confirm('确定要冻结该用户吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await freezeUser(row.id)
    ElMessage.success('冻结成功')
    loadUsers()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
    }
  }
}

const handleUnfreeze = async (row) => {
  try {
    await ElMessageBox.confirm('确定要解冻该用户吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await unfreezeUser(row.id)
    ElMessage.success('解冻成功')
    loadUsers()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
    }
  }
}

const showRechargeDialog = (row) => {
  currentUserId.value = row.id
  rechargeForm.amount = 0
  rechargeForm.reason = ''
  showRecharge.value = true
}

const handleRecharge = async () => {
  try {
    await rechargeBalance(currentUserId.value, rechargeForm)
    ElMessage.success('充值成功')
    showRecharge.value = false
    loadUsers()
  } catch (error) {
    console.error(error)
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该用户吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteUser(row.id)
    ElMessage.success('删除成功')
    loadUsers()
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

.header-buttons {
  display: flex;
  gap: 10px;
}
</style>