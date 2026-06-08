<template>
  <div class="header">
    <h3>电商管理平台</h3>
    <div class="user-info">
      <el-dropdown>
        <span class="username">
          {{ userStore.userInfo?.username || '用户' }}
          <el-icon><ArrowDown /></el-icon>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="handleViewProfile">查看个人信息</el-dropdown-item>
            <el-dropdown-item @click="handleEditProfile">修改个人信息</el-dropdown-item>
            <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>

  <!-- 查看个人信息弹窗 -->
  <el-dialog
    v-model="showInfoModal"
    title="个人信息"
    width="400px"
  >
    <el-form :model="userInfo" label-width="80px">
      <el-form-item label="用户名">
        <el-input v-model="userInfo.username" disabled />
      </el-form-item>
      <el-form-item label="角色">
        <el-input v-model="userInfo.role" disabled />
      </el-form-item>
      <el-form-item label="关联ID">
        <el-input v-model="userInfo.related_id" disabled />
      </el-form-item>
      <el-form-item label="失败次数">
        <el-input v-model="userInfo.failed_attempts" disabled />
      </el-form-item>
      <el-form-item label="锁定次数">
        <el-input v-model="userInfo.lock_count" disabled />
      </el-form-item>
      <el-form-item label="账户状态">
        <el-input v-model="userInfo.status" disabled />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button type="primary" @click="showInfoModal = false">关闭</el-button>
    </template>
  </el-dialog>

  <!-- 修改个人信息弹窗 -->
  <el-dialog
    v-model="showProfileModal"
    title="修改个人信息"
    width="400px"
  >
    <el-form :model="profileForm" label-width="80px">
      <el-form-item label="用户名">
        <el-input v-model="profileForm.username" disabled />
      </el-form-item>
      <el-form-item label="原密码">
        <el-input v-model="profileForm.oldPassword" type="password" placeholder="请输入原密码" />
      </el-form-item>
      <el-form-item label="新密码">
        <el-input v-model="profileForm.newPassword" type="password" placeholder="请输入新密码" />
      </el-form-item>
      <el-form-item label="确认密码">
        <el-input v-model="profileForm.confirmPassword" type="password" placeholder="请再次输入新密码" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="showProfileModal = false">取消</el-button>
      <el-button type="primary" @click="handleUpdateProfile">保存修改</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'
import { updateUserInfo } from '@/api/auth'

const router = useRouter()
const userStore = useUserStore()

const showInfoModal = ref(false)
const showProfileModal = ref(false)
const profileForm = reactive({
  username: userStore.userInfo?.username || '',
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const userInfo = reactive({
  username: '',
  role: '',
  related_id: '',
  failed_attempts: 0,
  lock_count: 0,
  status: ''
})

const handleViewProfile = () => {
  const info = userStore.userInfo || {}
  userInfo.username = info.username || ''
  userInfo.role = info.role === 'admin' ? '管理员' : '普通用户'
  userInfo.related_id = info.related_id || '-'
  userInfo.failed_attempts = info.failed_attempts || 0
  userInfo.lock_count = info.lock_count || 0
  userInfo.status = info.is_locked ? '已锁定' : '正常'
  showInfoModal.value = true
}

const handleEditProfile = () => {
  profileForm.username = userStore.userInfo?.username || ''
  profileForm.oldPassword = ''
  profileForm.newPassword = ''
  profileForm.confirmPassword = ''
  showProfileModal.value = true
}

const handleLogout = () => {
  userStore.logout()
  ElMessage.success('已退出登录')
  router.push('/login')
}

const handleUpdateProfile = async () => {
  if (!profileForm.oldPassword) {
    ElMessage.error('请输入原密码')
    return
  }
  if (!profileForm.newPassword) {
    ElMessage.error('请输入新密码')
    return
  }
  if (profileForm.newPassword !== profileForm.confirmPassword) {
    ElMessage.error('两次输入的新密码不一致')
    return
  }

  try {
    const response = await updateUserInfo({
      old_password: profileForm.oldPassword,
      new_password: profileForm.newPassword
    })
    if (response.code === 200) {
      ElMessage.success(response.message || '修改成功')
      showProfileModal.value = false
    } else {
      ElMessage.error(response.message || '修改失败')
    }
  } catch (error) {
    // 处理后端返回的错误响应
    if (error.response) {
      ElMessage.error(error.response.data?.message || '修改失败')
    } else {
      ElMessage.error('修改失败，请稍后重试')
    }
    console.error('修改个人信息失败:', error)
  }
}
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.username {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
}
</style>