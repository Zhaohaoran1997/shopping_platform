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
            {{ getStatusText(order.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="支付方式">{{ order.payment_method }}</el-descriptions-item>
        <el-descriptions-item label="收货人">{{ order.receiver }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ order.phone }}</el-descriptions-item>
        <el-descriptions-item label="收货地址" :span="2">
          {{ order.province }}{{ order.city }}{{ order.district }}{{ order.address }}
        </el-descriptions-item>
      </el-descriptions>

      <div class="order-items">
        <h3>商品信息</h3>
        <el-table :data="order.items" style="width: 100%">
          <el-table-column label="商品图片" width="120">
            <template #default="scope">
              <el-image 
                :src="scope.row.image_url" 
                :preview-src-list="[scope.row.image_url]"
                fit="cover"
                style="width: 80px; height: 80px"
              />
            </template>
          </el-table-column>
          <el-table-column prop="name" label="商品名称" />
          <el-table-column prop="specification" label="规格" width="120" />
          <el-table-column prop="price" label="单价" width="120">
            <template #default="scope">
              ¥{{ scope.row.price.toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column prop="quantity" label="数量" width="120" />
          <el-table-column label="小计" width="120">
            <template #default="scope">
              ¥{{ (scope.row.price * scope.row.quantity).toFixed(2) }}
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="order-summary">
        <div class="summary-item">
          <span>商品总额：</span>
          <span>¥{{ order.total_amount.toFixed(2) }}</span>
        </div>
        <div class="summary-item">
          <span>运费：</span>
          <span>¥{{ order.shipping_fee.toFixed(2) }}</span>
        </div>
        <div class="summary-item">
          <span>优惠金额：</span>
          <span>-¥{{ order.discount_amount.toFixed(2) }}</span>
        </div>
        <div class="summary-item total">
          <span>实付金额：</span>
          <span class="price">¥{{ order.final_amount.toFixed(2) }}</span>
        </div>
      </div>

      <div class="order-actions" v-if="order.status === 'pending_payment'">
        <el-button type="primary" @click="handlePay">立即支付</el-button>
        <el-button type="danger" @click="handleCancel">取消订单</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { formatDate } from '@/utils/date'
import { getOrderDetail, cancelOrder } from '@/api/order'

const router = useRouter()
const route = useRoute()
const order = ref({
  order_no: '',
  created_at: '',
  status: '',
  payment_method: '',
  receiver: '',
  phone: '',
  province: '',
  city: '',
  district: '',
  address: '',
  items: [],
  total_amount: 0,
  shipping_fee: 0,
  discount_amount: 0,
  final_amount: 0
})

const getStatusType = (status) => {
  const statusMap = {
    pending_payment: 'warning',
    paid: 'success',
    shipped: 'info',
    completed: 'success',
    cancelled: 'danger'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status) => {
  const statusMap = {
    pending_payment: '待支付',
    paid: '已支付',
    shipped: '已发货',
    completed: '已完成',
    cancelled: '已取消'
  }
  return statusMap[status] || '未知状态'
}

const fetchOrderDetail = async () => {
  try {
    const response = await getOrderDetail(route.params.id)
    order.value = response.data
  } catch (error) {
    ElMessage.error('获取订单详情失败')
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