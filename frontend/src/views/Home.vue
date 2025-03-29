<template>
  <div class="home">
    <el-row :gutter="20">
      <el-col :span="6" v-for="product in products" :key="product.id">
        <el-card class="product-card" :body-style="{ padding: '0px' }">
          <img :src="product.image" class="product-image">
          <div class="product-info">
            <h3>{{ product.name }}</h3>
            <p class="price">¥{{ product.price }}</p>
            <el-button type="primary" @click="addToCart(product)">加入购物车</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const products = ref([
  {
    id: 1,
    name: '商品1',
    price: 99.99,
    image: 'https://via.placeholder.com/200x200'
  },
  {
    id: 2,
    name: '商品2',
    price: 199.99,
    image: 'https://via.placeholder.com/200x200'
  },
  {
    id: 3,
    name: '商品3',
    price: 299.99,
    image: 'https://via.placeholder.com/200x200'
  },
  {
    id: 4,
    name: '商品4',
    price: 399.99,
    image: 'https://via.placeholder.com/200x200'
  }
])

const addToCart = (product) => {
  ElMessage.success(`已将 ${product.name} 加入购物车`)
}
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.product-card {
  margin-bottom: 20px;
  transition: all 0.3s;
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
}

.product-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.product-info {
  padding: 14px;
}

.product-info h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.price {
  color: #f56c6c;
  font-size: 20px;
  margin: 10px 0;
}

.el-button {
  width: 100%;
}
</style> 