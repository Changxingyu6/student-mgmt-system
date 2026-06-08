<template>
  <el-menu
    :default-active="activeMenu"
    router
    background-color="#304156"
    text-color="#bfcbd9"
    active-text-color="#409eff"
  >
    <!-- 管理员菜单 -->
    <el-menu-item index="/users" v-if="isAdmin">
      <el-icon><User /></el-icon>
      <span>用户管理</span>
    </el-menu-item>
    <el-menu-item index="/roles" v-if="isAdmin">
      <el-icon><Lock /></el-icon>
      <span>角色管理</span>
    </el-menu-item>
    <el-menu-item index="/logs" v-if="isAdmin">
      <el-icon><Document /></el-icon>
      <span>日志管理</span>
    </el-menu-item>
    
    <!-- 分隔线 -->
    <el-divider style="background-color: #435b71;" />
    
    <!-- 普通用户菜单 -->
    <el-menu-item index="/addresses">
      <el-icon><MapLocation /></el-icon>
      <span>收货地址</span>
    </el-menu-item>
    <el-menu-item index="/cart">
      <el-icon><ShoppingCart /></el-icon>
      <span>购物车</span>
    </el-menu-item>
  </el-menu>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { User, Lock, Document, MapLocation, ShoppingCart } from '@element-plus/icons-vue'

const route = useRoute()
const userStore = useUserStore()

const activeMenu = computed(() => route.path)
const isAdmin = computed(() => userStore.userInfo?.role === 'admin')
</script>