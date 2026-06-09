<template>
  <div class="layout-container">
    <el-container direction="vertical">
      <!-- 顶部 Header（铺满全宽） -->
      <el-header class="layout-header">
        <Header />
      </el-header>

      <el-container class="layout-body">
        <!-- 左侧导航栏 -->
        <el-aside width="200px" class="layout-aside">
          <Sidebar />
        </el-aside>

        <!-- 右侧内容区 -->
        <el-main class="layout-main">
          <router-view />
        </el-main>
      </el-container>
    </el-container>

    <!-- AI 悬浮球 -->
    <AIFloatButton />
  </div>
</template>

<script setup>
import Sidebar from '@/components/Layout/Sidebar.vue'
import Header from '@/components/Layout/Header.vue'
import AIFloatButton from '@/components/AIFloatButton.vue'
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.layout-header {
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
  padding: 0 20px;
}

.layout-aside {
  background-color: #304156;
  color: #fff;
  height: calc(100vh - 60px);
  overflow-y: auto;
}

.layout-main {
  background-color: #f5f7fa;
  height: calc(100vh - 60px);
  overflow-y: auto;
  padding: 0;
}
</style>
