<template>
  <div class="product-list-container">
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="价格区间">
          <el-input-number
            v-model="filterForm.minPrice"
            :min="0"
            placeholder="最低价"
            @change="handleFilter"
            size="small"
          />
          <span class="mx-2">-</span>
          <el-input-number
            v-model="filterForm.maxPrice"
            :min="0"
            placeholder="最高价"
            @change="handleFilter"
            size="small"
          />
        </el-form-item>

        <el-form-item label="排序">
          <el-select
            v-model="filterForm.sortBy"
            placeholder="选择排序方式"
            @change="handleFilter"
            size="small"
          >
            <el-option label="默认排序" value="-created_at" />
            <el-option label="价格从低到高" value="price" />
            <el-option label="价格从高到低" value="-price" />
            <el-option label="销量从高到低" value="-sales" />
          </el-select>
        </el-form-item>

        <el-form-item label="商品分类">
          <el-select v-model="filterForm.category" placeholder="选择分类" clearable>
            <el-option
              v-for="category in categories"
              :key="category.id"
              :label="category.name"
              :value="category.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleFilter" size="small">筛选</el-button>
          <el-button @click="resetFilter" size="small">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <div class="product-grid">
      <el-row :gutter="20">
        <el-col 
          v-for="product in products" 
          :key="product.id" 
          :xs="24" 
          :sm="12" 
          :md="8" 
          :lg="6"
        >
          <el-card 
            class="product-card" 
            :body-style="{ padding: '0px' }"
            @click="goToDetail(product.id)"
          >
            <el-image 
              :src="product.images[0]?.image_url" 
              :preview-src-list="product.images.map(img => img.image_url)"
              fit="cover"
              class="product-image"
            >
              <template #error>
                <div class="image-slot">
                  <el-icon><picture-filled /></el-icon>
                </div>
              </template>
            </el-image>
            <div class="product-info">
              <h3 class="product-title">{{ product.name }}</h3>
              <div class="product-price">
                <span class="price">¥{{ product.price }}</span>
                <span class="sales">销量: {{ product.sales }}</span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[12, 24, 36, 48]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { PictureFilled } from '@element-plus/icons-vue'
import request from '@/utils/request'
import { debounce } from 'lodash-es'

const router = useRouter()
const route = useRoute()

// 筛选表单
const filterForm = reactive({
  minPrice: null,
  maxPrice: null,
  sortBy: '-created_at',
  search: '',
  category: null
})

// 分页相关
const currentPage = ref(1)
const pageSize = ref(12)
const total = ref(0)

// 数据
const products = ref([])
const categories = ref([])

// 获取商品列表
const fetchProducts = async () => {
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      min_price: filterForm.minPrice,
      max_price: filterForm.maxPrice,
      order_by: filterForm.sortBy,
      search: filterForm.search,
      category_id: filterForm.category,
      is_active: true
    }
    
    // 移除空值参数
    Object.keys(params).forEach(key => {
      if (params[key] === null || params[key] === '') {
        delete params[key]
      }
    })
    
    const response = await request.get('/products/products/', { params })
    products.value = response.results
    total.value = response.count
  } catch (error) {
    console.error('获取商品列表失败:', error)
    ElMessage.error('获取商品列表失败')
  }
}

// 获取分类列表
const fetchCategories = async () => {
  try {
    const response = await request.get('/products/categories/')
    // 从分页响应中获取分类列表
    categories.value = (response.results || []).filter(category => category.is_active)
  } catch (error) {
    console.error('获取分类列表失败:', error)
    // 只在真正失败时显示错误消息
    if (error.response?.status !== 200) {
      ElMessage.error('获取分类列表失败')
    }
  }
}

// 处理筛选
const handleFilter = debounce(() => {
  currentPage.value = 1 // 重置页码
  fetchProducts()
}, 300)

// 重置筛选
const resetFilter = () => {
  filterForm.minPrice = null
  filterForm.maxPrice = null
  filterForm.sortBy = '-created_at'
  filterForm.search = ''
  filterForm.category = null
  handleFilter()
}

// 处理分页
const handleSizeChange = (val) => {
  pageSize.value = val
  fetchProducts()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchProducts()
}

// 跳转到商品详情
const goToDetail = (productId) => {
  router.push(`/products/${productId}`)
}

// 监听路由参数变化
watch(() => route.query.q, (newQuery) => {
  if (newQuery) {
    filterForm.search = newQuery
    handleFilter()
  }
})

// 监听筛选条件变化
watch(
  () => ({
    minPrice: filterForm.minPrice,
    maxPrice: filterForm.maxPrice,
    sortBy: filterForm.sortBy
  }),
  () => {
    handleFilter()
  },
  { deep: true }
)

onMounted(() => {
  fetchCategories()
  fetchProducts()
})
</script>

<style scoped>
.product-list-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.filter-card {
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

.product-grid {
  margin-bottom: 20px;
}

.product-card {
  margin-bottom: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.15);
}

.product-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.product-card:hover .product-image {
  transform: scale(1.05);
}

.image-slot {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  background: #f5f7fa;
  color: #909399;
  font-size: 30px;
}

.product-info {
  padding: 14px;
  background: #fff;
}

.product-title {
  margin: 0;
  font-size: 16px;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  transition: color 0.3s ease;
}

.product-card:hover .product-title {
  color: #409EFF;
}

.product-price {
  margin-top: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.price {
  color: #f56c6c;
  font-size: 18px;
  font-weight: bold;
}

.sales {
  color: #909399;
  font-size: 14px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  padding: 20px 0;
}

.mx-2 {
  margin: 0 8px;
}

:deep(.el-form-item) {
  margin-bottom: 0;
}

:deep(.el-input-number) {
  width: 120px;
}

:deep(.el-select) {
  width: 160px;
}
</style> 