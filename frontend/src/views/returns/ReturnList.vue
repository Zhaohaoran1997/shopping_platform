<template>
  <div class="return-list">
    <div class="page-header">
      <h2>退换货管理</h2>
      <el-button type="primary" @click="router.push('/returns/create')">申请退换货</el-button>
    </div>

    <el-card v-loading="loading" class="list-card">
      <el-table :data="returnList" style="width: 100%">
        <el-table-column prop="id" label="申请编号" width="100" />
        <el-table-column prop="order_number" label="订单编号" width="120" />
        <el-table-column prop="product_name" label="商品名称" min-width="150" />
        <el-table-column prop="quantity" label="数量" width="80" />
        <el-table-column prop="total_price" label="总价" width="100">
          <template #default="{ row }">
            ¥{{ row.total_price }}
          </template>
        </el-table-column>
        <el-table-column prop="type_display" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.type === 1 ? 'danger' : 'warning'">
              {{ row.type_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="reason" label="原因" min-width="150" />
        <el-table-column prop="status_display" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ row.status_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="申请时间" width="180" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              link
              @click="router.push(`/returns/${row.id}`)"
            >
              查看详情
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
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const router = useRouter()
const loading = ref(false)
const returnList = ref([])
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

const fetchReturnList = async () => {
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
    console.log('API Response:', response)  // 添加调试日志
    returnList.value = response.data.results
    total.value = response.data.count
  } catch (error) {
    console.error('获取退换货列表失败:', error)
    ElMessage.error(error.message || '获取退换货列表失败')
    returnList.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

const handleSizeChange = (val) => {
  pageSize.value = val
  fetchReturnList()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchReturnList()
}

onMounted(() => {
  fetchReturnList()
})
</script>

<style scoped>
.return-list {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.list-card {
  max-width: 1200px;
  margin: 0 auto;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style> 