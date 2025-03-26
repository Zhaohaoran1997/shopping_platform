<template>
  <div class="cart-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>我的购物车</span>
          <el-button type="danger" @click="clearCart" :disabled="!cartItems.length">清空购物车</el-button>
        </div>
      </template>
      
      <div v-if="cartItems.length" class="cart-content">
        <el-table :data="cartItems" style="width: 100%">
          <el-table-column type="selection" width="55" />
          <el-table-column label="商品信息">
            <template #default="{ row }">
              <div class="product-info">
                <img :src="row.image" class="product-image">
                <div class="product-detail">
                  <h3>{{ row.name }}</h3>
                  <p class="product-category">{{ row.category }}</p>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="单价" width="120">
            <template #default="{ row }">
              <span class="price">¥{{ row.price }}</span>
            </template>
          </el-table-column>
          <el-table-column label="数量" width="200">
            <template #default="{ row }">
              <el-input-number
                v-model="row.quantity"
                :min="1"
                :max="row.stock"
                @change="updateQuantity(row)"
              />
            </template>
          </el-table-column>
          <el-table-column label="小计" width="120">
            <template #default="{ row }">
              <span class="subtotal">¥{{ (row.price * row.quantity).toFixed(2) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button type="danger" link @click="removeItem(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <div class="cart-footer">
          <div class="cart-summary">
            <span>已选择 {{ selectedCount }} 件商品</span>
            <span>合计：<span class="total-price">¥{{ totalPrice.toFixed(2) }}</span></span>
          </div>
          <el-button type="primary" size="large" @click="checkout" :disabled="!selectedCount">
            结算
          </el-button>
        </div>
      </div>
      
      <div v-else class="empty-cart">
        <el-empty description="购物车是空的">
          <el-button type="primary" @click="$router.push('/products')">去购物</el-button>
        </el-empty>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { products } from '@/mock/products'

const router = useRouter()

// 模拟购物车数据
const cartItems = ref([
  {
    ...products[0],
    quantity: 1
  },
  {
    ...products[1],
    quantity: 1
  }
])

// 计算选中商品数量
const selectedCount = computed(() => {
  return cartItems.value.length
})

// 计算总价
const totalPrice = computed(() => {
  return cartItems.value.reduce((total, item) => {
    return total + item.price * item.quantity
  }, 0)
})

// 更新商品数量
const updateQuantity = (item) => {
  ElMessage.success('数量已更新')
}

// 删除商品
const removeItem = (item) => {
  ElMessageBox.confirm('确定要删除这个商品吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    const index = cartItems.value.findIndex(i => i.id === item.id)
    if (index > -1) {
      cartItems.value.splice(index, 1)
      ElMessage.success('商品已删除')
    }
  })
}

// 清空购物车
const clearCart = () => {
  ElMessageBox.confirm('确定要清空购物车吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    cartItems.value = []
    ElMessage.success('购物车已清空')
  })
}

// 结算
const checkout = () => {
  router.push('/checkout')
}
</script>

<style scoped>
.cart-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.product-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.product-image {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 4px;
}

.product-detail h3 {
  margin: 0;
  font-size: 16px;
}

.product-category {
  margin: 5px 0 0;
  color: #999;
  font-size: 14px;
}

.price {
  color: #f56c6c;
  font-weight: bold;
}

.subtotal {
  color: #f56c6c;
  font-weight: bold;
}

.cart-footer {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 20px;
}

.cart-summary {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 10px;
}

.total-price {
  color: #f56c6c;
  font-size: 20px;
  font-weight: bold;
}

.empty-cart {
  padding: 40px 0;
}
</style> 