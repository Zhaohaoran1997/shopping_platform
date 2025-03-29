<template>
  <el-container class="layout-container">
    <el-header>
      <div class="header-content">
        <div class="logo">
          购物平台
        </div>
        <div class="search-wrapper">
          <ProductSearch />
        </div>
        <el-menu
          mode="horizontal"
          :router="true"
          :default-active="route.path"
        >
          <el-menu-item index="/">首页</el-menu-item>
          <el-menu-item index="/products">商品列表</el-menu-item>
          <el-menu-item index="/cart">购物车</el-menu-item>
        </el-menu>
        <div class="user-info">
          <template v-if="authStore.isAuthenticated">
            <el-dropdown>
              <span class="el-dropdown-link">
                {{ authStore.user?.username }}
                <el-icon class="el-icon--right">
                  <arrow-down />
                </el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="$router.push('/profile')">个人信息</el-dropdown-item>
                  <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
          <template v-else>
            <el-button type="primary" @click="$router.push('/login')">登录</el-button>
          </template>
        </div>
      </div>
    </el-header>
    
    <el-main>
      <router-view />
    </el-main>
    
    <el-footer>
      © 2024 购物平台 All Rights Reserved
    </el-footer>
  </el-container>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ArrowDown } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import ProductSearch from '@/components/ProductSearch.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const handleLogout = async () => {
  try {
    await authStore.logout()
    ElMessage.success('退出登录成功')
    router.push('/login')
  } catch (error) {
    ElMessage.error('退出登录失败')
  }
}
</script>

<style scoped>
.layout-container {
  min-height: 100vh;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
}

.logo {
  font-size: 20px;
  font-weight: bold;
  color: #409EFF;
  margin-right: 20px;
}

.search-wrapper {
  flex: 1;
  max-width: 500px;
  margin: 0 20px;
}

.el-menu {
  border-bottom: none;
}

.user-info {
  display: flex;
  align-items: center;
  margin-left: 20px;
}

.el-dropdown-link {
  cursor: pointer;
  color: #409EFF;
}

.el-footer {
  text-align: center;
  color: #909399;
  padding: 20px 0;
}
</style> 