<template>
  <div class="page">
    <div class="page-header">
      <h2>操作日志</h2>
      <p>记录所有数据的创建、修改与删除轨迹</p>
    </div>
    <div class="card">
      <div class="card-body">
        <!-- 筛选栏 -->
        <div class="search-bar">
          <el-select v-model="filter.type" placeholder="操作类型" clearable style="width: 140px">
            <el-option label="🟢 新增 (CREATE)" value="CREATE"></el-option>
            <el-option label="🟠 修改 (UPDATE)" value="UPDATE"></el-option>
            <el-option label="🔴 删除 (DELETE)" value="DELETE"></el-option>
          </el-select>
          <el-select v-model="filter.table" placeholder="涉及模块" clearable style="width: 140px">
            <el-option label="订单表" value="orders"></el-option>
            <el-option label="客户表" value="customers"></el-option>
            <el-option label="业务表" value="business_info"></el-option>
          </el-select>
          <el-input v-model="filter.operator" placeholder="操作人" clearable></el-input>
          <el-date-picker v-model="filter.dateRange" type="daterange" range-separator="至" start-placeholder="开始" end-placeholder="结束" value-format="YYYY-MM-DD" style="width: 260px"></el-date-picker>
          <el-button type="primary" @click="fetchLogs" icon="Search">查询</el-button>
        </div>

        <!-- 日志表格 -->
        <el-table :data="logs" stripe v-loading="loading" max-height="600">
          <el-table-column prop="operated_at" label="时间" width="170"></el-table-column>
          <el-table-column prop="operator" label="操作人" width="100"></el-table-column>
          <el-table-column label="类型" width="110" align="center">
            <template #default="scope">
              <el-tag :type="tagType(scope.row.operation_type)" size="small">{{ scope.row.operation_type }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="table_name" label="模块" width="100">
            <template #default="scope">
              <span style="font-size:12px; color:#666">{{ scope.row.table_name }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="record_id" label="记录ID" width="80" align="center"></el-table-column>
          <el-table-column prop="reason" label="原因/备注" min-width="150" show-overflow-tooltip></el-table-column>
          <el-table-column label="数据快照" width="120" fixed="right">
            <template #default="scope">
              <el-button type="primary" size="small" text @click="viewDiff(scope.row)">查看变更</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 数据对比弹窗 -->
    <el-dialog v-model="diffVisible" :title="`${currentLog.operation_type} 数据详情`" width="800px">
      <div style="display: flex; gap: 20px;">
        <div style="flex: 1">
          <h4 style="margin-bottom: 10px; color: #666;">变更前 (Old)</h4>
          <pre class="json-box">{{ formatJson(currentLog.old_data) }}</pre>
        </div>
        <div style="flex: 1">
          <h4 style="margin-bottom: 10px; color: #007AFF;">变更后 (New)</h4>
          <pre class="json-box">{{ formatJson(currentLog.new_data) }}</pre>
        </div>
      </div>
      <template #footer><el-button @click="diffVisible = false">关闭</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const logs = ref([])
const diffVisible = ref(false)
const currentLog = ref({})

const filter = reactive({ type: '', table: '', operator: '', dateRange: [] })

const tagType = (type) => type === 'CREATE' ? 'success' : type === 'UPDATE' ? 'warning' : 'danger'

const fetchLogs = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams()
    if (filter.type) params.append('operation_type', filter.type)
    if (filter.table) params.append('table_name', filter.table)
    if (filter.operator) params.append('operator', filter.operator)
    if (filter.dateRange?.[0]) params.append('start_date', filter.dateRange[0])
    if (filter.dateRange?.[1]) params.append('end_date', filter.dateRange[1])
    
    const res = await fetch(`http://127.0.0.1:8000/api/operation-logs?${params}`)
    logs.value = await res.json()
  } catch (e) {
    ElMessage.error('加载日志失败')
  }
  loading.value = false
}

const viewDiff = (row) => { currentLog.value = row; diffVisible.value = true }
const formatJson = (data) => data ? JSON.stringify(data, null, 2) : '无变更记录'

onMounted(() => fetchLogs())
</script>

<style scoped>
.page { animation: fadeIn 0.4s; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
.page-header { margin-bottom: 32px; }
.page-header h2 { font-size: 32px; font-weight: 700; color: #1c1c1e; margin-bottom: 8px; }
.page-header p { color: #8E8E93; font-size: 16px; }
.card { background: rgba(255,255,255,0.9); backdrop-filter: blur(20px); border-radius: 20px; box-shadow: 0 8px 32px rgba(0,0,0,0.08); border: 1px solid rgba(255,255,255,0.6); overflow: hidden; }
.card-body { padding: 32px; }
.search-bar { display: flex; gap: 16px; margin-bottom: 20px; flex-wrap: wrap; }
.json-box { background: #f5f7fa; padding: 15px; border-radius: 10px; max-height: 400px; overflow: auto; font-size: 13px; line-height: 1.5; white-space: pre-wrap; }
:deep(.el-table) { border-radius: 14px; overflow: hidden; }
:deep(.el-table__header-wrapper th) { background: linear-gradient(135deg, rgba(0,122,255,0.05) 0%, rgba(88,86,214,0.05) 100%); font-weight: 700; font-size: 13px; }
</style>