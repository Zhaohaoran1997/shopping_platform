<template>
  <div class="product-list-container">
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="分类">
          <el-select v-model="filterForm.category" placeholder="选择分类" clearable>
            <el-option
              v-for="item in categories"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="价格区间">
          <el-input-number v-model="filterForm.minPrice" :min="0" placeholder="最低价" />
          <span class="mx-2">-</span>
          <el-input-number v-model="filterForm.maxPrice" :min="0" placeholder="最高价" />
        </el-form-item>
        <el-form-item label="排序">
          <el-select v-model="filterForm.sortBy" placeholder="排序方式">
            <el-option label="价格从低到高" value="price_asc" />
            <el-option label="价格从高到低" value="price_desc" />
            <el-option label="销量从高到低" value="sales_desc" />
            <el-option label="上架时间最新" value="created_desc" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleFilter">筛选</el-button>
          <el-button @click="resetFilter">重置</el-button>
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
              :src="product.main_image" 
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
import axios from '@/utils/axios'

const router = useRouter()
const route = useRoute()

// 筛选表单
const filterForm = reactive({
  category: '',
  minPrice: null,
  maxPrice: null,
  sortBy: 'created_desc',
  search: ''
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
      category: filterForm.category,
      min_price: filterForm.minPrice,
      max_price: filterForm.maxPrice,
      sort_by: filterForm.sortBy,
      search: filterForm.search
    }
    
    const response = await axios.get('/products/products/', { params })
    products.value = response.data.results
    total.value = response.data.count
  } catch (error) {
    ElMessage.error('获取商品列表失败')
  }
}

// 获取分类列表
const fetchCategories = async () => {
  try {
    const response = await axios.get('/products/categories/')
    categories.value = response.data
  } catch (error) {
    ElMessage.error('获取分类列表失败')
  }
}

// 处理筛选
const handleFilter = () => {
  currentPage.value = 1
  fetchProducts()
}

// 重置筛选
const resetFilter = () => {
  filterForm.category = ''
  filterForm.minPrice = null
  filterForm.maxPrice = null
  filterForm.sortBy = 'created_desc'
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
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.product-grid {
  margin-bottom: 20px;
}

.product-card {
  margin-bottom: 20px;
  cursor: pointer;
  transition: transform 0.3s;
}

.product-card:hover {
  transform: translateY(-5px);
}

.product-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
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
}

.product-title {
  margin: 0;
  font-size: 16px;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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
}

.mx-2 {
  margin: 0 8px;
}
</style> 