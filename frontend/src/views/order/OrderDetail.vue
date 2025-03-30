<template>
  <div class="order-detail">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>订单详情</span>
          <el-button @click="router.back()">返回</el-button>
        </div>
      </template>

      <el-descriptions :column="2" border>
        <el-descriptions-item label="订单编号">{{ order.order_no }}</el-descriptions-item>
        <el-descriptions-item label="下单时间">{{ formatDate(order.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="订单状态">
          <el-tag :type="getStatusType(order.status)">
            {{ order.status_display }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="支付方式">{{ order.payment_method_display }}</el-descriptions-item>
        <el-descriptions-item label="收货人">{{ order.shipping_name }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ order.shipping_phone }}</el-descriptions-item>
        <el-descriptions-item label="收货地址" :span="2">
          {{ order.shipping_province }}{{ order.shipping_city }}{{ order.shipping_district }}{{ order.shipping_address_detail }}
        </el-descriptions-item>
      </el-descriptions>

      <div class="order-items">
        <h3>商品信息</h3>
        <el-table :data="order.items" style="width: 100%">
          <el-table-column label="商品图片" width="120">
            <template #default="scope">
              <el-image 
                :src="scope.row.product_image" 
                :preview-src-list="[scope.row.product_image]"
                fit="cover"
                style="width: 80px; height: 80px"
              />
            </template>
          </el-table-column>
          <el-table-column prop="product_name" label="商品名称" />
          <el-table-column label="规格" width="200">
            <template #default="scope">
              <div v-for="spec in scope.row.product.specifications" :key="spec.id">
                {{ spec.name }}：{{ spec.value }}
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="price" label="单价" width="120">
            <template #default="scope">
              ¥{{ scope.row.price }}
            </template>
          </el-table-column>
          <el-table-column prop="quantity" label="数量" width="120" />
          <el-table-column prop="total_price" label="小计" width="120">
            <template #default="scope">
              ¥{{ scope.row.total_price }}
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="order-summary">
        <div class="summary-item">
          <span>商品总额：</span>
          <span>¥{{ order.total_amount }}</span>
        </div>
        <div class="summary-item">
          <span>运费：</span>
          <span>¥{{ order.shipping_fee }}</span>
        </div>
        <div class="summary-item">
          <span>优惠金额：</span>
          <span>-¥{{ order.discount_amount }}</span>
        </div>
        <div class="summary-item total">
          <span>实付金额：</span>
          <span class="price">¥{{ order.final_amount }}</span>
        </div>
      </div>

      <div class="order-actions" v-if="order.status === 0">
        <el-button type="primary" @click="handlePay">立即支付</el-button>
        <el-button type="danger" @click="handleCancel">取消订单</el-button>
      </div>
      <div class="order-actions" v-if="order.status === 2">
        <el-button type="success" @click="handleConfirmReceive">确认收货</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { formatDate } from '@/utils/date'
import { getOrderDetail, cancelOrder, confirmReceive } from '@/api/order'

const router = useRouter()
const route = useRoute()
const order = ref({
  order_no: '',
  created_at: '',
  status: 0,
  status_display: '',
  payment_method: '',
  payment_method_display: '',
  shipping_name: '',
  shipping_phone: '',
  shipping_province: '',
  shipping_city: '',
  shipping_district: '',
  shipping_address_detail: '',
  items: [],
  total_amount: '0.00',
  shipping_fee: '0.00',
  discount_amount: '0.00',
  final_amount: '0.00'
})

const getStatusType = (status) => {
  const statusMap = {
    0: 'warning',   // 待付款
    1: 'primary',   // 待发货
    2: 'success',   // 待收货
    3: 'info',      // 已完成
    4: 'danger'     // 已取消
  }
  return statusMap[status] || 'info'
}

const fetchOrderDetail = async () => {
  try {
    console.log('Fetching order detail for ID:', route.params.id)
    const response = await getOrderDetail(route.params.id)
    console.log('Raw API Response:', response)

    // 检查响应数据
    if (!response || !response.results || response.results.length === 0) {
      throw new Error('未找到订单信息')
    }

    // 获取第一个订单数据
    const orderData = response.results[0]
    console.log('Order data before processing:', orderData)
    
    // 确保所有必需的字段都有默认值
    order.value = {
      order_no: '',
      created_at: '',
      status: 0,
      status_display: '',
      payment_method: '',
      payment_method_display: '',
      shipping_name: '',
      shipping_phone: '',
      shipping_province: '',
      shipping_city: '',
      shipping_district: '',
      shipping_address_detail: '',
      items: [],
      total_amount: '0.00',
      shipping_fee: '0.00',
      discount_amount: '0.00',
      final_amount: '0.00',
      ...orderData
    }
    
    console.log('Final processed order data:', order.value)
    console.log('Order items:', order.value.items)
    console.log('Order status:', order.value.status)
    console.log('Order total amount:', order.value.total_amount)
  } catch (error) {
    console.error('获取订单详情失败:', error)
    console.error('错误详情:', {
      message: error.message,
      stack: error.stack,
      response: error.response
    })
    ElMessage.error(error.message || '获取订单详情失败')
  }
}

const handlePay = () => {
  router.push(`/order/payment/${route.params.id}`)
}

const handleCancel = async () => {
  try {
    await ElMessageBox.confirm('确定要取消该订单吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await cancelOrder(route.params.id)
    ElMessage.success('订单已取消')
    router.push('/order/list')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('取消订单失败')
    }
  }
}

const handleConfirmReceive = async () => {
  try {
    await ElMessageBox.confirm('确认已收到商品？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await confirmReceive(route.params.id)
    ElMessage.success('确认收货成功')
    router.push('/order/list')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('确认收货失败')
    }
  }
}

onMounted(() => {
  fetchOrderDetail()
})
</script>

<style scoped>
.order-detail {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.order-items {
  margin-top: 20px;
}

.order-summary {
  margin-top: 20px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.summary-item {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 10px;
}

.summary-item.total {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #dcdfe6;
  font-weight: bold;
}

.summary-item .price {
  color: #f56c6c;
  font-size: 18px;
}

.order-actions {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style> 