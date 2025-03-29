<template>
  <div class="order-create">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>确认订单</span>
        </div>
      </template>

      <el-form :model="orderForm" label-width="100px">
        <!-- 收货地址 -->
        <div class="section-title">收货地址</div>
        <el-form-item label="收货地址">
          <el-select v-model="orderForm.address_id" placeholder="请选择收货地址">
            <el-option
              v-for="address in addresses"
              :key="address.id"
              :label="formatAddress(address)"
              :value="address.id"
            />
          </el-select>
          <el-button type="primary" link @click="showAddressDialog = true">
            添加新地址
          </el-button>
        </el-form-item>

        <!-- 商品信息 -->
        <div class="section-title">商品信息</div>
        <el-table :data="orderForm.items" style="width: 100%">
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

        <!-- 优惠券 -->
        <div class="section-title">优惠券</div>
        <el-form-item label="优惠券">
          <el-select v-model="orderForm.coupon_id" placeholder="请选择优惠券">
            <el-option
              v-for="coupon in availableCoupons"
              :key="coupon.id"
              :label="formatCoupon(coupon)"
              :value="coupon.id"
            />
          </el-select>
        </el-form-item>

        <!-- 支付方式 -->
        <div class="section-title">支付方式</div>
        <el-form-item label="支付方式">
          <el-radio-group v-model="orderForm.payment_method">
            <el-radio label="alipay">支付宝</el-radio>
            <el-radio label="wechat">微信支付</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 订单备注 -->
        <el-form-item label="订单备注">
          <el-input
            v-model="orderForm.remark"
            type="textarea"
            :rows="3"
            placeholder="请输入订单备注（选填）"
          />
        </el-form-item>

        <!-- 订单金额 -->
        <div class="order-summary">
          <div class="summary-item">
            <span>商品总额：</span>
            <span>¥{{ orderForm.total_amount.toFixed(2) }}</span>
          </div>
          <div class="summary-item">
            <span>运费：</span>
            <span>¥{{ orderForm.shipping_fee.toFixed(2) }}</span>
          </div>
          <div class="summary-item">
            <span>优惠金额：</span>
            <span>-¥{{ orderForm.discount_amount.toFixed(2) }}</span>
          </div>
          <div class="summary-item total">
            <span>实付金额：</span>
            <span class="price">¥{{ orderForm.final_amount.toFixed(2) }}</span>
          </div>
        </div>

        <!-- 提交按钮 -->
        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">
            提交订单
          </el-button>
          <el-button @click="router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 添加地址对话框 -->
    <el-dialog
      v-model="showAddressDialog"
      title="添加新地址"
      width="500px"
    >
      <el-form :model="newAddress" label-width="100px">
        <el-form-item label="收货人">
          <el-input v-model="newAddress.receiver" />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="newAddress.phone" />
        </el-form-item>
        <el-form-item label="所在地区">
          <el-cascader
            v-model="newAddress.region"
            :options="regionOptions"
          />
        </el-form-item>
        <el-form-item label="详细地址">
          <el-input
            v-model="newAddress.address"
            type="textarea"
            :rows="2"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAddressDialog = false">取消</el-button>
          <el-button type="primary" @click="handleAddAddress">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { createOrder } from '@/api/order'
import { getAddressList, createAddress } from '@/api/address'
import { getAvailableCoupons } from '@/api/coupon'
import { getCartList } from '@/api/cart'

const router = useRouter()
const route = useRoute()
const submitting = ref(false)
const showAddressDialog = ref(false)

// 表单数据
const orderForm = ref({
  address_id: '',
  items: [],
  coupon_id: '',
  payment_method: 'alipay',
  remark: '',
  total_amount: 0,
  shipping_fee: 0,
  discount_amount: 0,
  final_amount: 0
})

// 地址相关
const addresses = ref([])
const newAddress = ref({
  receiver: '',
  phone: '',
  region: [],
  address: ''
})

// 优惠券相关
const availableCoupons = ref([])

// Mock data for demonstration
const mockItems = [
  {
    id: 1,
    name: '商品1',
    image_url: 'https://example.com/image1.jpg',
    specification: '规格1',
    price: 299.00,
    quantity: 1
  },
  {
    id: 2,
    name: '商品2',
    image_url: 'https://example.com/image2.jpg',
    specification: '规格2',
    price: 199.00,
    quantity: 2
  }
]

const mockCoupons = [
  {
    id: 1,
    name: '满300减50',
    amount: 50,
    min_amount: 300
  }
]

// 格式化地址显示
const formatAddress = (address) => {
  return `${address.receiver} ${address.phone} ${address.province}${address.city}${address.district}${address.address}`
}

// 格式化优惠券显示
const formatCoupon = (coupon) => {
  return `${coupon.name}（满${coupon.min_amount}减${coupon.amount}）`
}

// 计算订单金额
const calculateAmount = () => {
  const total = orderForm.value.items.reduce((sum, item) => sum + item.price * item.quantity, 0)
  orderForm.value.total_amount = total
  orderForm.value.shipping_fee = 10 // 固定运费
  orderForm.value.discount_amount = 0 // 优惠金额，根据选择的优惠券计算
  orderForm.value.final_amount = total + orderForm.value.shipping_fee - orderForm.value.discount_amount
}

// 初始化数据
const initData = async () => {
  try {
    // 获取地址列表
    const addressResponse = await getAddressList()
    addresses.value = addressResponse.results

    // 获取可用优惠券
    const couponResponse = await getAvailableCoupons()
    availableCoupons.value = couponResponse.results.map(item => ({
      id: item.id,
      name: item.coupon.name,
      type: item.coupon.type,
      type_display: item.coupon.type_display,
      amount: parseFloat(item.coupon.amount),
      min_amount: parseFloat(item.coupon.min_amount),
      start_time: item.coupon.start_time,
      end_time: item.coupon.end_time,
      status: item.coupon.status,
      status_display: item.coupon.status_display
    }))

    // 从路由参数获取商品信息
    const items = route.query.items
    if (!items) {
      ElMessage.error('未选择商品')
      router.push('/cart')
      return
    }
    orderForm.value.items = JSON.parse(items)
    calculateAmount()
  } catch (error) {
    ElMessage.error('获取数据失败')
  }
}

// 提交订单
const handleSubmit = async () => {
  if (!orderForm.value.address_id) {
    ElMessage.warning('请选择收货地址')
    return
  }

  submitting.value = true
  try {
    await createOrder(orderForm.value)
    ElMessage.success('订单创建成功')
    router.push('/order/list')
  } catch (error) {
    ElMessage.error('订单创建失败')
  } finally {
    submitting.value = false
  }
}

// 添加新地址
const handleAddAddress = async () => {
  try {
    await createAddress(newAddress.value)
    ElMessage.success('地址添加成功')
    showAddressDialog.value = false
    // 刷新地址列表
    const response = await getAddressList()
    addresses.value = response.results
  } catch (error) {
    ElMessage.error('地址添加失败')
  }
}

initData()
</script>

<style scoped>
.order-create {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title {
  font-size: 16px;
  font-weight: bold;
  margin: 20px 0 10px;
  padding-left: 10px;
  border-left: 4px solid #409eff;
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
</style> 