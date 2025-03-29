<template>
  <div class="order-list">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>我的订单</span>
        </div>
      </template>
      
      <el-table :data="orders" style="width: 100%">
        <el-table-column prop="order_no" label="订单编号" />
        <el-table-column prop="created_at" label="下单时间">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="total_amount" label="订单金额">
          <template #default="scope">
            ¥{{ scope.row.total_amount }}
          </template>
        </el-table-column>
        <el-table-column prop="status_display" label="订单状态">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ scope.row.status_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button 
              v-if="scope.row.status === 1"
              type="primary" 
              size="small"
              @click="handlePay(scope.row)"
            >
              立即支付
            </el-button>
            <el-button 
              v-if="scope.row.status === 1"
              type="danger" 
              size="small"
              @click="handleCancel(scope.row)"
            >
              取消订单
            </el-button>
            <el-button 
              type="info" 
              size="small"
              @click="handleViewDetail(scope.row)"
            >
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 30, 50]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { formatDate } from '@/utils/date'
import { getOrderList, cancelOrder } from '@/api/order'

const router = useRouter()
const orders = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const getStatusType = (status) => {
  const statusMap = {
    1: 'warning',   // 待支付
    2: 'primary',   // 待收货
    3: 'success',   // 已完成
    4: 'info'       // 已取消
  }
  return statusMap[status] || 'info'
}

const fetchOrders = async () => {
  try {
    const response = await getOrderList({
      page: currentPage.value,
      page_size: pageSize.value
    })
    orders.value = response.results
    total.value = response.count
  } catch (error) {
    console.error('获取订单列表失败:', error)
    ElMessage.error('获取订单列表失败')
  }
}

const handlePay = (order) => {
  router.push(`/order/payment/${order.id}`)
}

const handleCancel = async (order) => {
  try {
    await ElMessageBox.confirm('确定要取消该订单吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await cancelOrder(order.id)
    ElMessage.success('订单已取消')
    fetchOrders()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('取消订单失败')
    }
  }
}

const handleViewDetail = (order) => {
  router.push(`/order/detail/${order.id}`)
}

const handleSizeChange = (val) => {
  pageSize.value = val
  fetchOrders()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchOrders()
}

onMounted(() => {
  fetchOrders()
})
</script>

<style scoped>
.order-list {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.order-list .el-card {
  margin-bottom: 20px;
}

.order-list .el-card__header {
  padding: 15px 20px;
  border-bottom: 1px solid #ebeef5;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.order-list .el-card__body {
  padding: 20px;
}

.order-list .el-table {
  width: 100%;
  margin-top: 20px;
}

.order-list .el-table__inner-wrapper {
  width: 100%;
}

.order-list .el-table__body-wrapper {
  width: 100%;
}

.order-list .el-table__header-wrapper {
  width: 100%;
}

.order-list .el-table th {
  background-color: #f5f7fa;
  color: #606266;
  font-weight: 500;
  text-align: left;
  padding: 12px 0;
}

.order-list .el-table td {
  padding: 12px 0;
}

.order-list .el-tag {
  min-width: 80px;
  text-align: center;
}

.order-list .el-pagination {
  margin-top: 20px;
  text-align: right;
}
</style> 