<template>
  <div class="not-found">
    <!-- 移除了AppHeader -->
    <main class="container">
      <div class="not-found-content">
        <div class="error-icon-container">
          <el-icon class="error-icon"><warning /></el-icon>
        </div>
        <h1 class="error-code">404</h1>
        <p class="error-message">哎呀，您访问的页面走丢了</p>
        <p class="error-description">该页面可能已被删除或暂时不可用</p>
        <div class="action-buttons">
          <el-button type="primary" size="large" @click="goBack">返回</el-button>
          <el-button size="large" @click="goHome">回到首页</el-button>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { Warning } from '@element-plus/icons-vue'

export default {
  name: 'NotFoundView',
  components: {
    Warning
  },
  methods: {
    // 根据登录状态决定返回行为
    goBack() {
      // 如果有上一个页面，返回上一个页面
      if (window.history.length > 1) {
        this.$router.go(-1)
      } else {
        this.goHome() // 没有历史记录则按主页处理
      }
    },
    // 根据登录状态返回主页或登录页
    goHome() {
      const token = localStorage.getItem('access_token')
      if (token) {
        this.$router.push('/')  // 已登录，返回主页
      } else {
        this.$router.push('/login')  // 未登录，返回登录页
      }
    }
  },
  created() {
    // 设置元数据，标记为不需要导航栏
    this.$route.meta.hideHeader = true
  }
}
</script>

<style scoped>
.not-found {
  min-height: 100vh;
  background-color: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: center;
  /* 添加背景图案使界面不那么单调 */
  background-image: 
    radial-gradient(circle at 10% 20%, rgba(216, 241, 230, 0.46) 0%, rgba(233, 226, 226, 0.28) 90.1%),
    url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M11 18c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm48 25c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm-43-7c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm63 31c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM34 90c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm56-76c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM12 86c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm28-65c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm23-11c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-6 60c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm29 22c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zM32 63c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm57-13c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-9-21c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM60 91c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM35 41c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM12 60c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2z' fill='%239C92AC' fill-opacity='0.1' fill-rule='evenodd'/%3E%3C/svg%3E");
}

.container {
  width: 100%;
  max-width: 1200px;
  padding: 20px;
  margin: 0 auto;
}

.not-found-content {
  background-color: white;
  border-radius: 12px;
  padding: 40px;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  max-width: 600px;
  margin: 0 auto;
  animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.error-icon-container {
  margin-bottom: 20px;
}

.error-icon {
  font-size: 80px;
  color: #f56c6c;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.1); }
  100% { transform: scale(1); }
}

.error-code {
  font-size: 72px;
  font-weight: 700;
  margin: 0;
  background: linear-gradient(45deg, #f56c6c, #e6a23c);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 10px;
}

.error-message {
  font-size: 24px;
  color: #303133;
  margin-bottom: 16px;
  font-weight: 500;
}

.error-description {
  color: #606266;
  margin-bottom: 30px;
  font-size: 16px;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 16px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .not-found-content {
    padding: 30px 20px;
  }
  
  .error-code {
    font-size: 60px;
  }
  
  .error-message {
    font-size: 20px;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 10px;
  }
}
</style>