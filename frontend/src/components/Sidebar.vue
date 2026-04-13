<template>
  <div class="sidebar">
    <div class="sidebar-header">
      <h1>📦 Logistics Pro</h1>
    </div>
    <nav class="sidebar-menu">
      <RouterLink to="/forecast" class="menu-item" active-class="active">
        <span>📋</span> 客户预报
      </RouterLink>
      <RouterLink to="/orders" class="menu-item" active-class="active">
        <span>📦</span> 订单查询
      </RouterLink>
      <RouterLink to="/bills" class="menu-item" active-class="active">
        <span>💰</span> 账单查询
      </RouterLink>
      <RouterLink to="/business" class="menu-item" active-class="active">
        <span>🚢</span> 业务信息
      </RouterLink>
      <RouterLink to="/customers" class="menu-item" active-class="active">
        <span>👥</span> 客户维护
      </RouterLink>
      
      <!-- ✅ 新增：在库管理 -->
      <RouterLink to="/inventory" class="menu-item" active-class="active">
        <span>🏭</span> 在库管理
      </RouterLink>

      <RouterLink to="/users" class="menu-item" active-class="active" v-if="userRole === 'admin'">
        <span>👨‍💼</span> 用户管理
      </RouterLink>
      <RouterLink to="/logs" class="menu-item" active-class="active" v-if="userRole === 'admin'">
        <span>📜</span> 删除日志
      </RouterLink>
    </nav>
    <div class="sidebar-footer">
      <div class="user-info" v-if="userInfo">
        <div class="user-avatar">{{ userInfo?.real_name?.[0] || 'U' }}</div>
        <div>
          <div style="font-weight: 600">{{ userInfo?.real_name || userInfo?.username }}</div>
          <div :class="['role-tag', 'role-' + (userRole || 'admin')]">{{ roleText(userRole) }}</div>
        </div>
      </div>
      <button class="logout-btn" @click="handleLogout">🚪 退出登录</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'

const router = useRouter()
const userRole = ref('')
const userInfo = ref(null)

const roleText = (role) => {
  const map = { 'admin': '管理员', 'operator': '操作员', 'finance': '财务', 'customer': '客户' }
  return map[role] || role
}

const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' })
    .then(() => {
      localStorage.removeItem('token'); localStorage.removeItem('userRole'); localStorage.removeItem('userInfo')
      router.push('/')
    })
}

onMounted(() => {
  userRole.value = localStorage.getItem('userRole') || ''
  const info = localStorage.getItem('userInfo')
  if (info) userInfo.value = JSON.parse(info)
})
</script>

<style scoped>
.sidebar {
  width: 260px; min-width: 220px;
  background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(20px);
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.08);
  position: fixed;  left: 0; top: 0; bottom: 0; z-index: 1000;
  display: flex; flex-direction: column; transition: width 0.3s ease;
}
.sidebar-header { padding: 32px 24px; border-bottom: 1px solid rgba(0,0,0,0.06); }
.sidebar-header h1 { font-size: 24px; font-weight: 700; color: #007AFF; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.sidebar-menu { flex: 1;  padding: 20px 16px; overflow-y: auto; overflow-x: hidden; }
.menu-item {
  padding: 14px 18px; margin-bottom: 8px; border-radius: 12px;
  display: flex; align-items: center; gap:  14px;
  font-size: 15px; font-weight: 500; color: #3a3a3c;
  text-decoration: none; transition: all 0.2s; white-space: nowrap;
}
.menu-item:hover { background: rgba(0,122,255,0.08) ; color: #007AFF; }
.menu-item.active { background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%); color: white; box-shadow: 0 4px 15px rgba(0,122,255,0.3); }
.sidebar-footer {  padding: 24px; border-top: 1px solid rgba(0,0,0,0.06); }
.user-info { display: flex; align-items: center; gap: 14px; padding: 16px; background: rgba(255,255,255,0.8); border-radius: 14px; margin-bottom: 14px; }
.user-avatar { width: 48px; height: 48px; border-radius: 50%; background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%); display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: 20px; flex-shrink: 0; }
.role-tag { display: inline-block; padding: 4px 10px; border-radius: 8px; font-size: 11px; font-weight: 700; color: white; }
.role-admin { background: #FF3B30; } .role-operator { background: #FF9500; } .role-finance { background: #34C759; } .role-customer  { background: #5856D6; }
.logout-btn { width: 100%; padding: 12px; border-radius: 12px; border: 1px solid rgba(0,0,0,0.1); background: transparent; cursor: pointer; font-size: 15px; font-weight: 600; color: #8E8E93; transition: all 0.3s; }
.logout-btn:hover { background: #FF3B30; color: white; border-color: transparent; }

/* 响应式 */
@media (max-width: 992px ) {
  .sidebar { width: 220px; }
  .menu-item { padding: 12px 14px; font-size: 14px; gap: 10px; }
  .sidebar-header h1 { font-size: 20px; }
}
@media (max-width: 768px) {
  .sidebar  { position: relative; width: 100%; height: auto; bottom: auto; box-shadow: none; border-bottom: 1px solid rgba(0,0,0,0.1); }
  .sidebar-menu { display: flex; flex-wrap: wrap; gap:  8px; padding: 12px; }
  .menu-item { flex: 1 1 calc(33% - 8px); justify-content: center; padding: 10px; font-size: 13px; }
  .sidebar-footer { display: none; }
}
@media (max-width : 480px) { .menu-item { flex: 1 1 100%; } }
</style>