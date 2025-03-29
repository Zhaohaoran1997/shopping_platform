<template>
  <div class="product-detail-container">
    <el-card v-loading="loading">
      <template v-if="product">
        <div class="product-content">
          <!-- 商品图片展示 -->
          <div class="product-gallery">
            <el-carousel height="400px" indicator-position="outside">
              <el-carousel-item v-for="image in product.images" :key="image.id">
                <el-image 
                  :src="image.image_url" 
                  fit="contain"
                  class="gallery-image"
                >
                  <template #error>
                    <div class="image-slot">
                      <el-icon><picture-filled /></el-icon>
                    </div>
                  </template>
                </el-image>
              </el-carousel-item>
            </el-carousel>
          </div>

          <!-- 商品信息 -->
          <div class="product-info">
            <h1 class="product-name">{{ product.name }}</h1>
            <div class="product-price">
              <span class="price">¥{{ product.price }}</span>
              <span class="original-price" v-if="product.original_price">¥{{ product.original_price }}</span>
              <span class="sales">销量: {{ product.sales }}</span>
            </div>
            
            <!-- 商品规格选择 -->
            <div class="product-specs">
              <div v-for="spec in product.specifications" :key="spec.id" class="spec-group">
                <div class="spec-name">{{ spec.name }}</div>
                <div class="spec-values">
                  <el-radio-group v-model="selectedSpecs[spec.id]">
                    <el-radio-button 
                      v-for="value in spec.values" 
                      :key="value.id"
                      :label="value.id"
                    >
                      {{ value.value }}
                    </el-radio-button>
                  </el-radio-group>
                </div>
              </div>
            </div>

            <!-- 商品数量选择 -->
            <div class="product-quantity">
              <span class="label">数量</span>
              <el-input-number 
                v-model="quantity" 
                :min="1" 
                :max="product.stock"
                size="large"
              />
            </div>

            <!-- 操作按钮 -->
            <div class="product-actions">
              <el-button 
                type="primary" 
                size="large"
                :disabled="!isSpecsSelected"
                @click="handleAddToCart"
              >
                加入购物车
              </el-button>
              <el-button 
                type="danger" 
                size="large"
                :disabled="!isSpecsSelected"
                @click="handleBuyNow"
              >
                立即购买
              </el-button>
            </div>
          </div>
        </div>

        <!-- 商品详情 -->
        <div class="product-detail">
          <el-tabs>
            <el-tab-pane label="商品详情">
              <div class="detail-content" v-html="product.description"></div>
            </el-tab-pane>
            <el-tab-pane label="商品规格">
              <el-table :data="product.specifications" border>
                <el-table-column prop="name" label="规格名称" />
                <el-table-column prop="value" label="规格值" />
              </el-table>
            </el-tab-pane>
          </el-tabs>
        </div>
      </template>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { PictureFilled } from '@element-plus/icons-vue'
import axios from '@/utils/axios'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const product = ref(null)
const quantity = ref(1)
const selectedSpecs = reactive({})

// 计算是否已选择所有规格
const isSpecsSelected = computed(() => {
  if (!product.value?.specifications) return false
  return product.value.specifications.every(spec => selectedSpecs[spec.id])
})

// 获取商品详情
const fetchProductDetail = async () => {
  loading.value = true
  try {
    const response = await axios.get(`/products/products/${route.params.id}/`)
    product.value = response.data
    // 初始化规格选择
    if (product.value.specifications) {
      product.value.specifications.forEach(spec => {
        selectedSpecs[spec.id] = ''
      })
    }
  } catch (error) {
    ElMessage.error('获取商品详情失败')
  } finally {
    loading.value = false
  }
}

// 加入购物车
const handleAddToCart = async () => {
  try {
    const specifications = Object.entries(selectedSpecs)
      .filter(([_, valueId]) => valueId) // 只包含已选择的规格
      .map(([specId, valueId]) => ({
        specification_id: specId,
        value_id: valueId
      }))

    await axios.post('/cart/items/', {
      product_id: product.value.id,
      quantity: quantity.value,
      specifications
    })
    ElMessage.success('已添加到购物车')
  } catch (error) {
    ElMessage.error('添加到购物车失败')
  }
}

// 立即购买
const handleBuyNow = async () => {
  try {
    // 先添加到购物车
    await handleAddToCart()
    // 跳转到结算页面
    router.push('/checkout')
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

onMounted(() => {
  fetchProductDetail()
})
</script>

<style scoped>
.product-detail-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.product-content {
  display: flex;
  gap: 40px;
  margin-bottom: 40px;
}

.product-gallery {
  flex: 1;
  max-width: 500px;
}

.gallery-image {
  width: 100%;
  height: 100%;
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
  flex: 1;
}

.product-name {
  font-size: 24px;
  color: #303133;
  margin-bottom: 20px;
}

.product-price {
  margin-bottom: 20px;
}

.price {
  font-size: 28px;
  color: #f56c6c;
  font-weight: bold;
  margin-right: 10px;
}

.original-price {
  font-size: 16px;
  color: #909399;
  text-decoration: line-through;
  margin-right: 10px;
}

.sales {
  color: #909399;
}

.product-specs {
  margin-bottom: 20px;
}

.spec-group {
  margin-bottom: 15px;
}

.spec-name {
  font-size: 16px;
  color: #606266;
  margin-bottom: 10px;
}

.spec-values {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.product-quantity {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.label {
  margin-right: 20px;
  color: #606266;
}

.product-actions {
  display: flex;
  gap: 20px;
}

.product-detail {
  margin-top: 40px;
}

.detail-content {
  padding: 20px;
  background: #f5f7fa;
  border-radius: 4px;
}

:deep(.el-carousel__item) {
  display: flex;
  justify-content: center;
  align-items: center;
}
</style> 