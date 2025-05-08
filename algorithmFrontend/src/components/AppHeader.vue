<template>
  <div class="header-container">
    <!-- 右上角用户区域 -->
    <div class="user-area">
      <el-dropdown trigger="click" @command="handleCommand">
        <div class="user-info">
          <el-icon><User /></el-icon>
          <span>{{ username }}</span>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="logout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
    
    <!-- 侧边导航栏 -->
    <div class="side-nav">
      <div class="nav-header">
        <div class="logo-container" @click="$router.push('/')">
          <img class="logo" src="@/assets/logo.png" alt="Logo">
        </div>
      </div>

      <div class="nav-menu">
        <div 
          class="nav-item" 
          :class="{ active: $route.path === '/create' }"
          @click="$router.push('/create')"
        >
          <el-icon><EditPen /></el-icon>
          <span class="item-label">编辑</span>
          <div class="tooltip">创建题目或题解</div>
        </div>

        <div 
          class="nav-item" 
          :class="{ active: $route.path === '/problems' }"
          @click="$router.push('/problems')"
        >
          <el-icon><Collection /></el-icon>
          <span class="item-label">题库</span>
          <div class="tooltip">浏览所有题目</div>
        </div>

        <div 
          class="nav-item" 
          :class="{ active: $route.path === '/solutions' }"
          @click="$router.push('/solutions')"
        >
          <el-icon><Reading /></el-icon>
          <span class="item-label">题解</span>
          <div class="tooltip">查看解题思路</div>
        </div>

        <div 
          class="nav-item" 
          :class="{ active: $route.path === '/drafts' }"
          @click="$router.push('/drafts')"
        >
          <el-icon><Document /></el-icon>
          <span class="item-label">草稿</span>
          <div class="tooltip">临时保存草稿</div>
        </div>

        <div 
          class="nav-item" 
          :class="{ active: $route.path === '/trash' }"
          @click="$router.push('/trash')"
        >
          <el-icon><Delete /></el-icon>
          <span class="item-label">回收站</span>
          <div class="tooltip">已删除的内容</div>
        </div>
      </div>
    </div>
  </div>
</template>


<script>
import { 
  EditPen, 
  Collection, 
  Reading, 
  Document,
  User,
  Delete 
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

export default {
  name: 'AppHeader',
  components: {
    EditPen,
    Collection,
    Reading,
    Document,
    User,
    Delete
  },
  data() {
    return {
      username: '用户'
    }
  },
  created() {
    const userInfoStr = localStorage.getItem('user_info')
    if (userInfoStr) {
      try {
        const userInfo = JSON.parse(userInfoStr)
        this.username = userInfo.username || '用户'
      } catch (e) {
        console.error('解析用户信息失败:', e)
      }
    }
  },
  methods: {
    handleCommand(command) {
      if (command === 'logout') {
        this.handleLogout()
      }
    },
    handleLogout() {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user_info')
      
      ElMessage.success('已退出登录')
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
.header-container {
  padding: 0;
  margin: 0;
  position: relative;
}

.side-nav {
  position: fixed;
  left: 0;
  top: 0; /* 确保完全从顶部开始 */
  bottom: 0;
  width: 60px;
  background: #2c2c2c;
  color: #fff;
  display: flex;
  flex-direction: column;
  z-index: 100;
  padding: 0; /* 移除所有内边距 */
  margin: 0; /* 移除所有边距 */
}

.nav-header {
  padding: 16px 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  margin: 0; /* 确保没有外边距 */
}

.logo-container {
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  margin: 0; /* 确保没有外边距 */
}

.logo {
  height: 36px;
  width: 36px;
}

.nav-menu {
  flex: 1;
  padding: 16px 0;
  margin: 0; /* 确保没有外边距 */
}

.nav-item {
  padding: 16px 0;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  color: rgba(255, 255, 255, 0.7);
  transition: all 0.3s;
  margin: 0; /* 确保没有外边距 */
}

.nav-item:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.1);
}

.nav-item.active {
  color: #fff;
  background: rgba(255, 255, 255, 0.15);
  border-left: 3px solid #fff;
}

.nav-item .el-icon {
  font-size: 24px;
  margin-bottom: 8px;
}

.item-label {
  font-size: 12px;
}

.tooltip {
  position: absolute;
  background: rgba(0, 0, 0, 0.8);
  color: #fff;
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 12px;
  left: 100%;
  top: 50%;
  transform: translateY(-50%);
  white-space: nowrap;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s;
  z-index: 10;
}

.tooltip:before {
  content: "";
  position: absolute;
  left: -6px;
  top: 50%;
  transform: translateY(-50%);
  border-width: 6px 6px 6px 0;
  border-style: solid;
  border-color: transparent rgba(0, 0, 0, 0.8) transparent transparent;
}

.nav-item:hover .tooltip {
  opacity: 1;
  visibility: visible;
  left: calc(100% + 10px);
}

/* 用户区域样式 - 浅色方案 */
.user-area {
  position: fixed;
  top: 12px;
  right: 20px;
  display: flex;
  align-items: center;
  z-index: 101;
  margin: 0;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.85);
  color: #333;
  border-radius: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
  border: 1px solid rgba(0, 0, 0, 0.08);
}

.user-info:hover {
  background: #fff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.user-info .el-icon {
  margin-right: 8px;
  color: #666;
  font-size: 16px;
}

.user-info:hover .el-icon {
  color: #409EFF;
}

/* 优化下拉菜单样式 - 浅色方案 */
:deep(.el-dropdown-menu) {
  background-color: #fff;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  margin-top: 8px;
  padding: 4px 0;
}

:deep(.el-dropdown-menu__item) {
  color: #333;
  padding: 10px 20px;
  font-size: 14px;
}

:deep(.el-dropdown-menu__item:hover) {
  background-color: #f6f9ff;
  color: #409EFF;
}

:deep(.el-dropdown-menu__item:focus) {
  background-color: #f6f9ff;
  color: #409EFF;
}

/* 响应式设计 */
@media screen and (max-width: 768px) {
  .item-label {
    font-size: 10px;
  }
  
  .user-info span {
    display: none; /* 在小屏幕上只显示图标 */
  }
  
  .user-info {
    padding: 12px;
  }
  
  .user-info .el-icon {
    margin-right: 0;
  }
}
</style>