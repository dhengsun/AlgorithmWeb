<template>
  <div class="trash-view">
    <AppHeader />
    <main class="trash-container">
      <h1 class="page-title">回收站</h1>
      <div class="selection-buttons">
        <el-card 
          class="selection-card trash-card" 
          shadow="hover"
          @click="$router.push('/problems/trash')"
        >
          <div class="card-content">
            <el-icon class="card-icon"><Delete /></el-icon>
            <h2>题目回收站</h2>
            <p>管理已删除的题目</p>
          </div>
        </el-card>

        <el-card 
          class="selection-card solution-card" 
          shadow="hover"
          @click="$router.push('/solutions/trash')"
        >
          <div class="card-content">
            <el-icon class="card-icon"><Document /></el-icon>
            <h2>题解回收站</h2>
            <p>管理已删除的题解</p>
          </div>
        </el-card>

        <el-card 
          class="selection-card draft-card" 
          shadow="hover"
          @click="$router.push('/drafts/trash')"
        >
          <div class="card-content">
            <el-icon class="card-icon"><EditPen /></el-icon>
            <h2>草稿回收站</h2>
            <p>管理已删除的草稿</p>
          </div>
        </el-card>
      </div>
    </main>
  </div>
</template>

<script>
import AppHeader from '@/components/AppHeader.vue'
import { Delete, Document, EditPen } from '@element-plus/icons-vue'

export default {
  name: 'TrashView',
  components: {
    AppHeader,
    Delete,
    Document,
    EditPen
  }
}
</script>

<style scoped>
.trash-view {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
}

.trash-container {
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
  width: 100%;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 24px;
}

.selection-card {
  width: 300px;
  height: 240px;
  border-radius: 12px;
  border: none;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.1);
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(5px);
  cursor: pointer;
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

.trash-card .card-icon {
  color: #F56C6C;
  background: rgba(245, 108, 108, 0.1);
}

.solution-card .card-icon {
  color: #409EFF;
  background: rgba(64, 158, 255, 0.1);
}

.draft-card .card-icon {
  color: #E6A23C;
  background: rgba(230, 162, 60, 0.1);
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

@media (max-width: 1024px) {
  .selection-card {
    width: 280px;
    height: 220px;
  }
}

@media (max-width: 768px) {
  .selection-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .selection-card {
    width: 100%;
    max-width: 400px;
    height: 200px;
  }
  
  .page-title {
    font-size: 2rem;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 1.8rem;
  }
  
  .card-icon {
    font-size: 3rem;
    padding: 12px;
  }
  
  h2 {
    font-size: 1.3rem;
  }
}
</style>