<template>
  <div class="params-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>参数管理</span>
          <el-button type="primary" :icon="Plus">新增参数</el-button>
        </div>
      </template>
      <p>参数管理功能开发中...</p>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { Plus } from '@element-plus/icons-vue'
</script>

<style scoped>
.params-view {
  padding: 10px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
