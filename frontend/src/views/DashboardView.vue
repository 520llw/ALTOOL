<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>参数总数</span>
              <el-icon><Collection /></el-icon>
            </div>
          </template>
          <div class="card-value">{{ stats.paramCount }}</div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>分类数量</span>
              <el-icon><FolderOpened /></el-icon>
            </div>
          </template>
          <div class="card-value">{{ stats.categoryCount }}</div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>器件类型</span>
              <el-icon><Cpu /></el-icon>
            </div>
          </template>
          <div class="card-value">{{ stats.deviceTypeCount }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-20">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>欢迎使用 AITOOL</span>
            </div>
          </template>
          <div class="welcome-content">
            <p>AITOOL 是一个智能参数提取工具，支持从 PDF 数据手册中自动提取半导体器件参数。</p>
            <p>当前版本：v2.0.0</p>
            <p>后端 API：/api/v1</p>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Collection, FolderOpened, Cpu } from '@element-plus/icons-vue'
import * as paramApi from '@/api/param'

const stats = ref({
  paramCount: 0,
  categoryCount: 0,
  deviceTypeCount: 0
})

onMounted(async () => {
  try {
    const [paramsRes, categoriesRes, deviceTypesRes] = await Promise.all([
      paramApi.getParams(0, 1),
      paramApi.getCategories(),
      paramApi.getDeviceTypes()
    ])
    stats.value.paramCount = paramsRes.total
    stats.value.categoryCount = categoriesRes.items.length
    stats.value.deviceTypeCount = deviceTypesRes.items.length
  } catch (error) {
    // 静默处理
  }
})
</script>

<style scoped>
.dashboard {
  padding: 10px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  color: #606266;
}

.card-value {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
  text-align: center;
  padding: 20px 0;
}

.mt-20 {
  margin-top: 20px;
}

.welcome-content {
  line-height: 2;
  color: #606266;
}

.welcome-content p {
  margin: 8px 0;
}
</style>
