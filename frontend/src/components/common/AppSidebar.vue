<template>
  <el-aside width="220px" class="app-sidebar">
    <el-menu
      :default-active="activeMenu"
      router
      class="sidebar-menu"
      background-color="#304156"
      text-color="#bfcbd9"
      active-text-color="#409eff"
    >
      <el-menu-item index="/dashboard">
        <el-icon><Odometer /></el-icon>
        <span>控制台</span>
      </el-menu-item>
      
      <el-menu-item index="/params">
        <el-icon><Collection /></el-icon>
        <span>参数管理</span>
      </el-menu-item>
      
      <el-menu-item v-if="authStore.isAdmin" index="/users">
        <el-icon><User /></el-icon>
        <span>用户管理</span>
      </el-menu-item>
      
      <el-menu-item index="/profile">
        <el-icon><Setting /></el-icon>
        <span>个人设置</span>
      </el-menu-item>
    </el-menu>
  </el-aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { Odometer, Collection, User, Setting } from '@element-plus/icons-vue'

const route = useRoute()
const authStore = useAuthStore()

const activeMenu = computed(() => route.path)
</script>

<style scoped>
.app-sidebar {
  background-color: #304156;
  min-height: 100vh;
}

.sidebar-menu {
  border-right: none;
}
</style>
