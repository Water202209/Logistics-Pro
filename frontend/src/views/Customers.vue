<template>
  <div class="page">
    <div class="page-header">
      <h2>客户信息维护</h2>
      <p>管理客户资料</p>
    </div>
    <div class="card">
      <div class="card-header" style="display: flex; justify-content: space-between; align-items: center;">
        <span>客户列表</span>
        <el-button type="primary" @click="openCustomerDialog()" icon="Plus">新建客户</el-button>
      </div>
      <div class="card-body">
        <!-- 搜索栏 -->
        <div class="search-bar" style="margin-bottom: 20px; padding: 16px;">
          <el-input v-model="customerSearch" placeholder="搜索客户名称/公司" prefix-icon="Search" clearable @keyup.enter="fetchCustomers"></el-input>
          <el-button type="primary" @click="fetchCustomers" icon="Search">搜索</el-button>
        </div>

        <!-- 数据表格 -->
        <el-table :data="customers" stripe v-loading="customersLoading" height="500">
          <el-table-column prop="id" label="ID" width="70"></el-table-column>
          <el-table-column prop="customer_name" label="客户名称" min-width="150"></el-table-column>
          <el-table-column prop="company_name" label="公司名称" min-width="180"></el-table-column>
          <el-table-column prop="tax_no" label="税号" width="180"></el-table-column>
          <el-table-column prop="finance_contact" label="财务联系人" width="120"></el-table-column>
          <el-table-column prop="finance_phone" label="财务电话" width="120"></el-table-column>
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="scope">
              <div class="action-cell">
                <el-button type="primary" size="small" @click="openCustomerDialog(scope.row)">编辑</el-button>
                <el-button type="danger" size="small" @click="confirmDeleteCustomer(scope.row)">删除</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 客户编辑/新增弹窗 -->
    <el-dialog v-model="customerDialogVisible" :title="customerForm.id ? '编辑客户' : '新建客户'" width="800px">
      <el-form :model="customerForm" label-width="120px">
        <div class="form-section">
          <div class="form-section-title">📋 基本信息</div>
          <div class="form-row">
            <div class="form-item"><label class="required">客户名称</label><el-input v-model="customerForm.customer_name" placeholder="客户简称"></el-input></div>
            <div class="form-item"><label>税号</label><el-input v-model="customerForm.tax_no" placeholder="纳税人识别号"></el-input></div>
          </div>
          <div class="form-row">
            <div class="form-item"><label>公司名称</label><el-input v-model="customerForm.company_name" placeholder="公司全称"></el-input></div>
            <div class="form-item"><label>银行账号</label><el-input v-model="customerForm.bank_account" placeholder="银行账号"></el-input></div>
          </div>
        </div>
        
        <div class="form-section" style="border: none; margin-bottom: 0;">
          <div class="form-section-title">👤 联系人信息</div>
          <div class="form-row">
            <div class="form-item"><label>财务联系人</label><el-input v-model="customerForm.finance_contact" placeholder="财务负责人"></el-input></div>
            <div class="form-item"><label>业务联系人</label><el-input v-model="customerForm.business_contact" placeholder="业务负责人"></el-input></div>
          </div>
          <div class="form-row">
            <div class="form-item"><label>财务电话</label><el-input v-model="customerForm.finance_phone" placeholder="财务电话"></el-input></div>
            <div class="form-item"><label>业务电话</label><el-input v-model="customerForm.business_phone" placeholder="业务电话"></el-input></div>
          </div>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="customerDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveCustomer" :loading="customerSaving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const customersLoading = ref(false)
const customers = ref([])
const customerSearch = ref('')
const customerDialogVisible = ref(false)
const customerSaving = ref(false)

const customerForm = reactive({
  id: null, customer_name: '', tax_no: '', company_name: '', bank_account: '',
  finance_contact: '', business_contact: '', finance_phone: '', business_phone: ''
})

// ✅ 修复后的加载客户列表
const fetchCustomers = async () => {
  customersLoading.value = true
  try {
    const params = new URLSearchParams()
    if (customerSearch.value) params.append('search', customerSearch.value)
    const res = await fetch(`http://127.0.0.1:8000/api/customers?${params}`)
    const data = await res.json()
    customers.value = Array.isArray(data) ? data : []
  } catch (e) { ElMessage.error('加载客户失败') }
  customersLoading.value = false
}

// ✅ 修复后的保存客户 (加入 operator)
const saveCustomer = async () => {
  if (!customerForm.customer_name) return ElMessage.warning('请填写客户名称')
  
  customerSaving.value = true
  try {
    const url = customerForm.id ? `/api/customers/${customerForm.id}` : '/api/customers'
    const method = customerForm.id ? 'PUT' : 'POST'
    
    // 获取当前操作人信息
    const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
    const payload = {
      ...customerForm,
      operator: userInfo.username || 'system',
      user_role: userInfo.role || 'system'
    }
    
    const res = await fetch(`http://127.0.0.1:8000${url}`, {
      method: method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    
    if (res.ok) {
      ElMessage.success(customerForm.id ? '更新成功' : '创建成功')
      customerDialogVisible.value = false
      fetchCustomers()
    } else {
      const result = await res.json()
      ElMessage.error(result.detail || '操作失败')
    }
  } catch (e) { ElMessage.error('网络错误') }
  customerSaving.value = false
}

// ✅ 修复后的删除客户 (加入 operator)
const confirmDeleteCustomer = (row) => {
  ElMessageBox.confirm(`确定删除客户 ${row.customer_name} 吗？`, '警告', {
    confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning'
  }).then(async () => {
    try {
      const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
      const res = await fetch(`http://127.0.0.1:8000/api/customers/${row.id}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          operator: userInfo.username || 'system',
          user_role: userInfo.role || 'system',
          reason: '手动删除'
        })
      })
      if (res.ok) { ElMessage.success('删除成功'); fetchCustomers() }
      else ElMessage.error('删除失败')
    } catch (e) { ElMessage.error('网络错误') }
  })
}

onMounted(() => { fetchCustomers() })
</script>

<style scoped>
/* 沿用之前的样式 */
.page { animation: fadeIn 0.4s; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
.page-header { margin-bottom: 32px; }
.page-header h2 { font-size: 32px; font-weight: 700; color: #1c1c1e; margin-bottom: 8px; }
.page-header p { color: #8E8E93; font-size: 16px; }
.card { background: rgba(255,255,255,0.9); backdrop-filter: blur(20px); border-radius: 20px; box-shadow: 0 8px 32px rgba(0,0,0,0.08); border: 1px solid rgba(255,255,255,0.6); overflow: hidden; }
.card-header { padding: 24px 28px; border-bottom: 1px solid rgba(0,0,0,0.06); font-size: 18px; font-weight: 700; color: #1c1c1e; background: linear-gradient(135deg, rgba(0,122,255,0.03) 0%, rgba(88,86,214,0.03) 100%); }
.card-body { padding: 32px; }
.search-bar { display: flex; gap: 16px; }
.form-section { margin-bottom: 32px; padding-bottom: 28px; border-bottom: 1px solid rgba(0,0,0,0.06); }
.form-section-title { font-size: 13px; font-weight: 700; color: #007AFF; margin-bottom: 24px; text-transform: uppercase; letter-spacing: 0.8px; }
.form-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 20px; margin-bottom: 20px; }
.form-item label { display: block; margin-bottom: 8px; font-size: 14px; color: #3a3a3c; font-weight: 600; }
.form-item .required::before { content: '*'; color: #FF3B30; margin-right: 4px; }
.action-cell { display: flex; gap: 8px; }
:deep(.el-table) { border-radius: 14px; overflow: hidden; }
:deep(.el-table__header-wrapper th) { background: linear-gradient(135deg, rgba(0,122,255,0.05) 0%, rgba(88,86,214,0.05) 100%); font-weight: 700; font-size: 13px; }
:deep(.el-button--primary) { background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%) !important; border: none !important; border-radius: 12px !important; }
</style>