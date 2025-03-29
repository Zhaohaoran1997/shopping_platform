<template>
  <div class="address-container">
    <el-card class="address-card">
      <template #header>
        <div class="card-header">
          <h2>收货地址管理</h2>
          <el-button type="primary" @click="handleAdd">
            添加新地址
          </el-button>
        </div>
      </template>

      <el-table :data="addresses" style="width: 100%">
        <el-table-column prop="receiver" label="收货人" width="120" />
        <el-table-column prop="phone" label="联系电话" width="120" />
        <el-table-column label="收货地址">
          <template #default="{ row }">
            {{ row.province }}{{ row.city }}{{ row.district }}{{ row.address }}
          </template>
        </el-table-column>
        <el-table-column prop="is_default" label="默认地址" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.is_default" type="success">默认</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button type="primary" link @click="handleSetDefault(row)">
              设为默认
            </el-button>
            <el-button type="danger" link @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加/编辑地址对话框 -->
    <el-dialog
      v-model="showAddDialog"
      :title="editingAddress ? '编辑地址' : '添加新地址'"
      width="500px"
    >
      <el-form
        ref="addressFormRef"
        :model="addressForm"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="收货人" prop="receiver">
          <el-input v-model="addressForm.receiver" />
        </el-form-item>
        <el-form-item label="联系电话" prop="phone">
          <el-input v-model="addressForm.phone" />
        </el-form-item>
        <el-form-item label="所在地区" prop="region">
          <div class="region-inputs">
            <el-input v-model="addressForm.province" placeholder="省份" />
            <el-input v-model="addressForm.city" placeholder="城市" />
            <el-input v-model="addressForm.district" placeholder="区县" />
          </div>
        </el-form-item>
        <el-form-item label="详细地址" prop="address">
          <el-input
            v-model="addressForm.address"
            type="textarea"
            :rows="2"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAddDialog = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from '@/utils/axios'

const authStore = useAuthStore()
const addresses = ref([])
const addressFormRef = ref(null)
const editingAddress = ref(null)
const showAddDialog = ref(false)

const addressForm = reactive({
  receiver: '',
  phone: '',
  province: '',
  city: '',
  district: '',
  address: ''
})

// 表单验证规则
const rules = {
  receiver: [
    { required: true, message: '请输入收货人姓名', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入联系电话', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  province: [
    { required: true, message: '请输入省份', trigger: 'blur' }
  ],
  city: [
    { required: true, message: '请输入城市', trigger: 'blur' }
  ],
  district: [
    { required: true, message: '请输入区县', trigger: 'blur' }
  ],
  address: [
    { required: true, message: '请输入详细地址', trigger: 'blur' }
  ]
}

// 重置表单
const resetForm = () => {
  if (addressFormRef.value) {
    addressFormRef.value.resetFields()
  }
  editingAddress.value = null
  addressForm.receiver = ''
  addressForm.phone = ''
  addressForm.province = ''
  addressForm.city = ''
  addressForm.district = ''
  addressForm.address = ''
}

// 获取地址列表
const fetchAddresses = async () => {
  try {
    const response = await axios.get(`/users/${authStore.user.id}/addresses/`)
    // 从分页响应中提取地址数组
    addresses.value = response.data.results || []
  } catch (error) {
    ElMessage.error('获取地址列表失败')
  }
}

// 添加新地址
const handleAdd = () => {
  resetForm()
  showAddDialog.value = true
}

// 编辑地址
const handleEdit = (address) => {
  editingAddress.value = address
  addressForm.receiver = address.receiver
  addressForm.phone = address.phone
  addressForm.province = address.province
  addressForm.city = address.city
  addressForm.district = address.district
  addressForm.address = address.address
  showAddDialog.value = true
}

// 设置默认地址
const handleSetDefault = async (address) => {
  try {
    await axios.post(`/users/${authStore.user.id}/addresses/${address.id}/set_default/`)
    ElMessage.success('设置默认地址成功')
    fetchAddresses()
  } catch (error) {
    ElMessage.error('设置默认地址失败')
  }
}

// 删除地址
const handleDelete = async (address) => {
  try {
    await ElMessageBox.confirm('确定要删除这个地址吗？', '提示', {
      type: 'warning'
    })
    await axios.delete(`/users/${authStore.user.id}/addresses/${address.id}/`)
    ElMessage.success('删除地址成功')
    fetchAddresses()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除地址失败')
    }
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!addressFormRef.value) return
  
  try {
    await addressFormRef.value.validate()
    
    const addressData = {
      receiver: addressForm.receiver,
      phone: addressForm.phone,
      province: addressForm.province,
      city: addressForm.city,
      district: addressForm.district,
      address: addressForm.address
    }
    
    if (editingAddress.value) {
      await axios.put(`/users/${authStore.user.id}/addresses/${editingAddress.value.id}/`, addressData)
      ElMessage.success('更新地址成功')
    } else {
      await axios.post(`/users/${authStore.user.id}/addresses/`, addressData)
      ElMessage.success('添加地址成功')
    }
    
    showAddDialog.value = false
    resetForm()
    fetchAddresses()
  } catch (error) {
    if (error.response?.data) {
      ElMessage.error(error.response.data.error || '操作失败')
    } else {
      ElMessage.error('表单验证失败，请检查输入')
    }
  }
}

// 监听对话框关闭
watch(showAddDialog, (newVal) => {
  if (!newVal) {
    resetForm()
  }
})

onMounted(() => {
  fetchAddresses()
})
</script>

<style scoped>
.address-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  color: #303133;
}

.region-inputs {
  display: flex;
  gap: 10px;
}

.region-inputs .el-input {
  flex: 1;
}

.address-actions {
  display: flex;
  gap: 10px;
}

.default-badge {
  margin-left: 10px;
  color: #409EFF;
}
</style> 