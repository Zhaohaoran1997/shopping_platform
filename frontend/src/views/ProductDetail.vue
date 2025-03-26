<template>
  <div class="product-detail-container">
    <el-card v-loading="loading">
      <template v-if="product">
        <el-row :gutter="40">
          <!-- 商品图片 -->
          <el-col :span="12">
            <el-carousel height="400px" class="product-carousel">
              <el-carousel-item v-for="(image, index) in product.images" :key="index">
                <img :src="image" class="product-image">
              </el-carousel-item>
            </el-carousel>
          </el-col>
          
          <!-- 商品信息 -->
          <el-col :span="12">
            <div class="product-info">
              <h1 class="product-name">{{ product.name }}</h1>
              
              <div class="product-price">
                <span class="price">¥{{ product.price }}</span>
                <span class="original-price" v-if="product.originalPrice">¥{{ product.originalPrice }}</span>
              </div>
              
              <div class="product-meta">
                <span class="sales">销量: {{ product.sales }}</span>
                <span class="stock">库存: {{ product.stock }}</span>
                <span class="category">分类: {{ product.category }}</span>
              </div>
              
              <div class="product-description">
                <h3>商品描述</h3>
                <p>{{ product.description }}</p>
              </div>
              
              <div class="product-actions">
                <el-input-number
                  v-model="quantity"
                  :min="1"
                  :max="product.stock"
                  size="large"
                />
                <el-button
                  type="primary"
                  size="large"
                  :disabled="product.stock === 0"
                  @click="addToCart"
                >
                  加入购物车
                </el-button>
                <el-button
                  type="danger"
                  size="large"
                  :disabled="product.stock === 0"
                  @click="buyNow"
                >
                  立即购买
                </el-button>
              </div>
            </div>
          </el-col>
        </el-row>
        
        <!-- 商品详情 -->
        <div class="product-detail-section">
          <el-tabs v-model="activeTab">
            <el-tab-pane label="商品详情" name="detail">
              <div class="detail-content" v-html="product.detail"></div>
            </el-tab-pane>
            <el-tab-pane label="商品评价" name="reviews">
              <div class="reviews-list">
                <div v-for="review in product.reviews" :key="review.id" class="review-item">
                  <div class="review-header">
                    <el-avatar :src="review.user.avatar" />
                    <span class="review-user">{{ review.user.username }}</span>
                    <el-rate v-model="review.rating" disabled />
                    <span class="review-time">{{ review.created_at }}</span>
                  </div>
                  <div class="review-content">{{ review.content }}</div>
                  <div class="review-images" v-if="review.images && review.images.length">
                    <el-image
                      v-for="(image, index) in review.images"
                      :key="index"
                      :src="image"
                      :preview-src-list="review.images"
                    />
                  </div>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </template>
    </el-card>
  </div>
</template>
  
<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
  
const route = useRoute()
const router = useRouter()
const loading = ref(true)
const product = ref(null)
const quantity = ref(1)
const activeTab = ref('detail')
  
// 获取商品详情
const fetchProductDetail = async () => {
  try {
    const response = await request.get(`/products/${route.params.id}/`)
    product.value = response
  } catch (error) {
    ElMessage.error('获取商品详情失败')
  } finally {
    loading.value = false
  }
}
  
// 加入购物车
const addToCart = async () => {
  try {
    await request.post('/cart/items/', {
      product_id: product.value.id,
      quantity: quantity.value
    })
    ElMessage.success('已添加到购物车')
  } catch (error) {
    ElMessage.error('添加购物车失败')
  }
}
  
// 立即购买
const buyNow = () => {
  router.push({
    path: '/checkout',
    query: {
      product_id: product.value.id,
      quantity: quantity.value
    }
  })
}
  
onMounted(() => {
  fetchProductDetail()
})
</script>
  
<style scoped>
.product-detail-container {
  padding: 20px;
}
  
.product-carousel {
  border: 1px solid #eee;
  border-radius: 4px;
}
  
.product-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
  
.product-info {
  padding: 20px;
}
  
.product-name {
  font-size: 24px;
  margin: 0 0 20px;
  color: #303133;
}
  
.product-price {
  margin-bottom: 20px;
}
  
.price {
  font-size: 28px;
  color: #f56c6c;
  font-weight: bold;
}
  
.original-price {
  color: #999;
  text-decoration: line-through;
  margin-left: 10px;
  font-size: 16px;
}
  
.product-meta {
  margin-bottom: 20px;
  color: #666;
}
  
.product-meta span {
  margin-right: 20px;
}
  
.product-description {
  margin-bottom: 30px;
}
  
.product-description h3 {
  margin: 0 0 10px;
  font-size: 18px;
}
  
.product-description p {
  color: #666;
  line-height: 1.6;
}
  
.product-actions {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
}
  
.product-detail-section {
  margin-top: 40px;
}
  
.reviews-list {
  padding: 20px 0;
}
  
.review-item {
  padding: 20px 0;
  border-bottom: 1px solid #eee;
}
  
.review-header {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}
  
.review-user {
  margin: 0 10px;
  font-weight: bold;
}
  
.review-time {
  margin-left: auto;
  color: #999;
  font-size: 14px;
}
  
.review-content {
  margin: 10px 0;
  line-height: 1.6;
}
  
.review-images {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}
  
.review-images .el-image {
  width: 100px;
  height: 100px;
  border-radius: 4px;
  cursor: pointer;
}
</style> 