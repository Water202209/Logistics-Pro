<template>
  <div class="page">
    <div class="page-header">
      <h2>业务信息</h2>
      <p>船期管理与业务跟踪</p>
    </div>
    <div class="card">
      <div class="card-header" style="display: flex; justify-content: space-between; align-items: center;">
        <span>业务列表</span>
        <el-button type="primary" @click="openBusinessDialog()" icon="Plus">新增船期</el-button>
      </div>
      <div class="card-body">
        <!-- 搜索栏 -->
        <div class="search-bar">
          <el-input v-model="bizSearch.business_no" placeholder="业务编号" clearable prefix-icon="Search"></el-input>
          <el-input v-model="bizSearch.container_no" placeholder="集装箱号" clearable></el-input>
          <el-input v-model="bizSearch.bill_no" placeholder="提单号" clearable></el-input>
          <el-select v-model="bizSearch.business_type" placeholder="业务类型" clearable>
            <el-option label="601-代操作" value="601"></el-option>
            <el-option label="602-美国海运 - 美森" value="602"></el-option>
            <el-option label="603-美国海运尾程" value="603"></el-option>
            <el-option label="604-美国空运" value="604"></el-option>
            <el-option label="605-美国空运尾程" value="605"></el-option>
            <el-option label="606-日本海运" value="606"></el-option>
            <el-option label="607-日本空运" value="607"></el-option>
            <el-option label="608-转同行" value="608"></el-option>
            <el-option label="609-账单用" value="609"></el-option>
            <el-option label="610-美国海运 - 普船" value="610"></el-option>
            <el-option label="611-加拿大空海运" value="611"></el-option>
            <el-option label="612-东南亚空海运" value="612"></el-option>
          </el-select>
          <el-button type="primary" @click="fetchBusiness" icon="Search">查询</el-button>
        </div>

        <!-- 数据表格 -->
        <el-table :data="businessList" stripe v-loading="bizLoading" height="500">
          <el-table-column prop="id" label="ID" width="60"></el-table-column>
          <el-table-column prop="business_no" label="业务编号" width="180" sortable></el-table-column>
          <el-table-column prop="business_type_name" label="业务类型" width="160">
            <template #default="scope">
              <el-tag type="info" size="small">{{ scope.row.business_type_name }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="container_no" label="集装箱号" width="140"></el-table-column>
          <el-table-column prop="bill_no" label="提单号" width="140"></el-table-column>
          <el-table-column prop="ship_name" label="船名" width="140"></el-table-column>
          <el-table-column prop="voyage" label="航次" width="100"></el-table-column>
          <el-table-column prop="remark" label="备注" width="200" show-overflow-tooltip></el-table-column>
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="scope">
              <div class="action-cell">
                <el-button type="primary" size="small" @click="openBusinessDialog(scope.row)">编辑</el-button>
                <el-button type="danger" size="small" @click="deleteBusiness(scope.row.id)">删除</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 业务新增/编辑弹窗 -->
    <el-dialog v-model="bizDialogVisible" :title="bizForm.id ? '编辑业务信息' : '新增船期信息'" width="700px">
      <el-form :model="bizForm" label-width="120px">
        <el-form-item label="业务类型" required>
          <el-select v-model="bizForm.business_type" @change="onTypeChange" style="width: 100%" placeholder="请选择业务类型">
            <el-option label="601-代操作" value="601"></el-option>
            <el-option label="602-美国海运 - 美森" value="602"></el-option>
            <el-option label="603-美国海运尾程" value="603"></el-option>
            <el-option label="604-美国空运" value="604"></el-option>
            <el-option label="605-美国空运尾程" value="605"></el-option>
            <el-option label="606-日本海运" value="606"></el-option>
            <el-option label="607-日本空运" value="607"></el-option>
            <el-option label="608-转同行" value="608"></el-option>
            <el-option label="609-账单用" value="609"></el-option>
            <el-option label="610-美国海运 - 普船" value="610"></el-option>
            <el-option label="611-加拿大空海运" value="611"></el-option>
            <el-option label="612-东南亚空海运" value="612"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="业务编号" v-if="!bizForm.id">
          <el-input v-model="bizForm.generated_no" disabled placeholder="保存后自动生成"></el-input>
        </el-form-item>
        <el-form-item label="集装箱号">
          <el-input v-model="bizForm.container_no" placeholder="请输入集装箱号"></el-input>
        </el-form-item>
        <el-form-item label="箱型">
          <el-input v-model="bizForm.container_type" placeholder="如：40HQ"></el-input>
        </el-form-item>
        <el-form-item label="提单号">
          <el-input v-model="bizForm.bill_no" placeholder="请输入提单号"></el-input>
        </el-form-item>
        <el-form-item label="船名">
          <el-input v-model="bizForm.ship_name" placeholder="请输入船名"></el-input>
        </el-form-item>
        <el-form-item label="航次">
          <el-input v-model="bizForm.voyage" placeholder="请输入航次"></el-input>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="bizForm.remark" type="textarea" :rows="3" placeholder="备注信息"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="bizDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveBusiness" :loading="bizSaving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const bizLoading = ref(false)
const bizDialogVisible = ref(false)
const bizSaving = ref(false)
const businessList = ref([])

const bizSearch = reactive({ 
  business_no: '', 
  container_no: '', 
  bill_no: '', 
  business_type: '' 
})

const bizForm = reactive({ 
  id: null, 
  business_type: '', 
  business_type_name: '', 
  container_no: '', 
  container_type: '', 
  bill_no: '', 
  ship_name: '', 
  voyage: '', 
  remark: '', 
  generated_no: '' 
})

const typeMap = { 
  '602': '美国海运 - 美森', 
  '601': '代操作', 
  '610': '美国海运 - 普船', 
  '604': '美国空运', 
  '611': '加拿大空海运', 
  '612': '东南亚空海运', 
  '606': '日本海运', 
  '607': '日本空运', 
  '603': '美国海运尾程', 
  '605': '美国空运尾程', 
  '608': '转同行', 
  '609': '账单用' 
}

// 加载业务列表
const fetchBusiness = async () => {
  bizLoading.value = true
  try {
    const params = new URLSearchParams()
    Object.entries(bizSearch).forEach(([k, v]) => v && params.append(k, v))
    const res = await fetch(`http://127.0.0.1:8000/api/business?${params}`)
    businessList.value = await res.json()
  } catch (e) { 
    ElMessage.error('加载业务列表失败') 
  }
  bizLoading.value = false
}

const onTypeChange = (val) => { 
  bizForm.business_type_name = typeMap[val] || '' 
}

const openBusinessDialog = (row = null) => {
  if (row) {
    Object.assign(bizForm, row)
  } else {
    Object.assign(bizForm, { 
      id: null, 
      business_type: '', 
      business_type_name: '', 
      container_no: '', 
      container_type: '', 
      bill_no: '', 
      ship_name: '', 
      voyage: '', 
      remark: '', 
      generated_no: '' 
    })
  }
  bizDialogVisible.value = true
}

// 保存业务
const saveBusiness = async () => {
  if (!bizForm.business_type) {
    return ElMessage.warning('请选择业务类型')
  }
  
  bizSaving.value = true
  try {
    const url = bizForm.id ? `/api/business/${bizForm.id}` : '/api/business'
    const method = bizForm.id ? 'PUT' : 'POST'
    
    const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
    const payload = {
      ...bizForm,
      operator: userInfo.username || 'system',
      user_role: userInfo.role || 'system'
    }
    
    const res = await fetch(`http://127.0.0.1:8000${url}`, {
      method: method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    
    if (res.ok) {
      const result = await res.json()
      ElMessage.success(result.message || '保存成功')
      bizDialogVisible.value = false
      fetchBusiness()
    } else {
      const result = await res.json()
      ElMessage.error(result.detail || '操作失败')
    }
  } catch (e) { 
    ElMessage.error('网络错误') 
  }
  bizSaving.value = false
}

// 删除业务
const deleteBusiness = async (id) => {
  ElMessageBox.confirm('确定删除此业务信息吗？', '警告', { 
    confirmButtonText: '确定', 
    cancelButtonText: '取消', 
    type: 'warning' 
  }).then(async () => {
    try {
      const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
      const res = await fetch(`http://127.0.0.1:8000/api/business/${id}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          operator: userInfo.username || 'system',
          user_role: userInfo.role || 'system',
          reason: '手动删除'
        })
      })
      if (res.ok) { 
        ElMessage.success('删除成功')
        fetchBusiness() 
      } else {
        ElMessage.error('删除失败')
      }
    } catch (e) { 
      ElMessage.error('网络错误') 
    }
  })
}

onMounted(() => { 
  fetchBusiness() 
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
.search-bar { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-bottom: 24px; padding: 24px; background: rgba(242,242,247,0.6); border-radius: 16px; }
.action-cell { display: flex; gap: 8px; }
:deep(.el-table) { border-radius: 14px; overflow: hidden; }
:deep(.el-table__header-wrapper th) { background: linear-gradient(135deg, rgba(0,122,255,0.05) 0%, rgba(88,86,214,0.05) 100%); font-weight: 700; font-size: 13px; }
:deep(.el-button--primary) { background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%) !important; border: none !important; border-radius: 12px !important; }
</style>