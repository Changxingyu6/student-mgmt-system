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
            <el-dropdown-item @click="handleEditInfo">修改个人信息</el-dropdown-item>
            <el-dropdown-item @click="handleChangePassword">修改密码</el-dropdown-item>
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
      <el-form-item label="昵称">
        <el-input v-model="userInfo.nickname" disabled />
      </el-form-item>
      <el-form-item label="手机号">
        <el-input v-model="userInfo.phone" disabled />
      </el-form-item>
      <el-form-item label="邮箱">
        <el-input v-model="userInfo.email" disabled />
      </el-form-item>
      <el-form-item label="性别">
        <el-input v-model="userInfo.gender" disabled />
      </el-form-item>
      <el-form-item label="角色">
        <el-input v-model="userInfo.role" disabled />
      </el-form-item>
      <el-form-item label="用户等级">
        <el-input v-model="userInfo.user_level" disabled />
      </el-form-item>
      <el-form-item label="会员积分">
        <el-input v-model="userInfo.points" disabled />
      </el-form-item>
      <el-form-item label="账户余额">
        <el-input v-model="userInfo.balance" disabled />
      </el-form-item>
      <el-form-item label="优惠折扣">
        <el-input v-model="userInfo.discount_rate" disabled />
      </el-form-item>
      <el-form-item label="创建时间">
        <el-input v-model="userInfo.create_time" disabled />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button type="primary" @click="showInfoModal = false">关闭</el-button>
    </template>
  </el-dialog>

  <!-- 修改密码弹窗 -->
  <el-dialog
    v-model="showPasswordModal"
    title="修改密码"
    width="400px"
  >
    <el-form :model="passwordForm" label-width="80px">
      <el-form-item label="用户名">
        <el-input v-model="passwordForm.username" disabled />
      </el-form-item>
      <el-form-item label="原密码">
        <el-input v-model="passwordForm.oldPassword" type="password" placeholder="请输入原密码" />
      </el-form-item>
      <el-form-item label="新密码">
        <el-input v-model="passwordForm.newPassword" type="password" placeholder="请输入新密码" />
      </el-form-item>
      <el-form-item label="确认密码">
        <el-input v-model="passwordForm.confirmPassword" type="password" placeholder="请再次输入新密码" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="showPasswordModal = false">取消</el-button>
      <el-button type="primary" @click="handleUpdatePassword">确认修改</el-button>
    </template>
  </el-dialog>

  <!-- 修改个人信息弹窗 -->
  <el-dialog
    v-model="showInfoEditModal"
    title="修改个人信息"
    width="400px"
  >
    <el-form :model="infoForm" label-width="80px">
      <el-form-item label="用户名">
        <el-input v-model="infoForm.username" disabled />
      </el-form-item>
      <el-form-item label="昵称">
        <el-input v-model="infoForm.nickname" placeholder="请输入昵称" />
      </el-form-item>
      <el-form-item label="手机号">
        <el-input v-model="infoForm.phone" placeholder="请输入手机号" />
      </el-form-item>
      <el-form-item label="邮箱">
        <el-input v-model="infoForm.email" placeholder="请输入邮箱" />
      </el-form-item>
      <el-form-item label="性别">
        <el-radio-group v-model="infoForm.gender">
          <el-radio value="male">男</el-radio>
          <el-radio value="female">女</el-radio>
        </el-radio-group>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="showInfoEditModal = false">取消</el-button>
      <el-button type="primary" @click="handleUpdateInfo">保存修改</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'
import { updatePassword, updateProfile } from '@/api/auth'

const router = useRouter()
const userStore = useUserStore()

const showInfoModal = ref(false)
const showPasswordModal = ref(false)
const showInfoEditModal = ref(false)

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

const passwordForm = reactive({
  username: userStore.userInfo?.username || '',
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const infoForm = reactive({
  username: '',
  nickname: '',
  phone: '',
  email: '',
  gender: ''
})

const userInfo = reactive({
  username: '',
  nickname: '',
  phone: '',
  email: '',
  gender: '',
  role: '',
  user_level: '',
  points: 0,
  balance: 0,
  discount_rate: '',
  create_time: ''
})

const handleViewProfile = () => {
  const info = userStore.userInfo || {}
  userInfo.username = info.username || '-'
  userInfo.nickname = info.nickname || '-'
  userInfo.phone = info.phone || '-'
  userInfo.email = info.email || '-'
  userInfo.gender = info.gender === 'male' ? '男' : info.gender === 'female' ? '女' : '-'
  userInfo.role = info.role === 'admin' ? '管理员' : '普通用户'
  userInfo.user_level = info.user_level || '-'
  userInfo.points = info.points || 0
  userInfo.balance = info.balance || 0
  userInfo.discount_rate = info.discount_rate ? `${(info.discount_rate * 100).toFixed(0)}%` : '100%'
  userInfo.create_time = formatDate(info.create_time) || '-'
  showInfoModal.value = true
}

const handleEditInfo = () => {
  const info = userStore.userInfo || {}
  infoForm.username = info.username || ''
  infoForm.nickname = info.nickname || ''
  infoForm.phone = info.phone || ''
  infoForm.email = info.email || ''
  infoForm.gender = info.gender || ''
  showInfoEditModal.value = true
}

const handleChangePassword = () => {
  passwordForm.username = userStore.userInfo?.username || ''
  passwordForm.oldPassword = ''
  passwordForm.newPassword = ''
  passwordForm.confirmPassword = ''
  showPasswordModal.value = true
}

const handleLogout = () => {
  userStore.logout()
  ElMessage.success('已退出登录')
  router.push('/login')
}

const handleUpdatePassword = async () => {
  if (!passwordForm.oldPassword) {
    ElMessage.error('请输入原密码')
    return
  }
  if (!passwordForm.newPassword) {
    ElMessage.error('请输入新密码')
    return
  }
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    ElMessage.error('两次输入的新密码不一致')
    return
  }

  try {
    const response = await updatePassword({
      old_password: passwordForm.oldPassword,
      new_password: passwordForm.newPassword
    })
    if (response.code === 200) {
      ElMessage.success(response.message || '密码修改成功')
      showPasswordModal.value = false
    } else {
      ElMessage.error(response.message || '密码修改失败')
    }
  } catch (error) {
    if (error.response) {
      ElMessage.error(error.response.data?.message || '密码修改失败')
    } else {
      ElMessage.error('密码修改失败，请稍后重试')
    }
    console.error('修改密码失败:', error)
  }
}

const handleUpdateInfo = async () => {
  if (!infoForm.nickname && !infoForm.phone && !infoForm.email && !infoForm.gender) {
    ElMessage.warning('请至少修改一项信息')
    return
  }

  try {
    const data = {
      nickname: infoForm.nickname,
      phone: infoForm.phone,
      email: infoForm.email,
      gender: infoForm.gender
    }
    const response = await updateProfile(data)
    if (response.code === 200) {
      ElMessage.success(response.message || '个人信息修改成功')
      // 更新 store 中的用户信息
      await userStore.getUserInfo()
      showInfoEditModal.value = false
    } else {
      ElMessage.error(response.message || '个人信息修改失败')
    }
  } catch (error) {
    if (error.response) {
      ElMessage.error(error.response.data?.message || '个人信息修改失败')
    } else {
      ElMessage.error('个人信息修改失败，请稍后重试')
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