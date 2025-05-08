<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <h2>登录</h2>
        <p class="subtitle" v-if="loginForm.username">欢迎 {{ loginForm.username }}</p>
        <p class="subtitle" v-else>请输入您的用户名和密码</p>
      </div>
      <el-form 
        :model="loginForm" 
        ref="loginFormRef" 
        :rules="rules"
        class="login-form">
        <el-form-item prop="username">
          <el-input 
            v-model="loginForm.username"
            placeholder="用户名"
            size="large">
            <template #prefix>
              <el-icon class="input-icon"><el-icon-user /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item prop="password">
          <el-input 
            v-model="loginForm.password"
            type="password"
            placeholder="密码"
            size="large"
            show-password>
            <template #prefix>
              <el-icon class="input-icon"><el-icon-lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button 
            type="primary" 
            :loading="loading"
            size="large"
            class="login-button"
            @click="handleLogin">
            登录
          </el-button>
        </el-form-item>
      </el-form>
      <div class="register-link">
        <a href="javascript:void(0)" @click="goToRegister">马上注册</a>
      </div>
    </div>
  </div>
</template>

<script>
import { ElMessage } from 'element-plus'
import { User as ElIconUser, Lock as ElIconLock } from '@element-plus/icons-vue'
import { login } from '@/api/auth'

export default {
  name: 'LoginView',
  components: {
    ElIconUser,
    ElIconLock
  },
  data() {
    return {
      loginForm: {
        username: '',
        password: ''
      },
      loading: false,
      rules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' }
        ]
      }
    }
  },
  created() {
    console.log('LoginView组件已创建')
  },
  methods: {
    async handleLogin() {
      if (!this.$refs.loginFormRef) return
      
      try {
        await this.$refs.loginFormRef.validate()
        this.loading = true
        
        const response = await login(this.loginForm)
        console.log('登录响应:', response.data)

        // 存储 token 和用户信息
        localStorage.setItem('access_token', response.data.access)
        localStorage.setItem('refresh_token', response.data.refresh)
        localStorage.setItem('user_info', JSON.stringify(response.data.user))

        ElMessage.success('登录成功')
        this.$router.push('/')
      } catch (error) {
        console.error('登录错误:', error)
        ElMessage.error(error.response?.data?.detail || '登录失败')
      } finally {
        this.loading = false
      }
    },
    
    goToRegister() {
      this.$router.push('/register')
    }
  }
}
</script>

<style scoped>
.login-container {
  position: relative;
  height: 100vh;
  width: 100vw;
  display: flex;
  justify-content: center;
  align-items: center;
  background-image: url('../assets/auth.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  overflow: hidden;
}

.login-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  z-index: 1;
}

.login-box {
  position: relative;
  width: 450px;
  padding: 40px;
  border-radius: 12px;
  background: rgba(33, 33, 38, 0.8);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  z-index: 2;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h2 {
  font-size: 28px;
  font-weight: 600;
  color: #ffffff;
  margin-bottom: 8px;
}

.subtitle {
  font-size: 16px;
  color: #e1e1e1;
  margin-bottom: 20px;
  min-height: 24px;
  transition: all 0.3s ease;
}

.login-form {
  margin-top: 20px;
}

.login-button {
  width: 100%;
  margin-top: 10px;
  padding: 12px 0;
  font-size: 16px;
  border-radius: 6px;
  background: #409EFF;
  border-color: #409EFF;
}

.input-icon {
  color: #909399;
  font-size: 18px;
}

/* 登录框内输入框样式 */
:deep(.el-input__wrapper) {
  background-color: rgba(255, 255, 255, 0.1);
  box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.1) inset;
}

:deep(.el-input__inner) {
  color: #ffffff;
}

:deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.6);
}

/* 输入框悬停样式 */
:deep(.el-input:hover .el-input__wrapper) {
  box-shadow: 0 0 0 1px #409EFF inset;
}

/* 按钮悬停样式 */
.login-button:hover {
  background-color: #66b1ff;
  border-color: #66b1ff;
  color: #fff;
}

.register-link {
  text-align: center;
  margin-top: 20px;
  color: #ccc;
  font-size: 14px;
}

.register-link a {
  color: #409EFF;
  text-decoration: none;
  transition: color 0.3s ease;
}

.register-link a:hover {
  color: #66b1ff;
  text-decoration: underline;
}

/* 响应式设计 */
@media screen and (max-width: 768px) {
  .login-box {
    width: 90%;
    max-width: 450px;
    padding: 30px;
  }
}
</style>
