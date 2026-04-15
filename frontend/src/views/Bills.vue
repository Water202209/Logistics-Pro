<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h2>账单查询</h2>
        <p>查询、核销和管理账单信息</p>
      </div>
    </div>

    <div class="card">
      <div class="card-body">
        <!-- 查询区域 -->
        <div class="filter-bar">
          <el-input
            v-model="billSearch.customer_name"
            placeholder="客户"
            clearable
            class="filter-item"
            @keyup.enter="fetchBills"
          />

          <el-input
            v-model="billSearch.business_no"
            placeholder="业务编号"
            clearable
            class="filter-item"
            @keyup.enter="fetchBills"
          />

          <el-input
            v-model="billSearch.container_no"
            placeholder="集装箱号"
            clearable
            class="filter-item"
            @keyup.enter="fetchBills"
          />

          <el-select
            v-model="billSearch.bill_type"
            placeholder="账单类型"
            clearable
            class="filter-item"
          >
            <el-option label="预报账单" value="预报账单" />
            <el-option label="普通账单" value="普通账单" />
            <el-option label="手工账单" value="手工账单" />
          </el-select>

          <el-select
            v-model="billSearch.writeoff_status"
            placeholder="核销状态"
            clearable
            class="filter-item"
          >
            <el-option label="已核销" value="已核销" />
            <el-option label="未核销" value="未核销" />
          </el-select>

          <el-select
            v-model="billSearch.customer_fee_status"
            placeholder="客户费用状态"
            clearable
            class="filter-item"
          >
            <el-option label="已确认" value="已确认" />
            <el-option label="未确认" value="未确认" />
          </el-select>

          <el-date-picker
            v-model="billSearch.date_range"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            class="filter-item filter-date"
          />

          <div class="filter-actions">
            <el-button type="primary" @click="fetchBills">查询</el-button>
            <el-button @click="resetSearch">重置</el-button>
          </div>
        </div>

        <!-- 汇总 -->
        <div class="summary-bar">
          <div class="summary-item">
            <span class="label">当前结果票数：</span>
            <span class="value">{{ billsData.total_count || 0 }}</span>
          </div>
          <div class="summary-item">
            <span class="label">当前结果金额：</span>
            <span class="value">{{ formatCurrencySummary(billsData.items) }}</span>
          </div>
          <div class="summary-item" v-if="multipleSelection.length">
            <span class="label">已选票数：</span>
            <span class="value">{{ multipleSelection.length }}</span>
          </div>
          <div class="summary-item" v-if="multipleSelection.length">
            <span class="label">已选金额：</span>
            <span class="value">{{ formatCurrencySummary(multipleSelection) }}</span>
          </div>
        </div>

        <!-- 表格 -->
        <el-table
          :data="billsData.items"
          stripe
          border
          v-loading="billsLoading"
          @selection-change="handleSelectionChange"
          class="data-table"
        >
          <el-table-column type="selection" width="50" fixed="left" />
          <el-table-column prop="bill_no" label="账单编号" width="160" fixed="left" />
          <el-table-column prop="bill_type" label="账单类型" width="100" />
          <el-table-column prop="bill_date" label="账单日期" width="110" />
          <el-table-column prop="customer_name" label="客户" width="140" />
          <el-table-column prop="business_no" label="业务编号" width="140" />
          <el-table-column prop="container_no" label="集装箱号" width="140" />
          <el-table-column prop="order_no" label="订单号" width="170" />
          <el-table-column prop="boxes" label="件数" width="80" align="right" />
          <el-table-column prop="total_weight" label="重量(KG)" width="100" align="right" />
          <el-table-column prop="kg_price" label="KG单价" width="90" align="right" />
          <el-table-column prop="settle_weight" label="结算重量" width="100" align="right" />
          <el-table-column prop="volume_price" label="体积单价" width="90" align="right" />
          <el-table-column prop="settle_cbm" label="结算体积" width="100" align="right" />

          <el-table-column label="合计金额" width="120" align="right">
            <template #default="scope">
              <span class="money-text">
                {{ scope.row.currency || 'CNY' }}
                {{ Number(scope.row.total_amount || 0).toFixed(2) }}
              </span>
            </template>
          </el-table-column>

          <el-table-column label="核销状态" width="100" align="center">
            <template #default="scope">
              <el-tag
                :type="scope.row.writeoff_status === '已核销' ? 'success' : 'warning'"
                size="small"
              >
                {{ scope.row.writeoff_status || '未核销' }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column label="客户费用状态" width="110" align="center">
            <template #default="scope">
              <el-tag
                :type="scope.row.customer_fee_status === '已确认' ? 'success' : 'info'"
                size="small"
              >
                {{ scope.row.customer_fee_status || '未确认' }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="created_at" label="创建时间" width="160" />

          <el-table-column label="操作" width="120" fixed="right">
            <template #default="scope">
              <el-button
                size="small"
                type="success"
                @click="markAsPaid(scope.row)"
                v-if="scope.row.writeoff_status !== '已核销'"
              >
                核销
              </el-button>
              <el-tag v-else type="success" size="small">已核销</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const billsLoading = ref(false)
const multipleSelection = ref([])

const billsData = reactive({
  items: [],
  total_amount: 0,
  total_count: 0
})

const billSearch = reactive({
  customer_name: '',
  business_no: '',
  container_no: '',
  bill_type: '',
  writeoff_status: '',
  customer_fee_status: '',
  date_range: []
})

const handleSelectionChange = (rows) => {
  multipleSelection.value = rows || []
}

const formatCurrencySummary = (rows) => {
  if (!rows || !rows.length) return '0'

  const grouped = {}
  rows.forEach(row => {
    const currency = row.currency || 'CNY'
    const amount = Number(row.total_amount || 0)
    grouped[currency] = (grouped[currency] || 0) + amount
  })

  return Object.entries(grouped)
    .map(([currency, amount]) => `${currency} ${amount.toFixed(2)}`)
    .join(' / ')
}

const fetchBills = async () => {
  billsLoading.value = true
  try {
    const params = new URLSearchParams()

    if (billSearch.customer_name) params.append('customer_name', billSearch.customer_name)
    if (billSearch.business_no) params.append('business_no', billSearch.business_no)
    if (billSearch.container_no) params.append('container_no', billSearch.container_no)
    if (billSearch.bill_type) params.append('bill_type', billSearch.bill_type)
    if (billSearch.writeoff_status) params.append('writeoff_status', billSearch.writeoff_status)
    if (billSearch.customer_fee_status) params.append('customer_fee_status', billSearch.customer_fee_status)

    if (billSearch.date_range?.[0]) params.append('start_date', billSearch.date_range[0])
    if (billSearch.date_range?.[1]) params.append('end_date', billSearch.date_range[1])

    const res = await fetch(`http://127.0.0.1:8000/api/bills?${params.toString()}`)
    const data = await res.json()

    billsData.items = data.items || []
    billsData.total_amount = data.total_amount || 0
    billsData.total_count = data.total_count || 0
  } catch (error) {
    ElMessage.error('账单数据加载失败')
  } finally {
    billsLoading.value = false
  }
}

const resetSearch = () => {
  billSearch.customer_name = ''
  billSearch.business_no = ''
  billSearch.container_no = ''
  billSearch.bill_type = ''
  billSearch.writeoff_status = ''
  billSearch.customer_fee_status = ''
  billSearch.date_range = []
  fetchBills()
}

const markAsPaid = async (row) => {
  try {
    await ElMessageBox.confirm(`确认将账单 ${row.bill_no} 标记为已核销吗？`, '提示', {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    })

    const res = await fetch(`http://127.0.0.1:8000/api/bills/${row.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        writeoff_status: '已核销'
      })
    })

    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || '核销失败')
    }

    ElMessage.success('核销成功')
    fetchBills()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '操作失败')
    }
  }
}

onMounted(() => {
  fetchBills()
})
</script>

<style scoped>
.page {
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(6px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.page-header h2 {
  font-size: 24px;
  font-weight: 700;
  color: #1c1c1e;
  margin-bottom: 4px;
}

.page-header p {
  color: #8e8e93;
  font-size: 13px;
  margin: 0;
}

.card {
  background: rgba(255, 255, 255, 0.96);
  border-radius: 16px;
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.06);
  border: 1px solid rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.card-body {
  padding: 18px;
}

.filter-bar {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 14px;
  align-items: center;
}

.filter-item {
  width: 100%;
}

.filter-date {
  grid-column: span 2;
}

.filter-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.summary-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 18px;
  align-items: center;
  padding: 10px 12px;
  margin-bottom: 14px;
  background: #f8faff;
  border: 1px solid #e8f1ff;
  border-radius: 10px;
}

.summary-item {
  font-size: 13px;
  color: #606266;
}

.summary-item .label {
  color: #909399;
  margin-right: 4px;
}

.summary-item .value {
  color: #1677ff;
  font-weight: 700;
}

.data-table {
  width: 100%;
}

.money-text {
  color: #1677ff;
  font-weight: 700;
}

:deep(.el-input__wrapper),
:deep(.el-select .el-input__wrapper),
:deep(.el-date-editor.el-input__wrapper) {
  border-radius: 10px;
}

:deep(.el-button) {
  border-radius: 10px;
  font-weight: 600;
}

:deep(.el-table th.el-table__cell) {
  background: #f8fafc !important;
  color: #344054;
  font-weight: 700;
}

@media (max-width: 1400px) {
  .filter-bar {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }

  .filter-date {
    grid-column: span 2;
  }
}

@media (max-width: 900px) {
  .filter-bar {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .filter-date {
    grid-column: span 2;
  }

  .filter-actions {
    justify-content: stretch;
  }
}

@media (max-width: 640px) {
  .filter-bar {
    grid-template-columns: 1fr;
  }

  .filter-date {
    grid-column: span 1;
  }
}
</style>