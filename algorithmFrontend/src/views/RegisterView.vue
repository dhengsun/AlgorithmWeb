<template>
  <div class="register-container">
    <div class="register-box">
      <div class="register-header">
        <h2>注册</h2>
        <p class="subtitle" v-if="registerForm.username">欢迎 {{ registerForm.username }}</p>
        <p class="subtitle" v-else>请创建您的账号</p>
      </div>
      <el-form 
        :model="registerForm" 
        ref="registerFormRef" 
        :rules="rules"
        class="register-form">
        <el-form-item prop="username">
          <el-input 
            v-model="registerForm.username"
            placeholder="用户名"
            size="large">
            <template #prefix>
              <el-icon class="input-icon"><el-icon-user /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item prop="password">
          <el-input 
            v-model="registerForm.password"
            type="password"
            placeholder="密码"
            size="large"
            show-password>
            <template #prefix>
              <el-icon class="input-icon"><el-icon-lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item prop="confirmPassword">
          <el-input 
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="确认密码"
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
            class="register-button"
            @click="handleRegister">
            注册
          </el-button>
        </el-form-item>
      </el-form>
      <div class="login-link">
        <a href="javascript:void(0)" @click="goToLogin">返回登录</a>
      </div>
    </div>
  </div>
</template>

<script>
import { ElMessage } from 'element-plus'
import { User as ElIconUser, Lock as ElIconLock } from '@element-plus/icons-vue'
import { register } from '@/api/auth'

export default {
  name: 'RegisterView',
  components: {
    ElIconUser,
    ElIconLock
  },
  data() {
    // 确认密码验证函数
    const validateConfirmPassword = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请再次输入密码'))
      } else if (value !== this.registerForm.password) {
        callback(new Error('两次输入密码不一致'))
      } else {
        callback()
      }
    }
    
    return {
      registerForm: {
        username: '',
        password: '',
        confirmPassword: ''
      },
      loading: false,
      rules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { min: 3, max: 20, message: '用户名长度应为3-20个字符', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, message: '密码长度至少为6个字符', trigger: 'blur' }
        ],
        confirmPassword: [
          { required: true, message: '请确认密码', trigger: 'blur' },
          { validator: validateConfirmPassword, trigger: 'blur' }
        ]
      }
    }
  },
  created() {
    console.log('RegisterView组件已创建')
  },
  methods: {
    async handleRegister() {
      if (!this.$refs.registerFormRef) return
      
      try {
        await this.$refs.registerFormRef.validate()
        this.loading = true
        
        // 调用注册API
        const response = await register({
          username: this.registerForm.username,
          password: this.registerForm.password
        })
        
        console.log('注册响应:', response.data)
        
        ElMessage.success('注册成功，请登录')
        // 注册成功后跳转到登录页面
        this.$router.push('/login')
      } catch (error) {
        console.error('注册错误:', error)
        ElMessage.error(error.response?.data?.detail || '注册失败')
      } finally {
        this.loading = false
      }
    },
    
    goToLogin() {
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
.register-container {
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

.register-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  z-index: 1;
}

.register-box {
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

.register-header {
  text-align: center;
  margin-bottom: 30px;
}

.register-header h2 {
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

.register-form {
  margin-top: 20px;
}

.register-button {
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
.register-button:hover {
  background-color: #66b1ff;
  border-color: #66b1ff;
  color: #fff;
}

.login-link {
  text-align: center;
  margin-top: 20px;
  color: #ccc;
  font-size: 14px;
}

.login-link a {
  color: #409EFF;
  text-decoration: none;
  transition: color 0.3s ease;
}

.login-link a:hover {
  color: #66b1ff;
  text-decoration: underline;
}

/* 响应式设计 */
@media screen and (max-width: 768px) {
  .register-box {
    width: 90%;
    max-width: 450px;
    padding: 30px;
  }
}
</style> 