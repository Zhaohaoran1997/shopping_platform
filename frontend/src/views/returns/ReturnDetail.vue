<template>
  <div class="return-detail">
    <div class="page-header">
      <h2>退换货详情</h2>
      <el-button @click="router.back()">返回</el-button>
    </div>

    <el-card v-loading="loading" class="detail-card">
      <template #header>
        <div class="card-header">
          <span>申请编号：{{ returnData.id }}</span>
          <el-tag :type="getStatusType(returnData.status)">
            {{ getStatusText(returnData.status) }}
          </el-tag>
        </div>
      </template>

      <el-descriptions :column="2" border>
        <el-descriptions-item label="订单号">
          {{ returnData.order?.order_no }}
        </el-descriptions-item>
        <el-descriptions-item label="申请时间">
          {{ returnData.created_at }}
        </el-descriptions-item>
        <el-descriptions-item label="退换类型">
          <el-tag :type="returnData.type === 1 ? 'danger' : 'warning'">
            {{ returnData.type_display }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="退换原因">
          {{ returnData.reason }}
        </el-descriptions-item>
      </el-descriptions>

      <div class="product-info">
        <h3>商品信息</h3>
        <div v-for="item in returnData.order?.items" :key="item.id" class="product-card">
          <el-image
            :src="item.product_image"
            :preview-src-list="[item.product_image]"
            fit="cover"
            class="product-image"
          />
          <div class="product-details">
            <h4>{{ item.product_name }}</h4>
            <p class="price">¥{{ item.price }}</p>
            <p class="quantity">数量：{{ item.quantity }}</p>
            <p class="total-price">总价：¥{{ item.total_price }}</p>
            <div v-if="item.product.specifications?.length" class="specifications">
              <p v-for="spec in item.product.specifications" :key="spec.id">
                {{ spec.name }}：{{ spec.value }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div class="description-section">
        <h3>订单信息</h3>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="收货人">
            {{ returnData.order?.shipping_name }}
          </el-descriptions-item>
          <el-descriptions-item label="联系电话">
            {{ returnData.order?.shipping_phone }}
          </el-descriptions-item>
          <el-descriptions-item label="收货地址">
            {{ returnData.order?.shipping_province }}{{ returnData.order?.shipping_city }}{{ returnData.order?.shipping_district }}{{ returnData.order?.shipping_address_detail }}
          </el-descriptions-item>
          <el-descriptions-item label="支付方式">
            {{ returnData.order?.payment_method === 'alipay' ? '支付宝' : '微信支付' }}
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <div v-if="returnData.images?.length" class="images-section">
        <h3>问题图片</h3>
        <el-image
          v-for="(image, index) in returnData.images"
          :key="index"
          :src="image"
          :preview-src-list="returnData.images"
          fit="cover"
          class="problem-image"
        />
      </div>

      <div v-if="returnData.status === 3" class="shipping-info">
        <h3>物流信息</h3>
        <el-form
          ref="shippingFormRef"
          :model="shippingForm"
          :rules="shippingRules"
          label-width="100px"
        >
          <el-form-item label="物流公司" prop="shipping_company">
            <el-select v-model="shippingForm.shipping_company" placeholder="请选择物流公司">
              <el-option label="顺丰速运" value="SF" />
              <el-option label="中通快递" value="ZTO" />
              <el-option label="圆通速递" value="YTO" />
              <el-option label="韵达快递" value="YD" />
            </el-select>
          </el-form-item>
          <el-form-item label="物流单号" prop="tracking_number">
            <el-input v-model="shippingForm.tracking_number" placeholder="请输入物流单号" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSubmitShipping">提交物流信息</el-button>
          </el-form-item>
        </el-form>
      </div>

      <div v-if="returnData.order?.shipping_no" class="shipping-details">
        <h3>物流信息</h3>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="物流单号">
            {{ returnData.order.shipping_no }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const router = useRouter()
const route = useRoute()
const loading = ref(false)
const returnData = ref({})
const shippingFormRef = ref(null)

const shippingForm = ref({
  shipping_company: '',
  tracking_number: ''
})

const shippingRules = {
  shipping_company: [{ required: true, message: '请选择物流公司', trigger: 'change' }],
  tracking_number: [{ required: true, message: '请输入物流单号', trigger: 'blur' }]
}

const getStatusType = (status) => {
  const types = {
    1: 'warning',    // 待处理
    2: 'danger',     // 已拒绝
    3: 'primary',    // 已通过
    4: 'success'     // 已完成
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    1: '待处理',
    2: '已拒绝',
    3: '已通过',
    4: '已完成'
  }
  return texts[status] || status
}

const getReasonText = (reason) => {
  const texts = {
    quality: '商品质量问题',
    description: '商品与描述不符',
    damaged: '商品损坏',
    other: '其他原因'
  }
  return texts[reason] || reason
}

const getShippingCompanyText = (company) => {
  const texts = {
    SF: '顺丰速运',
    ZTO: '中通快递',
    YTO: '圆通速递',
    YD: '韵达快递'
  }
  return texts[company] || company
}

const fetchReturnDetail = async () => {
  loading.value = true
  try {
    const response = await request({
      url: `/returns/requests/${route.params.id}/`,
      method: 'get'
    })
    returnData.value = response
  } catch (error) {
    console.error('获取退换货详情失败:', error)
    ElMessage.error(error.message || '获取退换货详情失败')
  } finally {
    loading.value = false
  }
}

const handleSubmitShipping = async () => {
  if (!shippingFormRef.value) return
  
  try {
    await shippingFormRef.value.validate()
    
    await request({
      url: `/returns/requests/${route.params.id}/shipping/`,
      method: 'post',
      data: shippingForm.value
    })
    
    ElMessage.success('物流信息提交成功')
    fetchReturnDetail()
  } catch (error) {
    console.error('提交物流信息失败:', error)
    ElMessage.error(error.message || '提交物流信息失败')
  }
}

onMounted(() => {
  fetchReturnDetail()
})
</script>

<style scoped>
.return-detail {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.detail-card {
  max-width: 1000px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.product-info {
  margin-top: 20px;
}

.product-card {
  display: flex;
  gap: 20px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
  margin-top: 10px;
}

.product-image {
  width: 100px;
  height: 100px;
  border-radius: 4px;
}

.product-details {
  flex: 1;
}

.price {
  color: #f56c6c;
  font-size: 18px;
  margin-top: 10px;
}

.description-section,
.images-section,
.shipping-info,
.shipping-details {
  margin-top: 20px;
}

.problem-image {
  width: 150px;
  height: 150px;
  margin-right: 10px;
  margin-bottom: 10px;
  border-radius: 4px;
}

.shipping-info {
  max-width: 500px;
}
</style> 