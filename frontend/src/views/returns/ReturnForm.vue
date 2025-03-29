<template>
  <div class="return-form">
    <div class="page-header">
      <h2>申请退换货</h2>
      <el-button @click="router.back()">返回</el-button>
    </div>

    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="120px"
      class="return-form-content"
    >
      <el-form-item label="订单号" prop="order_id">
        <el-select
          v-model="form.order_id"
          placeholder="请选择要退换货的订单"
          filterable
          remote
          :remote-method="searchOrders"
          :loading="loading"
          @change="handleOrderChange"
        >
          <el-option
            v-for="order in orderOptions"
            :key="order.value"
            :label="order.label"
            :value="order.value"
          >
            <span>{{ order.label }}</span>
          </el-option>
        </el-select>
      </el-form-item>

      <el-form-item label="商品" prop="product_id">
        <el-select
          v-model="form.product_id"
          placeholder="请选择要退换货的商品"
          :disabled="!form.order_id"
        >
          <el-option
            v-for="product in productOptions"
            :key="product.value"
            :label="product.label"
            :value="product.value"
          >
            <span>{{ product.label }}</span>
          </el-option>
        </el-select>
      </el-form-item>

      <el-form-item label="退换类型" prop="return_type">
        <el-radio-group v-model="form.return_type">
          <el-radio label="refund">退款</el-radio>
          <el-radio label="exchange">换货</el-radio>
        </el-radio-group>
      </el-form-item>

      <el-form-item label="退换原因" prop="reason">
        <el-select v-model="form.reason" placeholder="请选择退换原因">
          <el-option label="商品质量问题" value="quality" />
          <el-option label="商品与描述不符" value="description" />
          <el-option label="商品损坏" value="damaged" />
          <el-option label="其他原因" value="other" />
        </el-select>
      </el-form-item>

      <el-form-item label="问题描述" prop="description">
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="4"
          placeholder="请详细描述问题"
        />
      </el-form-item>

      <el-form-item label="上传图片" prop="images">
        <el-upload
          class="upload-demo"
          action="/returns/requests/upload/"
          list-type="picture-card"
          :on-preview="handlePictureCardPreview"
          :on-remove="handleRemove"
          :before-upload="beforeUpload"
          multiple
        >
          <el-icon><Plus /></el-icon>
        </el-upload>
        <el-dialog v-model="dialogVisible">
          <img w-full :src="dialogImageUrl" alt="Preview Image" />
        </el-dialog>
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="handleSubmit">提交申请</el-button>
        <el-button @click="router.back()">取消</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import request from '@/utils/request'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)
const orderOptions = ref([])
const productOptions = ref([])
const dialogVisible = ref(false)
const dialogImageUrl = ref('')

const form = reactive({
  order_id: '',
  product_id: '',
  return_type: 'refund',
  reason: '',
  description: '',
  images: []
})

const rules = {
  order_id: [{ required: true, message: '请选择订单', trigger: 'change' }],
  product_id: [{ required: true, message: '请选择商品', trigger: 'change' }],
  return_type: [{ required: true, message: '请选择退换类型', trigger: 'change' }],
  reason: [{ required: true, message: '请选择退换原因', trigger: 'change' }],
  description: [{ required: true, message: '请描述问题', trigger: 'blur' }]
}

const searchOrders = async (query) => {
  if (!query) {
    orderOptions.value = []
    return
  }
  try {
    const response = await request({
      url: '/returns/orders/',
      method: 'get',
      params: {
        search: query
      }
    })
    console.log('Search response:', response)  // 添加调试日志
    orderOptions.value = response.data.results.map(order => ({
      value: order.id,
      label: `${order.order_number} (${order.created_at})`
    }))
  } catch (error) {
    console.error('搜索订单失败:', error)
    ElMessage.error('搜索订单失败')
    orderOptions.value = []
  }
}

const handleOrderChange = async (orderId) => {
  if (!orderId) {
    productOptions.value = []
    form.product_id = ''
    return
  }
  try {
    const response = await request({
      url: `/returns/orders/${orderId}/products/`,
      method: 'get'
    })
    console.log('Order products response:', response)  // 添加调试日志
    productOptions.value = response.data.map(product => ({
      value: product.id,
      label: `${product.name} (¥${product.price})`
    }))
    form.product_id = ''
  } catch (error) {
    console.error('获取订单商品失败:', error)
    ElMessage.error('获取订单商品失败')
    productOptions.value = []
    form.product_id = ''
  }
}

const handlePictureCardPreview = (file) => {
  dialogImageUrl.value = file.url
  dialogVisible.value = true
}

const handleRemove = (file) => {
  const index = form.images.indexOf(file)
  if (index !== -1) {
    form.images.splice(index, 1)
  }
}

const beforeUpload = async (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB!')
    return false
  }

  try {
    const formData = new FormData()
    formData.append('image', file)
    
    const response = await request.post('/returns/requests/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    form.images.push(response.url)
    return false // 阻止默认上传
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || error.message || '上传图片失败')
    return false
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    const response = await request.post('/returns/requests/', {
      order_id: form.order_id,
      product_id: form.product_id,
      type: form.return_type === 'refund' ? 1 : 2,  // 1: 退货, 2: 换货
      reason: form.reason,
      description: form.description,
      images: form.images
    })
    
    ElMessage.success('申请提交成功')
    router.push('/returns')
  } catch (error) {
    console.error('提交退换货申请失败:', error)
    ElMessage.error(error.response?.data?.detail || error.message || '提交申请失败')
  }
}
</script>

<style scoped>
.return-form {
  padding: 20px;
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.return-form-content {
  max-width: 800px;
  margin: 0 auto;
}

.product-option {
  display: flex;
  align-items: center;
  gap: 10px;
}

.product-image {
  width: 50px;
  height: 50px;
  border-radius: 4px;
}

.product-info {
  flex: 1;
}

.product-price {
  color: #f56c6c;
  font-size: 14px;
}

.upload-demo {
  :deep(.el-upload--picture-card) {
    width: 100px;
    height: 100px;
    line-height: 100px;
  }
}
</style> 