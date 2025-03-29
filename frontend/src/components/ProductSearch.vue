<template>
  <div class="search-container">
    <el-input
      v-model="searchQuery"
      placeholder="搜索商品"
      class="search-input"
      clearable
      @keyup.enter="handleSearch"
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
    router.push({
      path: '/products',
      query: { 
        q: searchQuery.value.trim(),
        page: 1  // 重置页码
      }
    })
  }
}

// 监听路由参数变化，同步搜索框的值
watch(() => route.query.q, (newQuery) => {
  if (newQuery) {
    searchQuery.value = newQuery
  }
})
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