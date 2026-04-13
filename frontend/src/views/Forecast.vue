<template>
  <div class="page">
    <div class="page-header">
      <h2>客户预报</h2>
      <p>新增预报订单信息</p>
    </div>
    <div class="card">
      <div class="card-body">
        <el-form :model="form" label-width="110px" size="default">
          
          <!-- 1. 基本信息 -->
          <div class="form-section">
            <div class="form-section-title">📌 基本信息</div>
            <div class="form-row">
              <div class="form-item">
                <label class="required">客户</label>
                <el-autocomplete 
                  v-model="form.customer_name" 
                  :fetch-suggestions="querySearch" 
                  placeholder="输入或选择客户" 
                  clearable
                ></el-autocomplete>
              </div>
              <div class="form-item">
                <label>订单号 <span class="form-hint">（留空自动生成）</span></label>
                <el-input v-model="form.order_no" placeholder="留空自动生成"></el-input>
              </div>
              <div class="form-item">
                <label class="required">渠道</label>
                <el-select v-model="form.channel" placeholder="请选择" clearable style="width:100%">
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
                <el-select v-model="form.warehouse" placeholder="请选择" style="width:100%">
                  <el-option label="铁士" value="铁士"></el-option>
                  <el-option label="其他" value="其他"></el-option>
                </el-select>
              </div>
            </div>
          </div>

          <!-- 2. 货物信息 -->
          <div class="form-section">
            <div class="form-section-title">📦 货物信息</div>
            <div class="form-row">
              <div class="form-item">
                <label>箱数</label>
                <el-input-number v-model="form.boxes" :min="0" controls-position="right" style="width: 100%;"></el-input-number>
              </div>
              <div class="form-item">
                <label>总重量 (KG)</label>
                <el-input-number v-model="form.total_weight" :min="0" :precision="2" controls-position="right" style="width: 100%;"></el-input-number>
              </div>
              <div class="form-item">
                <label>CBM (体积)</label>
                <el-input-number v-model="form.cbm" :min="0" :precision="3" controls-position="right" style="width: 100%;"></el-input-number>
              </div>
              <div class="form-item">
                <label>仓库代码</label>
                <el-input v-model="form.warehouse_code" placeholder="可选"></el-input>
              </div>
            </div>
          </div>

          <!-- 3. 收件信息 -->
          <div class="form-section">
            <div class="form-section-title">📍 收件信息</div>
            <div class="form-row">
              <div class="form-item">
                <label>收件人</label>
                <el-input v-model="form.receiver_name" placeholder="收件人姓名"></el-input>
              </div>
              <div class="form-item">
                <label>地址1</label>
                <el-input v-model="form.address1" placeholder="街道地址"></el-input>
              </div>
            </div>
            <div class="form-row">
              <div class="form-item">
                <label>地址2</label>
                <el-input v-model="form.address2" placeholder="公寓/套房号"></el-input>
              </div>
              <div class="form-item">
                <label>城市</label>
                <el-input v-model="form.city" placeholder="城市"></el-input>
              </div>
              <div class="form-item">
                <label>州/省</label>
                <el-input v-model="form.state" placeholder="州或省"></el-input>
              </div>
            </div>
            <div class="form-row">
              <div class="form-item">
                <label>邮编</label>
                <el-input v-model="form.zip_code" placeholder="邮政编码"></el-input>
              </div>
              <div class="form-item">
                <label>电话 <span class="form-hint">10位数字不含空格</span></label>
                <el-input v-model="form.phone" placeholder="联系电话"></el-input>
              </div>
              <div class="form-item">
                <label>电话2</label>
                <el-input v-model="form.phone2" placeholder="备用电话"></el-input>
              </div>
            </div>
          </div>

          <!-- 4. 费用信息 -->
          <div class="form-section">
            <div class="form-section-title">💰 费用信息</div>
            <div class="form-row">
              <div class="form-item">
                <label>是否报关</label>
                <el-checkbox v-model="form.is_customs">是</el-checkbox>
              </div>
              <div class="form-item">
                <label>KG单价</label>
                <el-input-number v-model="form.kg_price" :min="0" :precision="2" controls-position="right" style="width: 100%;"></el-input-number>
              </div>
              <div class="form-item">
                <label>业务编号 <span class="form-hint">（可选）</span></label>
                <el-select 
                  v-model="form.business_no" 
                  placeholder="请选择业务编号" 
                  clearable 
                  filterable
                  style="width:100%"
                >
                  <el-option 
                    v-for="biz in businessList" 
                    :key="biz.id" 
                    :label="`${biz.business_no} - ${biz.business_type_name}`" 
                    :value="biz.business_no"
                  >
                    <span style="float: left">{{ biz.business_no }}</span>
                    <span style="float: right; color: #8492a6; font-size: 13px">{{ biz.business_type_name }}</span>
                  </el-option>
                </el-select>
              </div>
              <div class="form-item">
                <label>体积单价</label>
                <el-input-number v-model="form.volume_price" :min="0" :precision="2" controls-position="right" style="width: 100%;"></el-input-number>
              </div>
            </div>
          </div>

          <!-- 5. 物流信息 -->
          <div class="form-section">
            <div class="form-section-title">🚢 物流信息</div>
            <div class="form-row">
              <div class="form-item">
                <label>船名航次</label>
                <el-input v-model="form.vessel_voyage" placeholder="如：COSCO/2105"></el-input>
              </div>
              <div class="form-item">
                <label>品名</label>
                <el-input v-model="form.product_name" placeholder="货物名称"></el-input>
              </div>
              <div class="form-item">
                <label>FBA号</label>
                <el-input v-model="form.fba_no" placeholder="亚马逊编号"></el-input>
              </div>
            </div>
            <div class="form-row">
              <div class="form-item">
                <label>预计入库时间</label>
                <el-date-picker 
                  v-model="form.expected_arrival" 
                  type="date" 
                  placeholder="选择日期" 
                  value-format="YYYY-MM-DD" 
                  style="width: 100%;"
                ></el-date-picker>
              </div>
              <div class="form-item">
                <label style="visibility: hidden;">选项</label>
                <div style="display: flex; gap: 24px; align-items: center; height: 40px;">
                  <el-checkbox v-model="form.is_non_standard">非标货</el-checkbox>
                  <el-checkbox v-model="form.generate_bill">生成账单</el-checkbox>
                </div>
              </div>
            </div>
          </div>

          <!-- 6. 备注信息 -->
          <div class="form-section">
            <div class="form-section-title">📝 备注信息</div>
            <div class="form-row">
              <div class="form-item">
                <label>入仓单备注</label>
                <el-input v-model="form.warehouse_note" type="textarea" :rows="2" placeholder="入仓注意事项"></el-input>
              </div>
            </div>
            <div class="form-row">
              <div class="form-item">
                <label>订单备注</label>
                <el-input v-model="form.order_note" type="textarea" :rows="2" placeholder="其他备注"></el-input>
              </div>
            </div>
            <div class="form-row">
              <div class="form-item">
                <label>派送预约要求</label>
                <el-input v-model="form.delivery_requirement" type="textarea" :rows="2" placeholder="预约要求"></el-input>
              </div>
            </div>
          </div>

          <!-- 按钮 -->
          <div class="button-group">
            <el-button @click="resetForm">清空</el-button>
            <el-button type="primary" @click="submitForm" :loading="loading">
              {{ loading ? '保存中...' : '💾 保存' }}
            </el-button>
          </div>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const businessList = ref([])  // 业务编号列表
const form = reactive({
  customer_name: '',
  order_no: '',
  channel: '',
  warehouse: '铁士',
  boxes: 0,
  total_weight: 0,
  cbm: 0,
  warehouse_code: '',
  receiver_name: '',
  address1: '',
  address2: '',
  city: '',
  state: '',
  zip_code: '',
  phone: '',
  phone2: '',
  is_customs: false,
  kg_price: null,
  business_no: '',  // 业务编号
  vessel_voyage: '',
  volume_price: null,
  volume_ratio: null,
  product_name: '',
  fba_no: '',
  is_non_standard: false,
  expected_arrival: '',
  warehouse_note: '',
  order_note: '',
  delivery_requirement: '',
  generate_bill: false
})

const customers = ref([])

// 查询客户联想
const querySearch = (queryString, cb) => {
  const results = queryString 
    ? customers.value.filter(c => c.value.toLowerCase().includes(queryString.toLowerCase())) 
    : customers.value
  cb(results)
}

// 加载客户列表
const loadCustomers = async () => {
  try {
    const res = await fetch('http://127.0.0.1:8000/api/customers')
    const data = await res.json()
    customers.value = Array.isArray(data) ? data.map(c => ({ value: c.customer_name })) : []
  } catch (e) {
    console.error('加载客户失败:', e)
    customers.value = []
  }
}

// ✅ 加载业务编号列表
const loadBusinessList = async () => {
  try {
    const res = await fetch('http://127.0.0.1:8000/api/business')
    const data = await res.json()
    businessList.value = Array.isArray(data) ? data : []
    console.log('📦 加载业务编号列表:', businessList.value.length, '条')
  } catch (e) {
    console.error('加载业务编号失败:', e)
    businessList.value = []
  }
}

// ✅ 修复后的提交表单
const submitForm = async () => {
  // 只验证客户，订单号可以为空（自动生成）
  if (!form.customer_name) {
    return ElMessage.warning('请填写客户')
  }
  
  loading.value = true
  try {
    // 获取当前登录用户信息
    const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
    const creatorId = userInfo.id || userInfo.username || '未知'
    
    // 准备提交的数据
    const submitData = {
      ...form,
      created_by: creatorId,
      // 如果订单号为空字符串，改为 null 或不传
      order_no: form.order_no?.trim() || null
    }
    
    const res = await fetch('http://127.0.0.1:8000/api/orders', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(submitData)
    })
    
    if (res.ok) {
      const result = await res.json()
      // 显示生成的订单号
      ElMessage.success(`✅ 保存成功！订单号：${result.order_no}`)
      resetForm()
    } else {
      const result = await res.json()
      ElMessage.error('❌ ' + (result.detail || '保存失败'))
    }
  } catch (e) {
    console.error('提交错误:', e)
    ElMessage.error('❌ 网络错误')
  }
  loading.value = false
}

// 重置表单
const resetForm = () => {
  Object.assign(form, {
    customer_name: '',
    order_no: '',
    channel: '',
    warehouse: '铁士',
    boxes: 0,
    total_weight: 0,
    cbm: 0,
    warehouse_code: '',
    receiver_name: '',
    address1: '',
    address2: '',
    city: '',
    state: '',
    zip_code: '',
    phone: '',
    phone2: '',
    is_customs: false,
    kg_price: null,
    business_no: '',
    vessel_voyage: '',
    volume_price: null,
    volume_ratio: null,
    product_name: '',
    fba_no: '',
    is_non_standard: false,
    expected_arrival: '',
    warehouse_note: '',
    order_note: '',
    delivery_requirement: '',
    generate_bill: false
  })
}

// 页面挂载时检查是否有待编辑的订单数据
onMounted(() => {
  const editingData = localStorage.getItem('editingOrder')
  if (editingData) {
    try {
      const data = JSON.parse(editingData)
      Object.assign(form, data)
      localStorage.removeItem('editingOrder')
      ElMessage.info('✅ 已加载订单数据，修改后点击保存即可覆盖')
    } catch (e) {
      console.error('解析编辑数据失败', e)
    }
  }
  loadCustomers()
  loadBusinessList()  // 加载业务编号列表
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

.form-section {
  margin-bottom: 32px;
  padding-bottom: 28px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.form-section:last-of-type {
  border-bottom: none;
}

.form-section-title {
  font-size: 13px;
  font-weight: 700;
  color: #007AFF;
  margin-bottom: 24px;
  text-transform: uppercase;
  letter-spacing: 0.8px;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.form-item label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #3a3a3c;
  font-weight: 600;
}

.form-item .required::before {
  content: '*';
  color: #FF3B30;
  margin-right: 4px;
}

.form-hint {
  font-size: 11px;
  color: #FF3B30;
  margin-left: 5px;
}

.button-group {
  display: flex;
  gap: 14px;
  justify-content: flex-end;
  margin-top: 32px;
  padding-top: 28px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}

:deep(.el-input__wrapper),
:deep(.el-select .el-input__wrapper) {
  border-radius: 12px;
  box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.08) inset;
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px #007AFF inset;
}

:deep(.el-button--primary) {
  background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%) !important;
  border: none !important;
  border-radius: 12px !important;
  padding: 12px 32px !important;
  font-weight: 600 !important;
}
</style>