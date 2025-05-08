<template>
  <div class="create-selection-view">
    <AppHeader />
    <main class="selection-container">
      <h1 class="page-title">内容管理</h1>
      <div class="selection-buttons">
        <el-card 
          class="selection-card create-card" 
          shadow="hover"
          @click="$router.push('/create/question')"
        >
          <div class="card-content">
            <el-icon class="card-icon"><Document /></el-icon>
            <h2>新建题目</h2>
            <p>创建新的算法题目</p>
          </div>
        </el-card>
        
        <el-card 
          class="selection-card update-card" 
          shadow="hover"
          @click="$router.push('/questions/update')"
        >
          <div class="card-content">
            <el-icon class="card-icon"><Refresh /></el-icon>
            <h2>更新题目</h2>
            <p>修改已有题目内容</p>
          </div>
        </el-card>
        
        <el-card 
          class="selection-card solution-card" 
          shadow="hover"
          @click="$router.push('/create/solution')"
        >
          <div class="card-content">
            <el-icon class="card-icon"><Edit /></el-icon>
            <h2>新建题解</h2>
            <p>为题目添加解题方案</p>
          </div>
        </el-card>
      </div>
    </main>
  </div>
</template>

<script>
import AppHeader from '@/components/AppHeader.vue'
import { Document, Refresh, Edit } from '@element-plus/icons-vue'

export default {
  name: 'CreateSelectionView',
  components: {
    AppHeader,
    Document,
    Refresh,
    Edit
  }
}
</script>

<style scoped>
.create-selection-view {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
}

.selection-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-title {
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 2rem;
  font-weight: 600;
  text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
}

.selection-buttons {
  display: flex;
  justify-content: center;
  gap: 30px;
  width: 100%;
  flex-wrap: wrap;
}

.selection-card {
  flex: 1;
  min-width: 280px;
  max-width: 320px;
  height: 240px;
  border-radius: 12px;
  border: none;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.1);
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(5px);
}

.selection-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
}

.card-content {
  padding: 30px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
  justify-content: center;
}

.card-icon {
  font-size: 3.5rem;
  margin-bottom: 1.5rem;
  padding: 15px;
  border-radius: 50%;
}

.create-card .card-icon {
  color: #409EFF;
  background: rgba(64, 158, 255, 0.1);
}

.update-card .card-icon {
  color: #E6A23C;
  background: rgba(230, 162, 60, 0.1);
}

.solution-card .card-icon {
  color: #67C23A;
  background: rgba(103, 194, 58, 0.1);
}

h2 {
  margin: 0.5rem 0;
  color: #34495e;
  font-size: 1.4rem;
  font-weight: 600;
}

p {
  color: #7f8c8d;
  margin: 0;
  font-size: 0.95rem;
  text-align: center;
  line-height: 1.5;
}

@media (max-width: 900px) {
  .selection-buttons {
    flex-direction: column;
    align-items: center;
  }
  .selection-card {
    width: 100%;
    max-width: 400px;
  }
}
</style>