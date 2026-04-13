<template>
  <div class="page">
    <div class="page-header">
      <h2>账单查询</h2>
      <p>查看订单账单和付款状态</p>
    </div>
    
    <!-- 账单统计 -->
    <div class="bill-summary">
      <div class="bill-stat">
        <div class="bill-stat-value">{{ billsData.total_count }}</div>
        <div class="bill-stat-label">账单数量</div>
      </div>
      <div class="bill-stat">
        <div class="bill-stat-value">¥{{ billsData.total_amount.toFixed(2) }}</div>
        <div class="bill-stat-label">总金额</div>
      </div>
    </div>

    <div class="card">
      <div class="card-body">
        <!-- 搜索栏 -->
        <div class="search-bar">
          <el-input 
            v-model="billSearch.customer_name" 
            placeholder="客户名称" 
            clearable
          ></el-input>
          <el-select 
            v-model="billSearch.status" 
            placeholder="付款状态" 
            clearable
          >
            <el-option label="已付款" value="paid"></el-option>
            <el-option label="未付款" value="unpaid"></el-option>
          </el-select>
          <el-date-picker 
            v-model="billSearch.date_range" 
            type="daterange" 
            range-separator="至" 
            start-placeholder="开始日期" 
            end-placeholder="结束日期" 
            value-format="YYYY-MM-DD"
          ></el-date-picker>
          <el-button type="primary" @click="fetchBills" icon="Search">查询</el-button>
        </div>

        <!-- 数据表格 -->
        <el-table :data="billsData.items" stripe v-loading="billsLoading">
          <el-table-column prop="id" label="ID" width="60"></el-table-column>
          <el-table-column prop="customer_name" label="客户" width="120"></el-table-column>
          <el-table-column prop="order_no" label="订单号" width="140"></el-table-column>
          <el-table-column prop="total_weight" label="重量(KG)" width="100" align="right"></el-table-column>
          <el-table-column prop="kg_price" label="单价" width="90" align="right"></el-table-column>
          <el-table-column label="金额" width="120" align="right">
            <template #default="scope">
              <strong style="color: #007AFF;">¥{{ (scope.row.amount || 0).toFixed(2) }}</strong>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100" align="center">
            <template #default="scope">
              <el-tag :type="scope.row.status === '已付款' ? 'success' : 'warning'" size="small">
                {{ scope.row.status === '已付款' ? '已付款' : '待付款' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="160"></el-table-column>
          <el-table-column label="操作" width="120" fixed="right" v-if="userRole === 'admin' || userRole === 'finance'">
            <template #default="scope">
              <el-button 
                type="success" 
                size="small" 
                @click="markAsPaid(scope.row)" 
                v-if="scope.row.status !== '已付款'"
              >
                标记付款
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const billsLoading = ref(false)
const billsData = reactive({
  items: [],
  total_amount: 0,
  total_count: 0
})
const userRole = ref('')

const billSearch = reactive({
  customer_name: '',
  status: '',
  date_range: []
})

// 加载账单列表
const fetchBills = async () => {
  billsLoading.value = true
  try {
    const params = new URLSearchParams()
    if (billSearch.customer_name) params.append('customer_name', billSearch.customer_name)
    if (billSearch.status) params.append('status', billSearch.status)
    if (billSearch.date_range && billSearch.date_range[0]) params.append('start_date', billSearch.date_range[0])
    if (billSearch.date_range && billSearch.date_range[1]) params.append('end_date', billSearch.date_range[1])
    
    const res = await fetch(`http://127.0.0.1:8000/api/bills?${params}`)
    const data = await res.json()
    billsData.items = Array.isArray(data.items) ? data.items : []
    billsData.total_amount = data.total_amount || 0
    billsData.total_count = data.total_count || 0
  } catch (e) {
    console.error('加载账单失败:', e)
    ElMessage.error('加载账单失败')
  }
  billsLoading.value = false
}

// 标记为已付款
const markAsPaid = async (row) => {
  ElMessageBox.confirm(`标记订单 ${row.order_no} 为已付款？`, '确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/bills/${row.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          status: '已付款',
          role: userRole.value
        })
      })
      if (res.ok) {
        ElMessage.success('标记成功')
        fetchBills()
      } else {
        const result = await res.json()
        ElMessage.error(result.detail || '操作失败')
      }
    } catch (e) {
      ElMessage.error('网络错误')
    }
  })
}

// 初始化
onMounted(() => {
  userRole.value = localStorage.getItem('userRole') || ''
  fetchBills()
})
</script>

<style scoped>
.page {
  animation: fadeIn 0.4s;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.page-header {
  margin-bottom: 32px;
}

.page-header h2 {
  font-size: 32px;
  font-weight: 700;
  color: #1c1c1e;
  margin-bottom: 8px;
}

.page-header p {
  color: #8E8E93;
  font-size: 16px;
}

.bill-summary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 32px;
  border-radius: 20px;
  margin-bottom: 28px;
  display: flex;
  justify-content: space-around;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
}

.bill-stat {
  text-align: center;
}

.bill-stat-value {
  font-size: 40px;
  font-weight: 700;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.bill-stat-label {
  font-size: 14px;
  opacity: 0.9;
  margin-top: 8px;
}

.card {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.6);
  overflow: hidden;
}

.card-body {
  padding: 32px;
}

.search-bar {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
  padding: 24px;
  background: rgba(242, 242, 247, 0.6);
  border-radius: 16px;
}

:deep(.el-table) {
  border-radius: 14px;
  overflow: hidden;
}

:deep(.el-table__header-wrapper th) {
  background: linear-gradient(135deg, rgba(0, 122, 255, 0.05) 0%, rgba(88, 86, 214, 0.05) 100%);
  font-weight: 700;
  font-size: 13px;
}

:deep(.el-button--primary) {
  background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%) !important;
  border: none !important;
  border-radius: 12px !important;
}
</style>