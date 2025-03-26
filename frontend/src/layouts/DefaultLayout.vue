<template>
  <el-container class="layout-container">
    <el-header>
      <div class="header-content">
        <div class="logo">
          购物平台
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
          <template v-if="userStore.token">
            <el-dropdown>
              <span class="el-dropdown-link">
                {{ userStore.userInfo?.username }}
                <el-icon class="el-icon--right">
                  <arrow-down />
                </el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
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
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
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
  font-size: 24px;
  font-weight: bold;
  margin-right: 40px;
}

.user-info {
  margin-left: 20px;
}

.el-dropdown-link {
  cursor: pointer;
  display: flex;
  align-items: center;
}

.el-footer {
  text-align: center;
  color: #666;
  padding: 20px;
}
</style> 