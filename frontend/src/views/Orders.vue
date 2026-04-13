<template>
  <div class="page">
    <div class="page-header">
      <h2>订单查询</h2>
      <p>查询和管理订单</p>
    </div>
    
    <div class="card">
      <div class="card-body">
        <!-- 增强搜索栏 -->
        <div class="search-bar">
          <el-input 
            v-model="search.order_no" 
            placeholder="订单号（支持多个，用逗号分隔）" 
            clearable 
            prefix-icon="Search"
          ></el-input>
          <el-input 
            v-model="search.customer_name" 
            placeholder="客户名称（模糊搜索）" 
            clearable
          ></el-input>
          <el-input 
            v-model="search.business_no" 
            placeholder="业务编号（支持多个，用逗号分隔）" 
            clearable
          ></el-input>
          <el-input 
            v-model="search.fba_no" 
            placeholder="FBA号（模糊搜索）" 
            clearable
          ></el-input>
          <el-select 
            v-model="search.warehouse" 
            placeholder="仓库" 
            clearable 
            style="width: 120px"
          >
            <el-option label="铁士" value="铁士"></el-option>
            <el-option label="其他" value="其他"></el-option>
          </el-select>
          <el-select 
            v-model="search.channel" 
            placeholder="渠道" 
            clearable 
            style="width: 150px"
          >
            <el-option label="美国海运 - 美森" value="美国海运 - 美森"></el-option>
            <el-option label="美国海运 - 普船" value="美国海运 - 普船"></el-option>
            <el-option label="美国空运" value="美国空运"></el-option>
            <el-option label="日本海运" value="日本海运"></el-option>
            <el-option label="日本空运" value="日本空运"></el-option>
            <el-option label="加拿大空海运" value="加拿大空海运"></el-option>
            <el-option label="东南亚空海运" value="东南亚空海运"></el-option>
            <el-option label="其它" value="其它"></el-option>
          </el-select>
          <el-select 
            v-model="search.status" 
            placeholder="状态" 
            clearable 
            style="width: 120px"
          >
            <el-option label="待入库" value="待入库"></el-option>
            <el-option label="已入库" value="已入库"></el-option>
            <el-option label="已出库" value="已出库"></el-option>
          </el-select>
        </div>
        
        <div style="display: flex; gap: 10px; justify-content: space-between; margin-bottom: 20px;">
          <div>
            <el-button type="success" @click="exportSelected" :disabled="selectedOrders.length === 0" icon="Download">
              导出选中 ({{ selectedOrders.length }})
            </el-button>
          </div>
          <div style="display: flex; gap: 10px;">
            <el-button @click="resetSearch">重置</el-button>
            <el-button type="primary" @click="fetchOrders" icon="Search">搜索</el-button>
          </div>
        </div>

        <!-- 数据表格 -->
        <el-table 
          :data="orders" 
          stripe 
          v-loading="tableLoading" 
          height="400"
          @selection-change="handleSelectionChange"
          @row-click="handleRowClick"
          highlight-current-row
        >
          <el-table-column type="selection" width="55"></el-table-column>
          <el-table-column prop="id" label="ID" width="60"></el-table-column>
          <el-table-column prop="customer_name" label="客户" width="120" show-overflow-tooltip></el-table-column>
          <el-table-column prop="order_no" label="订单号" width="180" show-overflow-tooltip></el-table-column>
          <el-table-column prop="business_no" label="业务编号" width="160" show-overflow-tooltip></el-table-column>
          <el-table-column prop="fba_no" label="FBA号" width="120" show-overflow-tooltip></el-table-column>
          <el-table-column prop="channel" label="渠道" width="140" show-overflow-tooltip></el-table-column>
          <el-table-column prop="warehouse" label="仓库" width="80"></el-table-column>
          <el-table-column prop="boxes" label="预报件数" width="90" align="center"></el-table-column>
          <el-table-column prop="total_weight" label="预报总重量" width="110" align="right"></el-table-column>
          <el-table-column prop="cbm" label="预报体积" width="100" align="right"></el-table-column>
          <el-table-column prop="status" label="状态" width="90" align="center">
            <template #default="scope">
              <el-tag :type="scope.row.status === '待入库' ? 'warning' : 'success'" size="small">
                {{ scope.row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="scope">
              <el-dropdown @command="(cmd) => handleOperation(cmd, scope.row)" trigger="click">
                <el-button type="primary" size="small">
                  操作 <el-icon class="el-icon--right"><arrow-down /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="detail">📄 详情</el-dropdown-item>
                    <el-dropdown-item command="edit">✏️ 编辑</el-dropdown-item>
                    <el-dropdown-item command="warehouse">📥 入仓通知单</el-dropdown-item>
                    <el-dropdown-item command="label">🏷️ 箱唛标签</el-dropdown-item>
                    <el-dropdown-item command="copy">📋 复制订单</el-dropdown-item>
                    <el-dropdown-item command="bill">💰 生成账单</el-dropdown-item>
                    <el-dropdown-item command="inbound">📦 生成入库数据</el-dropdown-item>
                    <el-dropdown-item command="send">📤 发送预报</el-dropdown-item>
                    <el-dropdown-item command="fetch">🔄 抓取收货数据</el-dropdown-item>
                    <el-dropdown-item command="delete" divided style="color: #f56c6c">🗑️ 删除</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
          </el-table-column>
        </el-table>

        <!-- 统计信息面板 -->
        <div class="statistics-panel" v-if="selectedOrders.length > 0 || currentRow">
          <div class="statistics-title">
            📊 统计信息 
            <span v-if="selectedOrders.length > 0" style="font-size: 12px; color: #909399">
              (已选 {{ selectedOrders.length }} 条记录)
            </span>
          </div>
          <div class="statistics-grid">
            <div class="stat-item">
              <div class="stat-label">预报件数</div>
              <div class="stat-value">{{ stats.forecastBoxes }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">预报总重量</div>
              <div class="stat-value">{{ stats.forecastWeight }} KG</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">预报体积</div>
              <div class="stat-value">{{ stats.forecastVolume }} m³</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">入库件数</div>
              <div class="stat-value">{{ stats.inboundBoxes }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">入库总重量</div>
              <div class="stat-value">{{ stats.inboundWeight }} KG</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">入库体积</div>
              <div class="stat-value">{{ stats.inboundVolume }} m³</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">入库体积重</div>
              <div class="stat-value">{{ stats.volumeWeight }} KG</div>
              <div class="stat-hint">长×宽×高÷6000</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 打印/下载对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="800px">
      <div id="print-content" v-html="printContent" style="padding: 20px;"></div>
      <template #footer>
        <el-button @click="dialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="downloadPDF">下载PDF</el-button>
      </template>
    </el-dialog>

    <!-- 右侧编辑抽屉 -->
    <el-drawer v-model="drawerVisible" :title="drawerTitle" size="65%" direction="rtl" :close-on-click-modal="false">
      <div class="drawer-content">
        <el-form :model="editForm" label-width="110px">
          <!-- 基本信息 -->
          <div class="form-section">
            <div class="form-section-title">📌 基本信息</div>
            <div class="form-row">
              <div class="form-item">
                <label class="required">客户</label>
                <el-input v-model="editForm.customer_name" placeholder="客户名称"></el-input>
              </div>
              <div class="form-item">
                <label class="required">订单号</label>
                <el-input v-model="editForm.order_no" placeholder="订单号"></el-input>
              </div>
              <div class="form-item">
                <label class="required">渠道</label>
                <el-select v-model="editForm.channel" placeholder="请选择" style="width:100%">
                  <el-option label="美国海运 - 美森" value="美国海运 - 美森"></el-option>
                  <el-option label="美国海运 - 普船" value="美国海运 - 普船"></el-option>
                  <el-option label="美国空运" value="美国空运"></el-option>
                  <el-option label="日本海运" value="日本海运"></el-option>
                  <el-option label="日本空运" value="日本空运"></el-option>
                  <el-option label="加拿大空海运" value="加拿大空海运"></el-option>
                  <el-option label="东南亚空海运" value="东南亚空海运"></el-option>
                  <el-option label="其它" value="其它"></el-option>
                </el-select>
              </div>
              <div class="form-item">
                <label class="required">仓库</label>
                <el-select v-model="editForm.warehouse" style="width:100%">
                  <el-option label="铁士" value="铁士"></el-option>
                  <el-option label="其他" value="其他"></el-option>
                </el-select>
              </div>
            </div>
          </div>

          <!-- 货物信息 -->
          <div class="form-section">
            <div class="form-section-title">📦 货物信息</div>
            <div class="form-row">
              <div class="form-item">
                <label>预报件数</label>
                <el-input-number v-model="editForm.boxes" :min="0" style="width:100%"></el-input-number>
              </div>
              <div class="form-item">
                <label>预报总重量(KG)</label>
                <el-input-number v-model="editForm.total_weight" :min="0" :precision="2" style="width:100%"></el-input-number>
              </div>
              <div class="form-item">
                <label>预报体积(CBM)</label>
                <el-input-number v-model="editForm.cbm" :min="0" :precision="3" style="width:100%"></el-input-number>
              </div>
              <div class="form-item">
                <label>仓库代码</label>
                <el-input v-model="editForm.warehouse_code"></el-input>
              </div>
            </div>
          </div>

          <!-- 收件信息 -->
          <div class="form-section">
            <div class="form-section-title">📍 收件信息</div>
            <div class="form-row">
              <div class="form-item">
                <label>收件人</label>
                <el-input v-model="editForm.receiver_name"></el-input>
              </div>
              <div class="form-item">
                <label>地址1</label>
                <el-input v-model="editForm.address1"></el-input>
              </div>
            </div>
            <div class="form-row">
              <div class="form-item">
                <label>地址2</label>
                <el-input v-model="editForm.address2"></el-input>
              </div>
              <div class="form-item">
                <label>城市</label>
                <el-input v-model="editForm.city"></el-input>
              </div>
              <div class="form-item">
                <label>州/省</label>
                <el-input v-model="editForm.state"></el-input>
              </div>
            </div>
            <div class="form-row">
              <div class="form-item">
                <label>邮编</label>
                <el-input v-model="editForm.zip_code"></el-input>
              </div>
              <div class="form-item">
                <label>电话</label>
                <el-input v-model="editForm.phone"></el-input>
              </div>
              <div class="form-item">
                <label>电话2</label>
                <el-input v-model="editForm.phone2"></el-input>
              </div>
            </div>
          </div>

          <!-- 费用与物流 -->
          <div class="form-section">
            <div class="form-section-title">💰 费用与物流</div>
            <div class="form-row">
              <div class="form-item">
                <label>是否报关</label>
                <el-checkbox v-model="editForm.is_customs">是</el-checkbox>
              </div>
              <div class="form-item">
                <label>KG单价</label>
                <el-input-number v-model="editForm.kg_price" :min="0" :precision="2" style="width:100%"></el-input-number>
              </div>
              <div class="form-item">
                <label>业务编号</label>
                <el-input v-model="editForm.business_no"></el-input>
              </div>
              <div class="form-item">
                <label>FBA号</label>
                <el-input v-model="editForm.fba_no"></el-input>
              </div>
            </div>
            <div class="form-row">
              <div class="form-item">
                <label>船名航次</label>
                <el-input v-model="editForm.vessel_voyage"></el-input>
              </div>
              <div class="form-item">
                <label>品名</label>
                <el-input v-model="editForm.product_name"></el-input>
              </div>
            </div>
          </div>

          <!-- 备注 -->
          <div class="form-section" style="border-bottom: none;">
            <div class="form-section-title">📝 备注</div>
            <el-input v-model="editForm.order_note" type="textarea" :rows="3" placeholder="订单备注"></el-input>
          </div>
        </el-form>
      </div>
      <template #footer>
        <div style="display: flex; justify-content: flex-end; gap: 12px; padding: 10px 20px;">
          <el-button @click="drawerVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSave" :loading="saving">💾 保存</el-button>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { reactive, ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'

const tableLoading = ref(false)
const orders = ref([])
const selectedOrders = ref([])
const currentRow = ref(null)
const dialogVisible = ref(false)
const dialogTitle = ref('')
const printContent = ref('')
const drawerVisible = ref(false)
const drawerTitle = ref('新增订单')
const saving = ref(false)

const editForm = reactive({
  id: null,
  customer_name: '', order_no: '', channel: '', warehouse: '铁士',
  boxes: 0, total_weight: 0, cbm: 0, warehouse_code: '',
  receiver_name: '', address1: '', address2: '', city: '', state: '',
  zip_code: '', phone: '', phone2: '',
  is_customs: false, kg_price: null, business_no: '', fba_no: '',
  vessel_voyage: '', product_name: '', order_note: ''
})

const search = reactive({
  order_no: '', customer_name: '', business_no: '', fba_no: '',
  warehouse: '', channel: '', status: ''
})

// 统计数据
const stats = computed(() => {
  const dataToCalc = selectedOrders.value.length > 0 ? selectedOrders.value : (currentRow.value ? [currentRow.value] : [])
  
  return dataToCalc.reduce((acc, order) => {
    acc.forecastBoxes += order.boxes || 0
    acc.forecastWeight += order.total_weight || 0
    acc.forecastVolume += order.cbm || 0
    acc.inboundBoxes += order.inbound_boxes || 0
    acc.inboundWeight += order.inbound_weight || 0
    acc.inboundVolume += order.inbound_volume || 0
    // 体积重计算：假设标准尺寸，这里需要根据实际情况调整
    // 简化计算：体积重 = 体积(m³) × 167 (航空标准)
    acc.volumeWeight += (order.cbm || 0) * 167
    return acc
  }, {
    forecastBoxes: 0,
    forecastWeight: 0,
    forecastVolume: 0,
    inboundBoxes: 0,
    inboundWeight: 0,
    inboundVolume: 0,
    volumeWeight: 0
  })
})

const fetchOrders = async () => {
  tableLoading.value = true
  try {
    const params = new URLSearchParams()
    
    // 处理多值搜索
    if (search.order_no) {
      const orders = search.order_no.split(',').map(o => o.trim()).filter(o => o)
      params.append('order_no_multi', JSON.stringify(orders))
    }
    if (search.business_no) {
      const businesses = search.business_no.split(',').map(b => b.trim()).filter(b => b)
      params.append('business_no_multi', JSON.stringify(businesses))
    }
    
    // 其他搜索条件
    if (search.customer_name) params.append('customer_name', search.customer_name)
    if (search.fba_no) params.append('fba_no', search.fba_no)
    if (search.warehouse) params.append('warehouse', search.warehouse)
    if (search.channel) params.append('channel', search.channel)
    if (search.status) params.append('status', search.status)
    
    const res = await fetch(`http://127.0.0.1:8000/api/orders?${params}`)
    const data = await res.json()
    orders.value = Array.isArray(data) ? data : []
  } catch (e) {
    ElMessage.error('加载订单失败')
  }
  tableLoading.value = false
}

const resetSearch = () => {
  Object.keys(search).forEach(k => search[k] = '')
  fetchOrders()
}

const handleSelectionChange = (selection) => {
  selectedOrders.value = selection
}

const handleRowClick = (row) => {
  currentRow.value = row
}

// 处理操作
const handleOperation = (command, row) => {
  switch(command) {
    case 'detail':
      viewDetail(row)
      break
    case 'edit':
      openEditDrawer(row)
      break
    case 'warehouse':
      generateWarehouseNotice(row)
      break
    case 'label':
      generateLabels(row)
      break
    case 'copy':
      copyOrder(row)
      break
    case 'bill':
      generateBill(row)
      break
    case 'inbound':
      generateInboundData(row)
      break
    case 'send':
      sendToWarehouse(row)
      break
    case 'fetch':
      fetchWarehouseData(row)
      break
    case 'delete':
      deleteOrder(row.id)
      break
  }
}

const downloadOrderPdf = async (order, type) => {
  if (!order?.id) {
    ElMessage.warning('未找到订单ID，无法下载')
    return
  }

  const endpoint = type === 'warehouse' ? 'warehouse-pdf' : 'labels-pdf'
  const loadingText = type === 'warehouse' ? '正在生成入仓单...' : '正在生成箱唛...'

  try {
    ElMessage.info(loadingText)
    const res = await fetch(`http://127.0.0.1:8000/api/orders/${order.id}/${endpoint}`)

    if (!res.ok) {
      let errorMessage = 'PDF生成失败'
      try {
        const err = await res.json()
        errorMessage = err.detail || errorMessage
      } catch (_) {}
      throw new Error(errorMessage)
    }

    const blob = await res.blob()
    const downloadUrl = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = downloadUrl

    const disposition = res.headers.get('content-disposition') || ''
    const utf8Match = disposition.match(/filename\*=UTF-8''([^;]+)/i)
    const asciiMatch = disposition.match(/filename=([^;]+)/i)

    let filename = type === 'warehouse' ? `入仓单_${order.order_no}.pdf` : `箱唛_${order.order_no}.pdf`
    if (utf8Match?.[1]) {
      filename = decodeURIComponent(utf8Match[1])
    } else if (asciiMatch?.[1]) {
      filename = asciiMatch[1].replaceAll('"', '').trim()
    }

    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(downloadUrl)

    ElMessage.success(type === 'warehouse' ? '入仓单下载成功' : '箱唛下载成功')
  } catch (e) {
    ElMessage.error(e.message || '下载失败')
  }
}

// 生成入仓通知单
const generateWarehouseNotice = (order) => {
  downloadOrderPdf(order, 'warehouse')
}

// 生成箱唛标签
const generateLabels = (order) => {
  downloadOrderPdf(order, 'label')
}

// 下载PDF
const downloadPDF = async () => {
  ElMessage.info('请在订单操作里直接点击“入仓通知单”或“箱唛标签”下载正式PDF')
}

// 复制订单
const copyOrder = (order) => {
  Object.assign(editForm, order)
  editForm.id = null
  editForm.order_no = '' // 清空订单号，让系统自动生成
  drawerTitle.value = '📋 复制订单'
  drawerVisible.value = true
}

// 生成账单
const generateBill = (order) => {
  ElMessage.info('生成账单功能开发中...')
  // TODO: 实现账单生成逻辑
}

// 生成入库数据
const generateInboundData = (order) => {
  ElMessage.info('生成入库数据功能开发中...')
  // TODO: 实现入库数据生成
}

// 发送预报给仓库
const sendToWarehouse = (order) => {
  ElMessageBox.prompt('选择仓库', '发送预报', {
    confirmButtonText: '发送',
    cancelButtonText: '取消',
    inputPlaceholder: '输入仓库名称或选择'
  }).then(({ value }) => {
    if (value) {
      ElMessage.success(`预报已发送至 ${value}`)
      // TODO: 实现发送逻辑
    }
  }).catch(() => {})
}

// 抓取仓库收货数据
const fetchWarehouseData = (order) => {
  ElMessage.info('抓取仓库收货数据功能开发中...')
  // TODO: 实现抓取逻辑
}

// 打开抽屉（编辑模式）
const openEditDrawer = (row) => {
  Object.assign(editForm, row)
  editForm.is_customs = !!row.is_customs
  drawerTitle.value = '📝 编辑订单'
  drawerVisible.value = true
}

// 保存逻辑
const handleSave = async () => {
  if (!editForm.customer_name || !editForm.order_no) {
    return ElMessage.warning('请填写客户和订单号')
  }
  saving.value = true
  try {
    const isEdit = !!editForm.id
    const url = isEdit ? `http://127.0.0.1:8000/api/orders/${editForm.id}` : 'http://127.0.0.1:8000/api/orders'
    const method = isEdit ? 'PUT' : 'POST'
    
    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(editForm)
    })
    
    if (res.ok) {
      ElMessage.success(isEdit ? '✅ 更新成功' : '✅ 新增成功')
      drawerVisible.value = false
      fetchOrders()
    } else {
      const err = await res.json()
      ElMessage.error(err.detail || '操作失败')
    }
  } catch (e) {
    ElMessage.error('网络错误')
  }
  saving.value = false
}

const deleteOrder = async (id) => {
  ElMessageBox.confirm('确定删除此订单吗？', '警告', { type: 'warning' }).then(async () => {
    try {
      const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
      const res = await fetch(`http://127.0.0.1:8000/api/orders/${id}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          operator: userInfo.username || 'admin', 
          user_role: userInfo.role || 'admin', 
          reason: '手动删除' 
        })
      })
      if (res.ok) { 
        ElMessage.success('删除成功')
        fetchOrders() 
      } else {
        ElMessage.error('删除失败')
      }
    } catch (e) { 
      ElMessage.error('网络错误') 
    }
  })
}

const exportSelected = () => {
  if (selectedOrders.value.length === 0) return ElMessage.warning('请先勾选订单')
  const headers = ['ID', '客户', '订单号', '业务编号', 'FBA号', '渠道', '仓库', '预报件数', '预报总重量', '预报体积', '状态', '备注']
  const rows = selectedOrders.value.map(o => [
    o.id, o.customer_name, o.order_no, o.business_no, o.fba_no, 
    o.channel, o.warehouse, o.boxes, o.total_weight, o.cbm, o.status, o.order_note
  ])
  const BOM = '\uFEFF'
  const csv = BOM + [headers.join(','), ...rows.map(r => r.join(','))].join('\n')
  const link = document.createElement('a')
  link.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8;' }))
  link.download = `订单导出_${new Date().toLocaleDateString()}.csv`
  link.click()
  ElMessage.success(`已导出 ${selectedOrders.value.length} 条数据`)
}

onMounted(() => fetchOrders())
</script>

<style scoped>
.page { animation: fadeIn 0.4s; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
.page-header { margin-bottom: 32px; }
.page-header h2 { font-size: 32px; font-weight: 700; color: #1c1c1e; margin-bottom: 8px; }
.page-header p { color: #8E8E93; font-size: 16px; }
.card { background: rgba(255,255,255,0.9); backdrop-filter: blur(20px); border-radius: 20px; box-shadow: 0 8px 32px rgba(0,0,0,0.08); border: 1px solid rgba(255,255,255,0.6); overflow: hidden; }
.card-body { padding: 32px; }
.search-bar { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; padding: 24px; background: rgba(242,242,247,0.6); border-radius: 16px; }
.form-section { margin-bottom: 24px; padding-bottom: 20px; border-bottom: 1px solid rgba(0,0,0,0.06); }
.form-section-title { font-size: 13px; font-weight: 700; color: #007AFF; margin-bottom: 16px; text-transform: uppercase; letter-spacing: 0.8px; }
.form-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 16px; }
.form-item label { display: block; margin-bottom: 6px; font-size: 13px; color: #3a3a3c; font-weight: 600; }
.statistics-panel {
  margin-top: 20px;
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 12px;
  border: 1px solid #e4e7ed;
}
.statistics-title {
  font-size: 16px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 16px;
  padding-bottom: 10px;
  border-bottom: 2px solid #409eff;
}
.statistics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
}
.stat-item {
  background: white;
  padding: 12px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.stat-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}
.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: #409eff;
}
.stat-hint {
  font-size: 10px;
  color: #c0c4cc;
  margin-top: 4px;
}
:deep(.el-table) { border-radius: 14px; overflow: hidden; }
:deep(.el-table__header-wrapper th) { background: linear-gradient(135deg, rgba(0,122,255,0.05) 0%, rgba(88,86,214,0.05) 100%); font-weight: 700; font-size: 13px; }
:deep(.el-button--primary) { background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%) !important; border: none !important; border-radius: 12px !important; }
</style>