<template>
  <div class="dashboard-container">
    <el-card class="welcome-card">
      <div class="welcome-content">
        <h2>欢迎回来，{{ userInfo?.nickname || userInfo?.username }}</h2>
        <p class="role-info">当前角色：{{ roleName }}</p>
      </div>
    </el-card>

    <div class="stats-grid">
      <el-card class="stat-card">
        <div class="stat-icon">
          <el-icon class="icon-balance"><Wallet /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-label">账户余额</div>
          <div class="stat-value">¥{{ userInfo?.balance || '0.00' }}</div>
        </div>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-icon">
          <el-icon class="icon-level"><Medal /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-label">会员等级</div>
          <div class="stat-value">{{ userInfo?.user_level || '普通会员' }}</div>
        </div>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-icon">
          <el-icon class="icon-points"><Star /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-label">会员积分</div>
          <div class="stat-value">{{ userInfo?.points || '0' }}</div>
        </div>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-icon">
          <el-icon class="icon-discount"><Discount /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-label">优惠折扣</div>
          <div class="stat-value">{{ (userInfo?.discount_rate * 100 || 100).toFixed(0) }}%</div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useUserStore } from '@/stores/user'
import { Wallet, Medal, Star, Discount } from '@element-plus/icons-vue'

const userStore = useUserStore()
const userInfo = computed(() => userStore.userInfo)

const roleName = computed(() => {
  const role = userInfo.value?.role
  if (role === 'admin') return '管理员'
  if (role === 'vip') return 'VIP会员'
  return '普通用户'
})
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
}

.welcome-card {
  margin-bottom: 20px;
}

.welcome-content {
  text-align: center;
}

.welcome-content h2 {
  margin: 0 0 10px 0;
  color: #304156;
}

.role-info {
  margin: 0;
  color: #999;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20px;
}

.icon-balance {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.icon-level {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.icon-points {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.icon-discount {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  color: white;
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #999;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #304156;
}

@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>