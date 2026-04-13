<template>
  <div class="page">
    <div class="page-header">
      <h2>在库管理</h2>
      <p>仓库库存实时查询与管理</p>
    </div>
    
    <div class="card">
      <div class="card-body">
        <!-- 可折叠搜索栏 -->
        <div class="search-section">
          <div class="search-header" @click="showSearch = !showSearch">
            <el-icon><Search /></el-icon>
            <span>搜索条件 (支持空格分隔多值模糊搜索)</span>
            <el-icon class="arrow"><ArrowUp v-if="showSearch" /><ArrowDown v-else /></el-icon>
          </div>
          
          <div v-show="showSearch" class="search-bar">
            <el-input v-model="search.customer_id" placeholder="客户 ID (多值空格分隔)" clearable></el-input>
            <el-input v-model="search.order_no" placeholder="订单号 (多值空格分隔)" clearable></el-input>
            <el-input v-model="search.box_no" placeholder="箱号 (多值空格分隔)" clearable></el-input>
            <el-input v-model="search.status" placeholder="状态 (多值空格分隔)" clearable></el-input>
            <el-input v-model="search.amazon_warehouse" placeholder="Amazon 仓库代码" clearable></el-input>
            <el-input v-model="search.channel" placeholder="渠道 (多值空格分隔)" clearable></el-input>
            <el-input v-model="search.business_no" placeholder="业务编号 (多值空格分隔)" clearable></el-input>
            <el-input v-model="search.business_type" placeholder="业务类型 (多值空格分隔)" clearable></el-input>
            <el-input v-model="search.zip_code" placeholder="邮编 (多值空格分隔)" clearable></el-input>
            <el-input v-model="search.ups_tracking" placeholder="UPS 尾程单号 (多值空格分隔)" clearable></el-input>
          </div>
        </div>
        
        <div style="display: flex; justify-content: space-between; margin-bottom: 16px;">
          <div>
            <el-button type="primary" @click="openDialog()" icon="Plus">新增记录</el-button>
            <el-button type="success" @click="exportData" icon="Download">导出 CSV</el-button>
          </div>
          <div>
            <el-button @click="resetSearch" icon="Refresh">重置</el-button>
            <el-button type="primary" @click="fetchData" icon="Search">查询</el-button>
          </div>
        </div>

        <!-- 数据表格 -->
        <div class="table-wrapper">
          <el-table :data="inventoryList" stripe v-loading="loading" style="width: 100%" min-height="500">
            <el-table-column prop="id" label="ID" width="60" fixed></el-table-column>
            <el-table-column prop="customer_id" label="客户 ID" width="100"></el-table-column>
            <el-table-column prop="order_no" label="订单号" width="150" fixed="left"></el-table-column>
            <el-table-column prop="boxes" label="件数" width="70" align="center"></el-table-column>
            <el-table-column prop="box_no" label="箱号" width="100"></el-table-column>
            <el-table-column prop="status" label="状态" width="90" align="center">
              <template #default="scope">
                <el-tag :type="scope.row.status === '在库' ? 'success' : 'info'" size="small">{{ scope.row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="inbound_date" label="入库日期" width="110"></el-table-column>
            <el-table-column prop="weight" label="重量 (KG)" width="90" align="right"></el-table-column>
            <el-table-column prop="length" label="长 (cm)" width="70" align="right"></el-table-column>
            <el-table-column prop="width" label="宽 (cm)" width="70" align="right"></el-table-column>
            <el-table-column prop="height" label="高 (cm)" width="70" align="right"></el-table-column>
            <el-table-column prop="volume" label="体积 (m³)" width="90" align="right"></el-table-column>
            <el-table-column prop="volume_weight" label="体积重 (KG)" width="100" align="right"></el-table-column>
            <el-table-column prop="amazon_warehouse" label="Amazon 仓库" width="120"></el-table-column>
            <el-table-column prop="non_std_weight" label="非标箱重" width="90" align="right"></el-table-column>
            <el-table-column prop="non_std_size" label="非标尺寸" width="100"></el-table-column>
            <el-table-column prop="zip_code" label="邮编" width="100"></el-table-column>
            <el-table-column prop="delivery_method" label="派送方式" width="100"></el-table-column>
            <el-table-column prop="ups_tracking" label="UPS 尾程单号" width="150"></el-table-column>
            <el-table-column prop="ups_scan_time" label="UPS 扫描时间" width="120"></el-table-column>
            <el-table-column prop="sign_time" label="签收时间" width="120"></el-table-column>
            <el-table-column prop="ups_master_no" label="UPS 总单号" width="150"></el-table-column>
            <el-table-column prop="channel" label="渠道" width="120"></el-table-column>
            <el-table-column prop="business_no" label="业务编号" width="140"></el-table-column>
            <el-table-column prop="business_type" label="业务类型" width="120"></el-table-column>
            <el-table-column prop="ship_name" label="船名" width="120"></el-table-column>
            <el-table-column prop="voyage" label="航次" width="100"></el-table-column>
            <el-table-column prop="remark" label="备注" width="150" show-overflow-tooltip></el-table-column>
            <el-table-column label="操作" width="140" fixed="right">
              <template #default="scope">
                <el-button type="primary" size="small" @click="openDialog(scope.row)">编辑</el-button>
                <el-button type="danger" size="small" @click="deleteItem(scope.row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </div>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑记录' : '新增记录'" width="900px" top="5vh">
      <el-form :model="form" label-width="120px" ref="formRef">
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item label="客户 ID"><el-input v-model="form.customer_id"></el-input></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="订单号"><el-input v-model="form.order_no"></el-input></el-form-item></el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8"><el-form-item label="件数"><el-input-number v-model="form.boxes" :min="0" style="width:100%"></el-input-number></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="箱号"><el-input v-model="form.box_no"></el-input></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="状态"><el-select v-model="form.status" style="width:100%"><el-option label="在库" value="在库"/><el-option label="已出库" value="已出库"/><el-option label="待上架" value="待上架"/></el-select></el-form-item></el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8"><el-form-item label="长 (cm)"><el-input-number v-model="form.length" :min="0" :precision="2" style="width:100%"></el-input-number></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="宽 (cm)"><el-input-number v-model="form.width" :min="0" :precision="2" style="width:100%"></el-input-number></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="高 (cm)"><el-input-number v-model="form.height" :min="0" :precision="2" style="width:100%"></el-input-number></el-form-item></el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8"><el-form-item label="重量 (KG)"><el-input-number v-model="form.weight" :min="0" :precision="2" style="width:100%"></el-input-number></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="体积 (m³)"><el-input v-model="form.volume" disabled style="width:100%"></el-input></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="体积重 (KG)"><el-input v-model="form.volume_weight" disabled style="width:100%"></el-input></el-form-item></el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item label="Amazon 仓库代码"><el-input v-model="form.amazon_warehouse" placeholder="如：ONT8"></el-input></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="邮编"><el-input v-model="form.zip_code"></el-input></el-form-item></el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item label="渠道"><el-input v-model="form.channel"></el-input></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="派送方式"><el-input v-model="form.delivery_method" placeholder="如：卡车派送"></el-input></el-form-item></el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item label="业务编号"><el-input v-model="form.business_no"></el-input></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="业务类型"><el-input v-model="form.business_type"></el-input></el-form-item></el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item label="船名"><el-input v-model="form.ship_name"></el-input></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="航次"><el-input v-model="form.voyage"></el-input></el-form-item></el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item label="UPS 尾程单号"><el-input v-model="form.ups_tracking"></el-input></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="UPS 总单号"><el-input v-model="form.ups_master_no"></el-input></el-form-item></el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item label="非标箱重量"><el-input-number v-model="form.non_std_weight" :min="0" :precision="2" style="width:100%"></el-input-number></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="非标箱尺寸"><el-input v-model="form.non_std_size" placeholder="如：超长/超宽"></el-input></el-form-item></el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item label="UPS 扫描时间"><el-date-picker v-model="form.ups_scan_time" type="datetime" placeholder="选择时间" style="width:100%"></el-date-picker></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="签收时间"><el-date-picker v-model="form.sign_time" type="datetime" placeholder="选择时间" style="width:100%"></el-date-picker></el-form-item></el-col>
        </el-row>
        <el-form-item label="备注"><el-input v-model="form.remark" type="textarea" :rows="3"></el-input></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveData" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, ArrowUp, ArrowDown } from '@element-plus/icons-vue'

const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const showSearch = ref(true)
const formRef = ref(null)

const search = reactive({
  customer_id: '', order_no: '', box_no: '', status: '',
  amazon_warehouse: '', channel: '', business_no: '',
  business_type: '', zip_code: '', ups_tracking: ''
})

const form = reactive({
  id: null, customer_id: '', order_no: '', boxes: 0, box_no: '',
  status: '在库', inbound_date: '', weight: 0,
  length: 0, width: 0, height: 0, volume: 0, volume_weight: 0,
  amazon_warehouse: '', non_std_weight: 0, non_std_size: '',
  zip_code: '', delivery_method: '', ups_tracking: '',
  ups_scan_time: '', sign_time: '', ups_master_no: '',
  channel: '', business_no: '', business_type: '',
  ship_name: '', voyage: '', remark: ''
})

const inventoryList = ref([])

// 自动计算体积和体积重 (长*宽*高/1000000, /6000)
watch([() => form.length, () => form.width, () => form.height], ([l, w, h]) => {
  if (l && w && h) {
    form.volume = parseFloat(((l * w * h) / 1000000).toFixed(4))
    form.volume_weight = parseFloat(((l * w * h) / 6000).toFixed(2))
  } else {
    form.volume = 0
    form.volume_weight = 0
  }
})

const fetchData = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams()
    Object.entries(search).forEach(([k, v]) => v && params.append(k, v))
    const res = await fetch(`http://127.0.0.1:8000/api/inventory?${params}`)
    inventoryList.value = await res.json()
  } catch (e) { ElMessage.error('加载数据失败') }
  loading.value = false
}

const resetSearch = () => { Object.keys(search).forEach(k => search[k] = ''); fetchData() }

const openDialog = (row = null) => {
  if (row) Object.assign(form, row)
  else Object.assign(form, { id: null, customer_id: '', order_no: '', boxes: 0, box_no: '', status: '在库', inbound_date: new Date().toISOString().split('T')[0], weight: 0, length: 0, width: 0, height: 0, volume: 0, volume_weight: 0, amazon_warehouse: '', non_std_weight: 0, non_std_size: '', zip_code: '', delivery_method: '', ups_tracking: '', ups_scan_time: '', sign_time: '', ups_master_no: '', channel: '', business_no: '', business_type: '', ship_name: '', voyage: '', remark: '' })
  dialogVisible.value = true
}

const saveData = async () => {
  saving.value = true
  try {
    const url = form.id ? `http://127.0.0.1:8000/api/inventory/${form.id}` : 'http://127.0.0.1:8000/api/inventory'
    const method = form.id ? 'PUT' : 'POST'
    const res = await fetch(url, { method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(form) })
    if (res.ok) { ElMessage.success('保存成功'); dialogVisible.value = false; fetchData() }
    else { const err = await res.json(); ElMessage.error(err.detail || '保存失败') }
  } catch (e) { ElMessage.error('网络错误') }
  saving.value = false
}

const deleteItem = async (id) => {
  ElMessageBox.confirm('确定删除这条记录吗？', '警告', { type: 'warning' }).then(async () => {
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/inventory/${id}`, { method: 'DELETE' })
      if (res.ok) { ElMessage.success('删除成功'); fetchData() } else { ElMessage.error('删除失败') }
    } catch (e) { ElMessage.error('网络错误') }
  })
}

const exportData = () => {
  if (inventoryList.value.length === 0) return ElMessage.warning('没有数据可导出')
  const headers = ['客户 ID','订单号','件数','箱号','状态','入库日期','重量','长','宽','高','体积','体积重','Amazon 仓库','非标箱重','非标尺寸','邮编','派送方式','UPS 尾程单号','UPS 扫描时间','签收时间','UPS 总单号','渠道','业务编号','业务类型','船名','航次','备注']
  const rows = inventoryList.value.map(i => [i.customer_id, i.order_no, i.boxes, i.box_no, i.status, i.inbound_date, i.weight, i.length, i.width, i.height, i.volume, i.volume_weight, i.amazon_warehouse, i.non_std_weight, i.non_std_size, i.zip_code, i.delivery_method, i.ups_tracking, i.ups_scan_time, i.sign_time, i.ups_master_no, i.channel, i.business_no, i.business_type, i.ship_name, i.voyage, i.remark])
  const csv = '\uFEFF' + [headers.join(','), ...rows.map(r => r.join(','))].join('\n')
  const link = document.createElement('a')
  link.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8;' }))
  link.download = `在库数据_${new Date().toLocaleDateString()}.csv`
  link.click()
  ElMessage.success(`已导出 ${inventoryList.value.length} 条数据`)
}

onMounted(() => fetchData())
</script>

<style scoped>
.page { animation: fadeIn 0.4s; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
.page-header { margin-bottom: 32px; }
.page-header h2 { font-size: 32px; font-weight: 700; color: #1c1c1e; margin-bottom: 8px; }
.page-header p { color: #8E8E93; font-size: 16px; }
.card { background: rgba(255,255,255,0.9); backdrop-filter: blur(20px); border-radius: 20px; box-shadow: 0 8px 32px rgba(0,0,0,0.08); border: 1px solid rgba(255,255,255,0.6); overflow: hidden; }
.card-body { padding: 32px; }
.search-section { margin-bottom: 20px; border: 1px solid #e4e7ed; border-radius: 8px; overflow: hidden; }
.search-header { padding: 12px 16px; background: #f5f7fa; cursor: pointer; display: flex; align-items: center; gap: 8px; font-weight: 600; user-select: none; }
.search-header:hover { background: #ecf5ff; }
.arrow { margin-left: auto; transition: transform 0.3s; }
.search-bar { padding: 16px; display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 16px; background: #fafafa; }
.table-wrapper { overflow-x: auto; }
:deep(.el-table) { font-size: 13px; }
:deep(.el-table__header-wrapper th) { font-weight: 700; }
</style>