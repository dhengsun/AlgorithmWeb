<template>
  <div id="main-container">
    <!-- 根据路由meta判断是否显示AppHeader -->
    <AppHeader v-if="!$route.meta.hideHeader" />
    <div class="content-container" :class="{ 'no-header': $route.meta.hideHeader }">
      <router-view></router-view>
    </div>
  </div>
</template>

<script>
import AppHeader from './components/AppHeader.vue'
import { ref, provide } from 'vue'

export default {
  name: 'App',
  components: {
    AppHeader
  },
  setup() {
    const isCollapsed = ref(false)
    provide('isCollapsed', isCollapsed)
    
    return {
      isCollapsed
    }
  },
  mounted() {
    console.log('App组件已挂载')
    
    // 检查登录状态，确保用户已登录
    this.checkAuth()
  },
  methods: {
    // 验证登录状态
    checkAuth() {
      const token = localStorage.getItem('access_token')
      if (!token && this.$route.meta.requiresAuth) {
        this.$router.push('/login')
      }
    }
  },
  errorCaptured(err, vm, info) {
    console.error('App捕获到错误:', err)
    console.error('错误信息:', info)
    return false
  }
}
</script>

<style>
/* 重置所有元素的边距和内边距 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
  /* 移除 overflow: hidden; 允许页面滚动 */
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  height: 100%;
  width: 100%;
  position: relative;
  /* 移除 overflow: hidden; 允许内容滚动 */
}

#main-container {
  height: 100%;
  width: 100%;
  position: relative;
  /* 移除 overflow: hidden; 允许内容滚动 */
}

.content-container {
  margin-left: 60px; /* 与导航栏宽度一致 */
  margin-top: 0; /* 确保顶部没有间隙 */
  padding: 16px; /* 内容区域内边距 */
  min-height: 100%; /* 修改为100%而不是100vh */
  width: calc(100% - 60px); /* 减去导航栏宽度 */
  background-color: #f5f5f5; /* 设置背景色以便于区分 */
  position: relative;
  /* 允许内容区域滚动，但不设置overflow-y: auto */
  
  /* 过渡效果 */
  transition: margin-left 0.3s, width 0.3s;
}

/* 当没有导航栏时的样式 */
.content-container.no-header {
  margin-left: 0;
  width: 100%;
}

/* 移除所有可能的默认边距 */
h1, h2, h3, h4, h5, h6, p, ol, ul, figure, blockquote {
  margin: 0;
  padding: 0;
}
</style>