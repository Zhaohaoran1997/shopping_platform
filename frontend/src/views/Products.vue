<template>
  <div class="products-container">
    <el-row :gutter="20">
      <!-- 筛选区域 -->
      <el-col :span="6">
        <el-card class="filter-card">
          <template #header>
            <div class="card-header">
              <span>商品筛选</span>
            </div>
          </template>
          
          <el-form :model="filterForm" label-width="80px">
            <el-form-item label="价格区间">
              <el-input-number v-model="filterForm.minPrice" :min="0" placeholder="最低价" />
              <span class="mx-2">-</span>
              <el-input-number v-model="filterForm.maxPrice" :min="0" placeholder="最高价" />
            </el-form-item>
            
            <el-form-item label="分类">
              <el-select v-model="filterForm.category" placeholder="选择分类" clearable>
                <el-option
                  v-for="item in categories"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item label="排序">
              <el-select v-model="filterForm.sort" placeholder="选择排序方式">
                <el-option label="默认排序" value="" />
                <el-option label="价格从低到高" value="price_asc" />
                <el-option label="价格从高到低" value="price_desc" />
                <el-option label="销量优先" value="sales_desc" />
              </el-select>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="handleFilter">筛选</el-button>
              <el-button @click="resetFilter">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      
      <!-- 商品列表 -->
      <el-col :span="18">
        <el-row :gutter="20">
          <el-col
            v-for="product in productsList"
            :key="product.id"
            :xs="24"
            :sm="12"
            :md="8"
            :lg="6"
          >
            <el-card class="product-card" :body-style="{ padding: '0px' }">
              <img :src="product.image" class="product-image" @click="goToDetail(product.id)">
              <div class="product-info">
                <h3 class="product-title" @click="goToDetail(product.id)">{{ product.name }}</h3>
                <div class="product-price">
                  <span class="price">¥{{ product.price }}</span>
                  <span class="original-price" v-if="product.originalPrice">¥{{ product.originalPrice }}</span>
                </div>
                <div class="product-footer">
                  <span class="sales">销量: {{ product.sales }}</span>
                  <el-button type="primary" size="small" @click="addToCart(product)">加入购物车</el-button>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
        
        <!-- 分页 -->
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
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { products, categories } from '@/mock/products'

const router = useRouter()
const productsList = ref(products)
const total = ref(products.length)
const currentPage = ref(1)
const pageSize = ref(12)

const filterForm = reactive({
  minPrice: null,
  maxPrice: null,
  category: '',
  sort: ''
})

// 获取商品列表
const fetchProducts = () => {
  let filteredProducts = [...products]
  
  // 价格筛选
  if (filterForm.minPrice !== null) {
    filteredProducts = filteredProducts.filter(p => p.price >= filterForm.minPrice)
  }
  if (filterForm.maxPrice !== null) {
    filteredProducts = filteredProducts.filter(p => p.price <= filterForm.maxPrice)
  }
  
  // 分类筛选
  if (filterForm.category) {
    filteredProducts = filteredProducts.filter(p => p.category === filterForm.category)
  }
  
  // 排序
  if (filterForm.sort) {
    switch (filterForm.sort) {
      case 'price_asc':
        filteredProducts.sort((a, b) => a.price - b.price)
        break
      case 'price_desc':
        filteredProducts.sort((a, b) => b.price - a.price)
        break
      case 'sales_desc':
        filteredProducts.sort((a, b) => b.sales - a.sales)
        break
    }
  }
  
  // 分页
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  productsList.value = filteredProducts.slice(start, end)
  total.value = filteredProducts.length
}

// 筛选
const handleFilter = () => {
  currentPage.value = 1
  fetchProducts()
}

// 重置筛选
const resetFilter = () => {
  Object.keys(filterForm).forEach(key => {
    filterForm[key] = ''
  })
  handleFilter()
}

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val
  fetchProducts()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchProducts()
}

// 跳转到商品详情
const goToDetail = (id) => {
  router.push(`/products/${id}`)
}

// 加入购物车
const addToCart = async (product) => {
  ElMessage.success('已添加到购物车')
}

onMounted(() => {
  fetchProducts()
})
</script>

<style scoped>
.products-container {
  padding: 20px;
}

.filter-card {
  margin-bottom: 20px;
}

.product-card {
  margin-bottom: 20px;
  transition: all 0.3s;
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 2px 12px 0 rgba(0,0,0,.1);
}

.product-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
  cursor: pointer;
}

.product-info {
  padding: 14px;
}

.product-title {
  margin: 0;
  font-size: 16px;
  cursor: pointer;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-title:hover {
  color: #409EFF;
}

.product-price {
  margin: 10px 0;
}

.price {
  color: #f56c6c;
  font-size: 20px;
  font-weight: bold;
}

.original-price {
  color: #999;
  text-decoration: line-through;
  margin-left: 10px;
  font-size: 14px;
}

.product-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
}

.sales {
  color: #999;
  font-size: 14px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.mx-2 {
  margin: 0 8px;
}
</style> 