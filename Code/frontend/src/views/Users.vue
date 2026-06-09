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
          </div>
        </div>
      </template>

      <!-- 状态筛选 -->
      <el-radio-group v-model="statusFilter" @change="loadUsers" style="margin-bottom: 20px">
        <el-radio-button value="">全部</el-radio-button>
        <el-radio-button value="locked">锁定</el-radio-button>
      </el-radio-group>

      <!-- 用户列表表格 -->
      <el-table :data="tableData" border style="width: 100%">
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="nickname" label="昵称" width="150" />
        <el-table-column label="角色" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.role" :type="getRoleTagType(row.role)">
              {{ getRoleLabel(row.role) }}
            </el-tag>
            <el-tag v-else type="info">未分配</el-tag>
          </template>
        </el-table-column>
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
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.is_locked" type="danger">锁定</el-tag>
            <el-tag v-else type="success">正常</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.create_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="320" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="showEditDialog(row)">
              编辑
            </el-button>
            <el-button type="warning" size="small" @click="showRoleDialog(row)">
              角色
            </el-button>
            <el-button v-if="row.is_locked" type="success" size="small" @click="handleUnlock(row)">
              解锁
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

    <!-- 修改角色弹窗 -->
    <el-dialog v-model="showRoleDialogVisible" title="修改角色" width="400px">
      <el-form :model="roleForm" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="roleForm.username" disabled />
        </el-form-item>
        <el-form-item label="当前角色">
          <el-tag v-if="roleForm.currentRole" :type="getRoleTagType(roleForm.currentRole)">
            {{ getRoleLabel(roleForm.currentRole) }}
          </el-tag>
          <el-tag v-else type="info">未分配</el-tag>
        </el-form-item>
        <el-form-item label="新角色">
          <el-select v-model="roleForm.roleId" placeholder="请选择角色" style="width: 100%">
            <el-option label="系统管理员" value="r-001">
              <span style="float: left">系统管理员</span>
              <span style="float: right; color: #8492a6; font-size: 12px">admin</span>
            </el-option>
            <el-option label="普通用户" value="r-002">
              <span style="float: left">普通用户</span>
              <span style="float: right; color: #8492a6; font-size: 12px">user</span>
            </el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRoleDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleChangeRole">确认修改</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getUsers, unlockUser, createUser, updateUser, deleteUser, rechargeBalance, updateUserRole } from '@/api/user'

const tableData = ref([])
const showUserDialog = ref(false)
const showRecharge = ref(false)
const showRoleDialogVisible = ref(false)
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
  balance: 0
})

const rechargeForm = reactive({
  amount: 0,
  reason: ''
})

const roleForm = reactive({
  username: '',
  currentRole: '',
  roleId: ''
})

const getLevelTagType = (level) => {
  const typeMap = {
    '青铜会员': 'info',
    '白银会员': 'primary',
    '黄金会员': 'warning'
  }
  return typeMap[level] || 'info'
}

const getRoleTagType = (roleName) => {
  const typeMap = {
    'admin': 'danger',
    'user': 'primary'
  }
  return typeMap[roleName] || 'info'
}

const getRoleLabel = (roleName) => {
  const labelMap = {
    'admin': '管理员',
    'user': '普通用户'
  }
  return labelMap[roleName] || roleName
}

const formatDate = (date) => {
  if (!date) return ''
  const d = new Date(date)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  const seconds = String(d.getSeconds()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

const loadUsers = async () => {
  try {
    const res = await getUsers(pagination.page, pagination.limit)
    let users = res.data.data || []
    // 根据状态筛选
    if (statusFilter.value === 'locked') {
      users = users.filter(u => u.is_locked)
    }
    tableData.value = users
    pagination.total = res.data.total || 0
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
    balance: 0
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

const ROLE_MAP = {
  'admin': 'r-001',
  'user': 'r-002'
}

const showRoleDialog = (row) => {
  currentUserId.value = row.id
  roleForm.username = row.username
  roleForm.currentRole = row.role || ''
  // role 现在是字符串（admin/user），需要通过映射转为 role_id
  roleForm.roleId = ROLE_MAP[row.role] || ''
  showRoleDialogVisible.value = true
}

const handleChangeRole = async () => {
  if (!roleForm.roleId) {
    ElMessage.warning('请选择角色')
    return
  }
  try {
    await updateUserRole(currentUserId.value, { role_id: roleForm.roleId })
    ElMessage.success('角色修改成功')
    showRoleDialogVisible.value = false
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