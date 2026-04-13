<template>
  <div class="page">
    <div class="page-header">
      <h2>用户管理</h2>
      <p>创建和管理系统用户</p>
    </div>
    <div class="card">
      <div class="card-header" style="display: flex; justify-content: space-between; align-items: center;">
        <span>用户列表</span>
        <el-button type="primary" @click="openUserDialog()" icon="Plus">新建用户</el-button>
      </div>
      <div class="card-body">
        <!-- 数据表格 -->
        <el-table :data="users" stripe v-loading="loading">
          <el-table-column prop="id" label="ID" width="60"></el-table-column>
          <el-table-column prop="username" label="用户名" width="120"></el-table-column>
          <el-table-column prop="real_name" label="姓名" width="120"></el-table-column>
          <el-table-column prop="role" label="角色" width="100">
            <template #default="scope">
              <span :class="['role-tag', 'role-' + scope.row.role]">{{ roleText(scope.row.role) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="180"></el-table-column>
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="scope">
              <div class="action-cell">
                <el-button type="primary" size="small" @click="openUserDialog(scope.row)">编辑</el-button>
                <el-button type="danger" size="small" @click="deleteUser(scope.row)" v-if="scope.row.username !== currentUser.username">删除</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 用户编辑/新增弹窗 -->
    <el-dialog v-model="userDialogVisible" :title="userForm.id ? '编辑用户' : '新建用户'" width="500px">
      <el-form :model="userForm" label-width="100px">
        <el-form-item label="用户名">
          <el-input v-model="userForm.username" :disabled="!!userForm.id" placeholder="用户名"></el-input>
        </el-form-item>
        <el-form-item label="密码" :required="!userForm.id">
          <el-input v-model="userForm.password" type="password" :placeholder="userForm.id ? '留空则不修改' : '请输入密码'"></el-input>
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="userForm.real_name" placeholder="真实姓名"></el-input>
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="userForm.role" style="width: 100%">
            <el-option label="管理员" value="admin"></el-option>
            <el-option label="操作员" value="operator"></el-option>
            <el-option label="财务" value="finance"></el-option>
            <el-option label="客户" value="customer"></el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="userDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveUser" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const saving = ref(false)
const users = ref([])
const userDialogVisible = ref(false)
const currentUser = ref({})

const userForm = reactive({ id: null, username: '', password: '', role: 'customer', real_name: '' })

const roleText = (role) => {
  const map = { 'admin': '管理员', 'operator': '操作员', 'finance': '财务', 'customer': '客户' }
  return map[role] || role
}

// 加载用户列表
const fetchUsers = async () => {
  loading.value = true
  try {
    const res = await fetch('http://127.0.0.1:8000/api/users')
    users.value = await res.json()
  } catch (e) { ElMessage.error('加载用户失败') }
  loading.value = false
}

// 打开弹窗
const openUserDialog = (row = null) => {
  if (row) { Object.assign(userForm, row); userForm.password = '' }
  else { Object.assign(userForm, { id: null, username: '', password: '', role: 'customer', real_name: '' }) }
  userDialogVisible.value = true
}

// ✅ 修复后的保存用户 (加入 operator)
const saveUser = async () => {
  if (!userForm.username) return ElMessage.warning('请填写用户名')
  if (!userForm.id && !userForm.password) return ElMessage.warning('新建用户必须设置密码')
  
  saving.value = true
  try {
    const url = userForm.id ? `/api/users/${userForm.id}` : '/api/users'
    const method = userForm.id ? 'PUT' : 'POST'
    
    const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
    const payload = {
      ...userForm,
      operator: userInfo.username || 'system',
      user_role: userInfo.role || 'system'
    }
    
    const res = await fetch(`http://127.0.0.1:8000${url}`, {
      method: method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    
    if (res.ok) {
      ElMessage.success(userForm.id ? '更新成功' : '创建成功')
      userDialogVisible.value = false
      fetchUsers()
    } else {
      const result = await res.json()
      ElMessage.error(result.detail || '操作失败')
    }
  } catch (e) { ElMessage.error('网络错误') }
  saving.value = false
}

// ✅ 修复后的删除用户 (加入 operator)
const deleteUser = (row) => {
  ElMessageBox.confirm(`确定删除用户 ${row.username} 吗？`, '警告', { type: 'warning' }).then(async () => {
    try {
      const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
      const res = await fetch(`http://127.0.0.1:8000/api/users/${row.id}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          operator: userInfo.username || 'system',
          user_role: userInfo.role || 'system',
          reason: '手动删除'
        })
      })
      if (res.ok) { ElMessage.success('删除成功'); fetchUsers() }
      else ElMessage.error('删除失败')
    } catch (e) { ElMessage.error('网络错误') }
  })
}

onMounted(() => {
  currentUser.value = JSON.parse(localStorage.getItem('userInfo') || '{}')
  fetchUsers()
})
</script>

<style scoped>
.page { animation: fadeIn 0.4s; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
.page-header { margin-bottom: 32px; }
.page-header h2 { font-size: 32px; font-weight: 700; color: #1c1c1e; margin-bottom: 8px; }
.page-header p { color: #8E8E93; font-size: 16px; }
.card { background: rgba(255,255,255,0.9); backdrop-filter: blur(20px); border-radius: 20px; box-shadow: 0 8px 32px rgba(0,0,0,0.08); border: 1px solid rgba(255,255,255,0.6); overflow: hidden; }
.card-header { padding: 24px 28px; border-bottom: 1px solid rgba(0,0,0,0.06); font-size: 18px; font-weight: 700; color: #1c1c1e; background: linear-gradient(135deg, rgba(0,122,255,0.03) 0%, rgba(88,86,214,0.03) 100%); }
.card-body { padding: 32px; }
.action-cell { display: flex; gap: 8px; }
.role-tag { display: inline-block; padding: 4px 10px; border-radius: 8px; font-size: 11px; font-weight: 700; color: white; }
.role-admin { background: #FF3B30; } .role-operator { background: #FF9500; } .role-finance { background: #34C759; } .role-customer { background: #5856D6; }
:deep(.el-table) { border-radius: 14px; overflow: hidden; }
:deep(.el-table__header-wrapper th) { background: linear-gradient(135deg, rgba(0,122,255,0.05) 0%, rgba(88,86,214,0.05) 100%); font-weight: 700; font-size: 13px; }
:deep(.el-button--primary) { background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%) !important; border: none !important; border-radius: 12px !important; }
</style>