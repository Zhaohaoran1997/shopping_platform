<template>
  <div class="return-detail">
    <div class="page-header">
      <h2>退换货详情</h2>
      <el-button @click="router.back()">返回</el-button>
    </div>

    <el-card v-loading="loading" class="detail-card">
      <template #header>
        <div class="card-header">
          <span>退换货详情</span>
          <el-tag :type="getStatusType(returnDetail.status)">
            {{ returnDetail.status_display }}
          </el-tag>
        </div>
      </template>

      <el-descriptions :column="2" border>
        <el-descriptions-item label="订单号">
          {{ returnDetail.order_number }}
        </el-descriptions-item>
        <el-descriptions-item label="商品名称">
          {{ returnDetail.product_name }}
        </el-descriptions-item>
        <el-descriptions-item label="商品单价">
          ¥{{ returnDetail.product_price }}
        </el-descriptions-item>
        <el-descriptions-item label="退货数量">
          {{ returnDetail.quantity }}
        </el-descriptions-item>
        <el-descriptions-item label="退货总价">
          ¥{{ returnDetail.total_price }}
        </el-descriptions-item>
        <el-descriptions-item label="优惠金额">
          ¥{{ returnDetail.discount_amount }}
        </el-descriptions-item>
        <el-descriptions-item label="实际退款金额">
          ¥{{ returnDetail.actual_amount }}
        </el-descriptions-item>
        <el-descriptions-item label="退换货类型">
          {{ returnDetail.type_display }}
        </el-descriptions-item>
        <el-descriptions-item label="申请原因">
          {{ getReasonDisplay(returnDetail.reason) }}
        </el-descriptions-item>
        <el-descriptions-item label="问题描述" :span="2">
          {{ returnDetail.description || '无' }}
        </el-descriptions-item>
        <el-descriptions-item label="申请时间">
          {{ returnDetail.created_at }}
        </el-descriptions-item>
        <el-descriptions-item label="更新时间">
          {{ returnDetail.updated_at }}
        </el-descriptions-item>
      </el-descriptions>

      <div v-if="returnDetail.images && returnDetail.images.length > 0" class="image-section">
        <h3>退换货图片</h3>
        <el-image-viewer
          v-if="showViewer"
          :on-close="closeViewer"
          :url-list="imageList"
          :initial-index="currentImageIndex"
        />
        <div class="image-list">
          <el-image
            v-for="(image, index) in returnDetail.images"
            :key="index"
            :src="image.image"
            :preview-src-list="imageList"
            fit="cover"
            class="return-image"
            @click="showImageViewer(index)"
          />
        </div>
      </div>

      <div v-if="returnDetail.status === 3" class="shipping-info">
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

      <div v-if="returnDetail.shipping_no" class="shipping-details">
        <h3>物流信息</h3>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="物流单号">
            {{ returnDetail.shipping_no }}
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
import { getReturnDetail } from '@/api/returns'

const router = useRouter()
const route = useRoute()
const loading = ref(false)
const returnDetail = ref({})
const shippingFormRef = ref(null)
const showViewer = ref(false)
const currentImageIndex = ref(0)
const imageList = ref([])

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
    0: 'warning',  // 待审核
    1: 'success',  // 已通过
    2: 'danger',   // 已拒绝
    3: 'info'      // 已完成
  }
  return types[status] || 'info'
}

const getReasonDisplay = (reason) => {
  const reasons = {
    quality: '质量问题',
    wrong: '发错商品',
    damage: '商品损坏',
    other: '其他原因'
  }
  return reasons[reason] || reason
}

const showImageViewer = (index) => {
  currentImageIndex.value = index
  showViewer.value = true
}

const closeViewer = () => {
  showViewer.value = false
}

const fetchReturnDetail = async () => {
  try {
    const response = await getReturnDetail(route.params.id)
    console.log('Return detail response:', response)  // 添加调试日志
    returnDetail.value = response.data
    // 更新图片列表
    imageList.value = returnDetail.value.images.map(img => img.image)
  } catch (error) {
    console.error('获取退换货详情失败:', error)
    ElMessage.error('获取退换货详情失败')
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

.image-section {
  margin-top: 20px;
}

.image-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 10px;
}

.return-image {
  width: 100px;
  height: 100px;
  border-radius: 4px;
  cursor: pointer;
}
</style> 