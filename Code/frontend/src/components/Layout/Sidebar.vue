<template>
  <el-menu
    :default-active="activeMenu"
    router
    background-color="#304156"
    text-color="#bfcbd9"
    active-text-color="#409eff"
  >
    <!-- 购物（所有人可见） -->
    <el-sub-menu index="shopping">
      <template #title>
        <el-icon><ShoppingCart /></el-icon>
        <span>购物</span>
      </template>
      <el-menu-item index="/goods">
        <el-icon><Goods /></el-icon>
        <span>商品列表</span>
      </el-menu-item>
      <el-menu-item index="/coupons">
        <el-icon><Ticket /></el-icon>
        <span>营销活动</span>
      </el-menu-item>
      <el-menu-item index="/cart">
        <el-icon><ShoppingCart /></el-icon>
        <span>我的购物车</span>
      </el-menu-item>
    </el-sub-menu>

    <!-- 我的订单（所有人可见） -->
    <el-sub-menu index="order">
      <template #title>
        <el-icon><Tickets /></el-icon>
        <span>我的订单</span>
      </template>
      <el-menu-item index="/payments">
        <el-icon><Money /></el-icon>
        <span>我的支付</span>
      </el-menu-item>
      <el-menu-item index="/logistics">
        <el-icon><Van /></el-icon>
        <span>我的物流</span>
      </el-menu-item>
      <el-menu-item index="/refunds">
        <el-icon><RefreshLeft /></el-icon>
        <span>我的退款</span>
      </el-menu-item>
      <el-menu-item index="/return-logistics">
        <el-icon><Box /></el-icon>
        <span>我的退货物流</span>
      </el-menu-item>
      <el-menu-item index="/addresses">
        <el-icon><MapLocation /></el-icon>
        <span>收货地址</span>
      </el-menu-item>
    </el-sub-menu>

    <!-- 系统管理（仅管理员可见） -->
    <el-sub-menu index="admin" v-if="isAdmin">
      <template #title>
        <el-icon><Setting /></el-icon>
        <span>系统管理</span>
      </template>
      <el-menu-item index="/users">
        <el-icon><User /></el-icon>
        <span>用户管理</span>
      </el-menu-item>
      <el-menu-item index="/roles">
        <el-icon><Lock /></el-icon>
        <span>角色管理</span>
      </el-menu-item>
      <el-menu-item index="/logs">
        <el-icon><Document /></el-icon>
        <span>日志管理</span>
      </el-menu-item>
    </el-sub-menu>
  </el-menu>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { User, Lock, Document, MapLocation, ShoppingCart, Goods, Ticket, Money, Van, RefreshLeft, Box, Setting, Tickets } from '@element-plus/icons-vue'

const route = useRoute()
const userStore = useUserStore()

const activeMenu = computed(() => route.path)
const isAdmin = computed(() => userStore.userInfo?.role === 'admin')
</script>
