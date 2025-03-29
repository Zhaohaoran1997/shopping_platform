<template>
  <div class="returns-list">
    <div class="page-header">
      <h2>我的退换货</h2>
      <el-button type="primary" @click="handleCreateReturn">
        <el-icon><Plus /></el-icon>
        申请退换货
      </el-button>
    </div>

    <el-table :data="returnsList" v-loading="loading" style="width: 100%">
      <el-table-column prop="order.order_no" label="订单号" width="180" />
      <el-table-column label="商品信息" min-width="300">
        <template #default="{ row }">
          <div v-for="item in row.order.items" :key="item.id" class="order-item">
            <el-image 
              :src="item.product_image" 
              :preview-src-list="[item.product_image]"
              class="product-image"
            />
            <span>{{ item.product_name }}</span>
            <span class="quantity">x{{ item.quantity }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="type_display" label="退换类型" width="120">
        <template #default="{ row }">
          <el-tag :type="row.type === 1 ? 'danger' : 'warning'">
            {{ row.type_display }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status_display" label="状态" width="120">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">
            {{ row.status_display }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="申请时间" width="180" />
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="handleViewDetail(row)">
            查看详情
          </el-button>
          <el-button 
            v-if="row.status === 1"
            link 
            type="danger" 
            @click="handleCancel(row)"
          >
            取消申请
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import request from '@/utils/request'

const router = useRouter()
const loading = ref(false)
const returnsList = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

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

const fetchReturnsList = async () => {
  loading.value = true
  try {
    const response = await request({
      url: '/returns/requests/',
      method: 'get',
      params: {
        page: currentPage.value,
        page_size: pageSize.value
      }
    })
    
    returnsList.value = response.results || []
    total.value = response.count || 0
  } catch (error) {
    console.error('获取退换货列表失败:', error)
    ElMessage.error(error.message || '获取退换货列表失败')
  } finally {
    loading.value = false
  }
}

const handleCreateReturn = () => {
  router.push('/returns/create')
}

const handleViewDetail = (row) => {
  router.push(`/returns/${row.id}`)
}

const handleCancel = async (row) => {
  try {
    await ElMessageBox.confirm('确定要取消该退换货申请吗？', '提示', {
      type: 'warning'
    })
    
    await request({
      url: `/returns/requests/${row.id}/cancel/`,
      method: 'post'
    })
    
    ElMessage.success('取消申请成功')
    fetchReturnsList()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消申请失败:', error)
      ElMessage.error(error.message || '取消申请失败')
    }
  }
}

const handleSizeChange = (val) => {
  pageSize.value = val
  fetchReturnsList()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchReturnsList()
}

onMounted(() => {
  fetchReturnsList()
})
</script>

<style scoped>
.returns-list {
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

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.order-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.order-item:last-child {
  margin-bottom: 0;
}

.product-image {
  width: 40px;
  height: 40px;
  margin-right: 8px;
  border-radius: 4px;
}

.quantity {
  margin-left: 8px;
  color: #999;
}
</style> 