import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

console.log('Vue应用初始化开始')

const app = createApp(App)

// 注册插件
app.use(ElementPlus)
app.use(router)

// 添加错误处理
app.config.errorHandler = (err, vm, info) => {
  console.error('Vue错误:', err)
  console.error('错误信息:', info)
}

console.log('挂载Vue应用到#app元素')
app.mount('#app')
console.log('Vue应用挂载完成')
