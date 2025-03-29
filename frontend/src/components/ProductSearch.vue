<template>
  <div class="search-container">
    <el-input
      v-model="searchQuery"
      placeholder="搜索商品"
      class="search-input"
      clearable
      @keyup.enter="handleSearch"
      @clear="handleClear"
    >
      <template #prefix>
        <el-icon><search /></el-icon>
      </template>
    </el-input>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Search } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const searchQuery = ref('')

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    // 如果当前不在商品列表页面，先跳转到商品列表页面
    if (route.path !== '/products') {
      router.push({
        path: '/products',
        query: { 
          q: searchQuery.value.trim(),
          page: 1  // 重置页码
        }
      })
    } else {
      // 如果已经在商品列表页面，只更新查询参数
      router.push({
        query: { 
          ...route.query,
          q: searchQuery.value.trim(),
          page: 1  // 重置页码
        }
      })
    }
  }
}

const handleClear = () => {
  searchQuery.value = ''
  // 如果当前不在商品列表页面，先跳转到商品列表页面
  if (route.path !== '/products') {
    router.push({
      path: '/products',
      query: { page: 1 }  // 重置页码
    })
  } else {
    // 如果已经在商品列表页面，只更新查询参数
    const query = { ...route.query }
    delete query.q
    router.push({ query })
  }
}

// 监听路由参数变化，同步搜索框的值
watch(() => route.query.q, (newQuery) => {
  if (newQuery) {
    searchQuery.value = newQuery
  } else {
    searchQuery.value = ''
  }
}, { immediate: true })
</script>

<style scoped>
.search-container {
  max-width: 500px;
  margin: 0 auto;
}

.search-input {
  width: 100%;
}
</style> 