<template>
  <div class="coupon-container">
    <el-tabs v-model="activeTab" class="coupon-tabs">
      <el-tab-pane label="我的优惠券" name="my">
        <el-card class="coupon-card">
          <template #header>
            <div class="card-header">
              <h2>我的优惠券</h2>
            </div>
          </template>
          
          <el-tabs v-model="myCouponTab" class="my-coupon-tabs">
            <el-tab-pane label="未使用" name="unused">
              <el-table :data="unusedCoupons" style="width: 100%">
                <el-table-column prop="coupon.name" label="优惠券名称" width="150" />
                <el-table-column prop="coupon.type_display" label="优惠券类型" width="100" />
                <el-table-column label="优惠金额" width="120">
                  <template #default="{ row }">
                    <template v-if="row.coupon.type === 1">
                      ¥{{ row.coupon.amount }}
                    </template>
                    <template v-else>
                      {{ (Number(row.coupon.amount) * 10).toFixed(0) }}折
                    </template>
                  </template>
                </el-table-column>
                <el-table-column prop="coupon.min_amount" label="使用条件" width="120">
                  <template #default="{ row }">
                    满{{ row.coupon.min_amount }}元可用
                  </template>
                </el-table-column>
                <el-table-column label="有效期" width="200">
                  <template #default="{ row }">
                    {{ formatDate(row.coupon.start_time) }} - {{ formatDate(row.coupon.end_time) }}
                  </template>
                </el-table-column>
                <el-table-column prop="created_at" label="领取时间" width="180">
                  <template #default="{ row }">
                    {{ formatDateTime(row.created_at) }}
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="120" fixed="right">
                  <template #default="{ row }">
                    <el-button 
                      type="primary" 
                      size="small"
                      @click="useCoupon(row)"
                    >
                      使用
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-tab-pane>
            
            <el-tab-pane label="已使用" name="used">
              <el-table :data="usedCoupons" style="width: 100%">
                <el-table-column prop="coupon.name" label="优惠券名称" width="150" />
                <el-table-column prop="coupon.type_display" label="优惠券类型" width="100" />
                <el-table-column label="优惠金额" width="120">
                  <template #default="{ row }">
                    <template v-if="row.coupon.type === 1">
                      ¥{{ row.coupon.amount }}
                    </template>
                    <template v-else>
                      {{ (Number(row.coupon.amount) * 10).toFixed(0) }}折
                    </template>
                  </template>
                </el-table-column>
                <el-table-column prop="coupon.min_amount" label="使用条件" width="120">
                  <template #default="{ row }">
                    满{{ row.coupon.min_amount }}元可用
                  </template>
                </el-table-column>
                <el-table-column label="有效期" width="200">
                  <template #default="{ row }">
                    {{ formatDate(row.coupon.start_time) }} - {{ formatDate(row.coupon.end_time) }}
                  </template>
                </el-table-column>
                <el-table-column prop="created_at" label="领取时间" width="180">
                  <template #default="{ row }">
                    {{ formatDateTime(row.created_at) }}
                  </template>
                </el-table-column>
                <el-table-column prop="used_at" label="使用时间" width="180">
                  <template #default="{ row }">
                    {{ formatDateTime(row.used_at) }}
                  </template>
                </el-table-column>
              </el-table>
            </el-tab-pane>
            
            <el-tab-pane label="已失效" name="expired">
              <el-table :data="expiredCoupons" style="width: 100%">
                <el-table-column prop="coupon.name" label="优惠券名称" width="150" />
                <el-table-column prop="coupon.type_display" label="优惠券类型" width="100" />
                <el-table-column label="优惠金额" width="120">
                  <template #default="{ row }">
                    <template v-if="row.coupon.type === 1">
                      ¥{{ row.coupon.amount }}
                    </template>
                    <template v-else>
                      {{ (Number(row.coupon.amount) * 10).toFixed(0) }}折
                    </template>
                  </template>
                </el-table-column>
                <el-table-column prop="coupon.min_amount" label="使用条件" width="120">
                  <template #default="{ row }">
                    满{{ row.coupon.min_amount }}元可用
                  </template>
                </el-table-column>
                <el-table-column label="有效期" width="200">
                  <template #default="{ row }">
                    {{ formatDate(row.coupon.start_time) }} - {{ formatDate(row.coupon.end_time) }}
                  </template>
                </el-table-column>
                <el-table-column prop="created_at" label="领取时间" width="180">
                  <template #default="{ row }">
                    {{ formatDateTime(row.created_at) }}
                  </template>
                </el-table-column>
              </el-table>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-tab-pane>
      
      <el-tab-pane label="优惠券中心" name="center">
        <el-card class="coupon-card">
          <template #header>
            <div class="card-header">
              <h2>优惠券中心</h2>
            </div>
          </template>
          
          <el-row :gutter="20">
            <el-col 
              v-for="coupon in availableCoupons" 
              :key="coupon.id" 
              :xs="24" 
              :sm="12" 
              :md="8" 
              :lg="6"
            >
              <el-card class="coupon-item" :body-style="{ padding: '0px' }">
                <div class="coupon-content">
                  <div class="coupon-amount">
                    <span class="currency">¥</span>
                    <span class="amount">{{ coupon.type === 1 ? coupon.amount : (Number(coupon.amount) * 10).toFixed(0) + '折' }}</span>
                  </div>
                  <div class="coupon-info">
                    <h3>{{ coupon.name }}</h3>
                    <p>满{{ coupon.min_amount }}元可用</p>
                    <p class="validity">
                      {{ formatDate(coupon.start_time) }} - {{ formatDate(coupon.end_time) }}
                    </p>
                  </div>
                  <div class="coupon-actions">
                    <el-button 
                      type="primary" 
                      @click="claimCoupon(coupon)"
                      :disabled="isCouponClaimed(coupon.id)"
                    >
                      {{ isCouponClaimed(coupon.id) ? '已领取' : '立即领取' }}
                    </el-button>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import { formatDate, formatDateTime } from '@/utils/format'

const authStore = useAuthStore()
const activeTab = ref('my')
const myCouponTab = ref('unused') // 默认显示未使用的优惠券
const myCoupons = ref([])
const availableCoupons = ref([])

// 根据状态筛选优惠券
const unusedCoupons = computed(() => {
  return myCoupons.value.filter(coupon => coupon.status === 0)
})

const usedCoupons = computed(() => {
  return myCoupons.value.filter(coupon => coupon.status === 1)
})

const expiredCoupons = computed(() => {
  return myCoupons.value.filter(coupon => coupon.status === 2)
})

// 获取我的优惠券
const fetchMyCoupons = async () => {
  try {
    const response = await request.get('/coupons/user-coupons/')
    if (response && Array.isArray(response.results)) {
      myCoupons.value = response.results
    } else {
      myCoupons.value = []
      ElMessage.warning('暂无优惠券数据')
    }
  } catch (error) {
    myCoupons.value = []
    ElMessage.error('获取我的优惠券失败')
    console.error('获取我的优惠券失败:', error)
  }
}

// 获取可领取的优惠券
const fetchAvailableCoupons = async () => {
  try {
    const response = await request.get('/coupons/coupons/')
    if (response && Array.isArray(response.results)) {
      availableCoupons.value = response.results
    } else {
      availableCoupons.value = []
      ElMessage.warning('暂无可领取的优惠券')
    }
  } catch (error) {
    availableCoupons.value = []
    ElMessage.error('获取优惠券中心数据失败')
    console.error('获取优惠券中心数据失败:', error)
  }
}

// 检查优惠券是否已领取
const isCouponClaimed = (couponId) => {
  return myCoupons.value.some(myCoupon => myCoupon.coupon.id === couponId)
}

// 领取优惠券
const claimCoupon = async (coupon) => {
  try {
    await request.post(`/coupons/coupons/${coupon.id}/claim/`)
    ElMessage.success('领取成功')
    // 重新获取两个列表
    await Promise.all([
      fetchMyCoupons(),
      fetchAvailableCoupons()
    ])
  } catch (error) {
    const errorMessage = error.response?.data?.detail || '领取失败'
    ElMessage.error(errorMessage)
    console.error('领取优惠券失败:', error)
  }
}

// 使用优惠券
const useCoupon = (userCoupon) => {
  // TODO: 实现使用优惠券的逻辑
  ElMessage.info('使用优惠券功能开发中')
}

// 获取状态类型
const getStatusType = (status) => {
  const types = {
    0: 'success',  // 未使用
    1: 'info',     // 已使用
    2: 'danger'    // 已过期
  }
  return types[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const texts = {
    1: '未使用',
    2: '已使用',
    3: '已过期'
  }
  return texts[status] || '未知'
}

onMounted(async () => {
  try {
    await Promise.all([
      fetchMyCoupons(),
      fetchAvailableCoupons()
    ])
  } catch (error) {
    console.error('初始化优惠券数据失败:', error)
  }
})
</script>

<style scoped>
.coupon-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.coupon-tabs {
  margin-bottom: 20px;
}

.coupon-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.coupon-item {
  margin-bottom: 20px;
  transition: all 0.3s;
}

.coupon-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 2px 12px 0 rgba(0,0,0,.1);
}

.coupon-content {
  padding: 20px;
  text-align: center;
}

.coupon-amount {
  margin-bottom: 15px;
}

.currency {
  font-size: 16px;
  color: #f56c6c;
}

.amount {
  font-size: 36px;
  font-weight: bold;
  color: #f56c6c;
}

.coupon-info {
  margin-bottom: 15px;
}

.coupon-info h3 {
  margin: 0 0 10px;
  font-size: 16px;
  color: #303133;
}

.coupon-info p {
  margin: 5px 0;
  color: #909399;
  font-size: 14px;
}

.validity {
  font-size: 12px;
  color: #909399;
}

.coupon-actions {
  margin-top: 15px;
}

:deep(.el-tabs__nav-wrap::after) {
  height: 1px;
}
</style> 