<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-logo">
        <h1>📦 Logistics Pro</h1>
        <p>物流管理系统</p>
      </div>
      <el-form :model="loginForm">
        <el-form-item>
          <el-input 
            v-model="loginForm.username" 
            placeholder="用户名" 
            prefix-icon="User" 
            size="large" 
            @keyup.enter="handleLogin"
          ></el-input>
        </el-form-item>
        <el-form-item>
          <el-input 
            v-model="loginForm.password" 
            type="password" 
            placeholder="密码" 
            prefix-icon="Lock" 
            size="large" 
            @keyup.enter="handleLogin"
          ></el-input>
        </el-form-item>
        <el-form-item>
          <el-button 
            type="primary" 
            class="login-btn" 
            @click="handleLogin" 
            :loading="loginLoading"
          >
            {{ loginLoading ? '登录中...' : '登 录' }}
          </el-button>
        </el-form-item>
      </el-form>
      <div style="text-align: center; color: #8E8E93; font-size: 13px; margin-top: 20px;">
        默认账号：admin / 123456
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const loginLoading = ref(false)
const loginForm = reactive({ username: '', password: '' })

const handleLogin = async () => {
  if (!loginForm.username || !loginForm.password) {
    return ElMessage.warning('请输入用户名和密码')
  }
  loginLoading.value = true
  
  try {
    const res = await fetch('http://127.0.0.1:8000/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(loginForm)
    })
    const result = await res.json()
    
    if (res.ok) {
      localStorage.setItem('token', 'fake-token')
      localStorage.setItem('userRole', result.user.role)
      localStorage.setItem('userInfo', JSON.stringify(result.user))
      ElMessage.success(`欢迎，${result.user.real_name}`)
      router.push('/forecast')
    } else {
      ElMessage.error(result.detail || '登录失败')
    }
  } catch (e) {
    ElMessage.error('无法连接服务器，请检查后端是否启动')
  }
  loginLoading.value = false
}
</script>

<style scoped>
.login-container {
  display: flex; 
  align-items: center; 
  justify-content: center; 
  min-height: 100vh;
}
.login-card {
  background: rgba(255, 255, 255, 0.9); 
  backdrop-filter: blur(20px);
  border-radius: 24px; 
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  padding: 48px 40px; 
  width: 100%; 
  max-width: 440px;
  animation: slideUp 0.5s;
}
@keyframes slideUp { 
  from { opacity: 0; transform: translateY(30px); } 
  to { opacity: 1; transform: translateY(0); } 
}
.login-logo { text-align: center; margin-bottom: 40px; }
.login-logo h1 { 
  font-size: 32px; 
  font-weight: 700; 
  color: #007AFF; 
  margin-bottom: 8px; 
}
.login-logo p { color: #8E8E93; font-size: 15px; }
.login-btn {
  width: 100%; 
  height: 50px;
  background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%);
  border: none; 
  border-radius: 14px; 
  font-size: 17px; 
  font-weight: 600; 
  color: white;
}
</style>