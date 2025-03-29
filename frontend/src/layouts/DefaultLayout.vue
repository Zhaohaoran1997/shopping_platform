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
          :default-active="activeMenu"
          class="el-menu"
          mode="horizontal"
          router
        >
          <el-menu-item index="/">首页</el-menu-item>
          <el-menu-item index="/products">商品列表</el-menu-item>
          <el-menu-item index="/cart">购物车</el-menu-item>
          <el-menu-item index="/order/list">我的订单</el-menu-item>
        </el-menu>
        <div class="flex-grow" />
        <div class="header-right">
          <template v-if="isLoggedIn">
            <el-dropdown trigger="click" @command="handleCommand">
              <span class="user-info">
                {{ username }}
                <el-icon><arrow-down /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                  <el-dropdown-item command="address">收货地址</el-dropdown-item>
                  <el-dropdown-item command="logout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
          <template v-else>
            <el-button type="primary" @click="$router.push('/login')">登录</el-button>
            <el-button @click="$router.push('/register')">注册</el-button>
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
import { computed } from 'vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const activeMenu = computed(() => route.path)
const isLoggedIn = computed(() => authStore.isAuthenticated)
const username = computed(() => authStore.user?.username)

const handleCommand = (command) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'address':
      router.push('/address')
      break
    case 'logout':
      handleLogout()
      break
  }
}

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
  max-width: 1200px;
  margin: 0 auto;
  height: 100%;
  padding: 0 20px;
}

.logo {
  font-size: 20px;
  font-weight: bold;
  color: #409EFF;
  margin-right: 20px;
  white-space: nowrap;
  flex-shrink: 0;
}

.search-wrapper {
  width: 300px;
  margin: 0 20px;
  flex-shrink: 0;
}

.el-menu {
  border-bottom: none;
  display: flex;
  align-items: center;
  flex: 1;
  margin-right: 20px;
  justify-content: flex-start;
  min-width: 0;
}

.el-menu-item {
  white-space: nowrap;
  padding: 0 15px;
  font-size: 14px;
  flex-shrink: 0;
}

.flex-grow {
  flex: 0 0 auto;
  width: 20px;
}

.header-right {
  display: flex;
  align-items: center;
  margin-left: 20px;
  flex-shrink: 0;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: #409EFF;
  white-space: nowrap;
  font-size: 14px;
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