<template>
  <el-menu
    :default-active="activeMenu"
    router
    background-color="#304156"
    text-color="#bfcbd9"
    active-text-color="#409eff"
  >
    <el-menu-item index="/students">
      <el-icon><User /></el-icon>
      <span>学生管理</span>
    </el-menu-item>
  </el-menu>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { User } from '@element-plus/icons-vue'

const route = useRoute()
const activeMenu = computed(() => route.path)
</script>