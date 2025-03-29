<template>
  <div class="order-payment">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>订单支付</span>
          <el-button @click="router.back()">返回</el-button>
        </div>
      </template>

      <div class="payment-info">
        <el-result
          :icon="paymentStatus === 'success' ? 'success' : 'warning'"
          :title="getPaymentStatusTitle"
          :sub-title="getPaymentStatusSubTitle"
        >
          <template #extra>
            <div class="payment-amount">
              <span class="label">支付金额：</span>
              <span class="amount">¥{{ order?.final_amount?.toFixed(2) || '0.00' }}</span>
            </div>
            <div class="payment-actions">
              <el-button 
                v-if="paymentStatus === 'pending'"
                type="primary" 
                @click="handlePay"
                :loading="paying"
              >
                立即支付
              </el-button>
              <el-button 
                v-if="paymentStatus === 'success'"
                type="primary" 
                @click="handleViewOrder"
              >
                查看订单
              </el-button>
              <el-button 
                v-if="paymentStatus === 'pending'"
                @click="handleCancel"
              >
                取消支付
              </el-button>
            </div>
          </template>
        </el-result>

        <!-- 支付方式 -->
        <div v-if="paymentStatus === 'pending'" class="payment-method">
          <div class="section-title">选择支付方式</div>
          <el-radio-group v-model="paymentMethod">
            <el-radio-button label="alipay">
              <img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSI0OCIgdmlld0JveD0iMCAwIDQ4IDQ4Ij48cGF0aCBmaWxsPSIjMTY3N0ZGIiBkPSJNMzMuMDY0IDI0LjQ4OGwtNS4yOTYtNS4yOTZjLS43ODQtLjc4NC0yLjA0OC0uNzg0LTIuODMyIDBsLTUuMjk2IDUuMjk2Yy0uNzg0Ljc4NC0uNzg0IDIuMDQ4IDAgMi44MzJsNS4yOTYgNS4yOTZjLjM5Mi4zOTIuOTA0LjU4OCAxLjQxNi41ODhzMS4wMjQtLjE5NiAxLjQxNi0uNTg4bDUuMjk2LTUuMjk2Yy43ODQtLjc4NC43ODQtMi4wNDggMC0yLjgzMnpNMjQgMGMtMTMuMjU1IDAtMjQgMTAuNzQ1LTI0IDI0czEwLjc0NSAyNCAyNCAyNCAyNC0xMC43NDUgMjQtMjRTMzcuMjU1IDAgMjQgMHoiLz48L3N2Zz4=" alt="支付宝" class="payment-icon">
              支付宝
            </el-radio-button>
            <el-radio-button label="wechat">
              <img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSI0OCIgdmlld0JveD0iMCAwIDQ4IDQ4Ij48cGF0aCBmaWxsPSIjMDdDMTYwIiBkPSJNMzMuMDY0IDI0LjQ4OGwtNS4yOTYtNS4yOTZjLS43ODQtLjc4NC0yLjA0OC0uNzg0LTIuODMyIDBsLTUuMjk2IDUuMjk2Yy0uNzg0Ljc4NC0uNzg0IDIuMDQ4IDAgMi44MzJsNS4yOTYgNS4yOTZjLjM5Mi4zOTIuOTA0LjU4OCAxLjQxNi41ODhzMS4wMjQtLjE5NiAxLjQxNi0uNTg4bDUuMjk2LTUuMjk2Yy43ODQtLjc4NC43ODQtMi4wNDggMC0yLjgzMnpNMjQgMGMtMTMuMjU1IDAtMjQgMTAuNzQ1LTI0IDI0czEwLjc0NSAyNCAyNCAyNCAyNC0xMC43NDUgMjQtMjRTMzcuMjU1IDAgMjQgMHoiLz48L3N2Zz4=" alt="微信支付" class="payment-icon">
              微信支付
            </el-radio-button>
          </el-radio-group>
        </div>

        <!-- 支付二维码 -->
        <div v-if="showQRCode" class="payment-qrcode">
          <div class="section-title">扫码支付</div>
          <div class="qrcode-container">
            <img :src="qrCodeUrl" alt="支付二维码" class="qrcode">
            <p class="qrcode-tip">请使用{{ paymentMethod === 'alipay' ? '支付宝' : '微信' }}扫码支付</p>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getOrderDetail, payOrder, getPaymentStatus, cancelOrder } from '@/api/order'

const router = useRouter()
const route = useRoute()
const paying = ref(false)
const paymentStatus = ref('pending') // pending, success, failed
const paymentMethod = ref('alipay')
const showQRCode = ref(false)
const qrCodeUrl = ref('')
const order = ref({
  id: '',
  order_no: '',
  final_amount: 0,
  status: 0
})

const getPaymentStatusTitle = computed(() => {
  const statusMap = {
    pending: '等待支付',
    success: '支付成功',
    failed: '支付失败'
  }
  return statusMap[paymentStatus.value] || '未知状态'
})

const getPaymentStatusSubTitle = computed(() => {
  const statusMap = {
    pending: '请在30分钟内完成支付',
    success: '您的订单已支付成功',
    failed: '支付过程中出现错误，请重试'
  }
  return statusMap[paymentStatus.value] || ''
})

// 轮询支付状态
let paymentTimer = null

const startPaymentStatusCheck = () => {
  paymentTimer = setInterval(async () => {
    try {
      const response = await getPaymentStatus(route.params.id)
      if (response.data.status === 'success') {
        clearInterval(paymentTimer)
        paymentStatus.value = 'success'
        ElMessage.success('支付成功')
      } else if (response.data.status === 'failed') {
        clearInterval(paymentTimer)
        paymentStatus.value = 'failed'
        ElMessage.error('支付失败')
      }
    } catch (error) {
      console.error('获取支付状态失败:', error)
    }
  }, 2000)
}

const handlePay = async () => {
  if (!paymentMethod.value) {
    ElMessage.warning('请选择支付方式')
    return
  }

  paying.value = true
  try {
    const response = await payOrder(route.params.id, {
      payment_method: paymentMethod.value
    })
    
    // 支付成功
    paymentStatus.value = 'success'
    ElMessage.success('支付成功')
    
    // 3秒后跳转到订单列表
    setTimeout(() => {
      router.push('/order/list')
    }, 3000)
  } catch (error) {
    paymentStatus.value = 'failed'
    ElMessage.error(error.response?.data?.detail || '支付失败')
  } finally {
    paying.value = false
  }
}

const handleCancel = async () => {
  try {
    await cancelOrder(route.params.id)
    ElMessage.success('已取消支付')
    router.push('/order/list')
  } catch (error) {
    ElMessage.error('取消支付失败')
  }
}

const handleViewOrder = () => {
  router.push(`/order/detail/${order.value.id}`)
}

// 初始化数据
const initData = async () => {
  try {
    const response = await getOrderDetail(route.params.id)
    order.value = response.data
  } catch (error) {
    ElMessage.error('获取订单信息失败')
  }
}

onMounted(() => {
  initData()
})

onUnmounted(() => {
  if (paymentTimer) {
    clearInterval(paymentTimer)
  }
})
</script>

<style scoped>
.order-payment {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.payment-info {
  padding: 20px;
}

.payment-amount {
  margin: 20px 0;
  text-align: center;
}

.payment-amount .label {
  font-size: 16px;
  color: #606266;
}

.payment-amount .amount {
  font-size: 24px;
  color: #f56c6c;
  font-weight: bold;
  margin-left: 10px;
}

.payment-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 20px;
}

.section-title {
  font-size: 16px;
  font-weight: bold;
  margin: 20px 0 10px;
  padding-left: 10px;
  border-left: 4px solid #409eff;
}

.payment-method {
  margin-top: 30px;
}

.payment-icon {
  width: 24px;
  height: 24px;
  margin-right: 8px;
  vertical-align: middle;
}

.payment-qrcode {
  margin-top: 30px;
}

.qrcode-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 20px;
}

.qrcode {
  width: 200px;
  height: 200px;
  margin-bottom: 20px;
}

.qrcode-tip {
  color: #909399;
  font-size: 14px;
}
</style> 