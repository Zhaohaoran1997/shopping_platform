<template>
  <div class="cart-container">
    <h2>我的购物车</h2>
    
    <div v-if="loading" class="loading">
      <el-skeleton :rows="3" animated />
    </div>
    
    <div v-else-if="cartItems.length === 0" class="empty-cart">
      <el-empty description="购物车是空的">
        <el-button type="primary" @click="$router.push('/products')">
          去购物
        </el-button>
      </el-empty>
    </div>
    
    <div v-else class="cart-content">
      <el-table 
        :data="cartItems" 
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        
        <el-table-column label="商品信息" min-width="400">
          <template #default="{ row }">
            <div class="product-info">
              <el-image
                :src="row.product.images[0]?.image_url"
                :preview-src-list="row.product.images.map(img => img.image_url)"
                fit="cover"
                class="product-image"
              />
              <div class="product-detail">
                <h3 @click="$router.push(`/products/${row.product.id}`)">
                  {{ row.product.name }}
                </h3>
                <div class="specifications">
                  <span v-for="spec in row.product.specifications" :key="spec.id" class="spec-item">
                    {{ spec.name }}: {{ spec.value }}
                  </span>
                </div>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="单价" width="120">
          <template #default="{ row }">
            ¥{{ row.product.price }}
          </template>
        </el-table-column>
        
        <el-table-column label="数量" width="200">
          <template #default="{ row }">
            <el-input-number
              v-model="row.quantity"
              :min="1"
              :max="row.product.stock"
              @change="handleQuantityChange(row)"
            />
          </template>
        </el-table-column>
        
        <el-table-column label="小计" width="120">
          <template #default="{ row }">
            ¥{{ (row.product.price * row.quantity).toFixed(2) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button
              type="danger"
              link
              @click="handleRemove(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="cart-footer">
        <div class="cart-summary">
          <span>已选择 {{ selectedItems.length }} 件商品</span>
          <span class="total-price">
            合计：<span class="price">¥{{ totalPrice.toFixed(2) }}</span>
          </span>
        </div>
        <el-button
          type="primary"
          size="large"
          :disabled="selectedItems.length === 0"
          @click="handleCheckout"
        >
          结算
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from '@/utils/axios'

const router = useRouter()
const loading = ref(true)
const cartItems = ref([])
const selectedItems = ref([])

// 计算总价
const totalPrice = computed(() => {
  return selectedItems.value.reduce((total, item) => {
    return total + item.product.price * item.quantity
  }, 0)
})

// 获取购物车列表
const fetchCartItems = async () => {
  try {
    const response = await axios.get('/cart/cart/')
    // 后端返回的是分页列表，需要获取第一个购物车的items
    if (response.data.results && response.data.results.length > 0) {
      cartItems.value = response.data.results[0].items
      // 更新选中状态
      selectedItems.value = cartItems.value.filter(item => item.selected)
    } else {
      cartItems.value = []
      selectedItems.value = []
    }
  } catch (error) {
    ElMessage.error('获取购物车列表失败')
    cartItems.value = []
    selectedItems.value = []
  } finally {
    loading.value = false
  }
}

// 更新商品数量
const handleQuantityChange = async (item) => {
  try {
    const cartResponse = await axios.get('/cart/cart/')
    const cartId = cartResponse.data.results[0].id

    await axios.put(`/cart/cart/${cartId}/update_item/`, {
      item_id: item.id,
      quantity: item.quantity
    })
    ElMessage.success('更新成功')
  } catch (error) {
    ElMessage.error('更新失败')
    // 恢复原数量
    await fetchCartItems()
  }
}

// 删除商品
const handleRemove = async (item) => {
  try {
    await ElMessageBox.confirm('确定要删除这个商品吗？', '提示', {
      type: 'warning'
    })
    
    const cartResponse = await axios.get('/cart/cart/')
    const cartId = cartResponse.data.results[0].id

    await axios.delete(`/cart/cart/${cartId}/remove_item/`, {
      data: { item_id: item.id }
    })
    ElMessage.success('删除成功')
    await fetchCartItems()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 结算
const handleCheckout = () => {
  if (selectedItems.value.length === 0) {
    ElMessage.warning('请选择要结算的商品')
    return
  }
  
  // 将选中的商品数据转换为订单所需格式
  const orderItems = selectedItems.value.map(item => ({
    id: item.product.id,
    name: item.product.name,
    image_url: item.product.image_url,
    specification: item.product.specification,
    price: parseFloat(item.product.price),
    quantity: item.quantity
  }))
  
  // 跳转到订单创建页面，并传递商品数据
  router.push({
    path: '/order/create',
    query: {
      items: JSON.stringify(orderItems)
    }
  })
}

// 表格选择变化
const handleSelectionChange = async (selection) => {
  selectedItems.value = selection
  try {
    const cartResponse = await axios.get('/cart/cart/')
    const cartId = cartResponse.data.results[0].id

    // 更新所有商品的选择状态
    await Promise.all(cartItems.value.map(item => 
      axios.put(`/cart/cart/${cartId}/select_item/`, {
        item_id: item.id,
        selected: selection.some(selected => selected.id === item.id)
      })
    ))
  } catch (error) {
    ElMessage.error('更新选择状态失败')
  }
}

onMounted(() => {
  fetchCartItems()
})
</script>

<style scoped>
.cart-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.loading {
  margin: 20px 0;
}

.empty-cart {
  margin: 40px 0;
}

.product-info {
  display: flex;
  align-items: center;
  gap: 20px;
}

.product-image {
  width: 80px;
  height: 80px;
  border-radius: 4px;
}

.product-detail h3 {
  margin: 0 0 8px;
  cursor: pointer;
  color: #409EFF;
}

.product-detail h3:hover {
  text-decoration: underline;
}

.specifications {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.spec-item {
  color: #666;
  font-size: 14px;
}

.cart-footer {
  margin-top: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 4px;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 20px;
}

.cart-summary {
  display: flex;
  align-items: center;
  gap: 20px;
}

.total-price {
  font-size: 16px;
}

.price {
  color: #f56c6c;
  font-size: 20px;
  font-weight: bold;
}
</style> 