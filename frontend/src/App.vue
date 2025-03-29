<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { ElMessage } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'

const router = useRouter()
const store = useStore()

const isLoggedIn = computed(() => store.getters.isLoggedIn)
const username = computed(() => store.getters.currentUser?.username || '')

const loginDialogVisible = ref(false)
const registerDialogVisible = ref(false)
const loginFormRef = ref(null)
const registerFormRef = ref(null)

const loginForm = ref({
  username: '',
  password: ''
})

const registerForm = ref({
  username: '',
  password: '',
  confirmPassword: '',
  email: ''
})

const loginRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const registerRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== registerForm.value.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

const showLoginDialog = () => {
  loginDialogVisible.value = true
}

const showRegisterDialog = () => {
  registerDialogVisible.value = true
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  try {
    await loginFormRef.value.validate()
    // TODO: 调用登录 API
    const response = await fetch('/api/users/login/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(loginForm.value)
    })
    
    if (!response.ok) {
      throw new Error('登录失败')
    }
    
    const data = await response.json()
    store.dispatch('login', {
      user: data.user,
      token: data.token
    })
    
    loginDialogVisible.value = false
    ElMessage.success('登录成功')
  } catch (error) {
    console.error('登录失败:', error)
    ElMessage.error(error.message || '登录失败')
  }
}

const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  try {
    await registerFormRef.value.validate()
    // TODO: 调用注册 API
    const response = await fetch('/api/users/register/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        username: registerForm.value.username,
        password: registerForm.value.password,
        email: registerForm.value.email
      })
    })
    
    if (!response.ok) {
      throw new Error('注册失败')
    }
    
    registerDialogVisible.value = false
    ElMessage.success('注册成功，请登录')
    showLoginDialog()
  } catch (error) {
    console.error('注册失败:', error)
    ElMessage.error(error.message || '注册失败')
  }
}

const handleCommand = (command) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'orders':
      router.push('/order/list')
      break
    case 'address':
      router.push('/address')
      break
    case 'logout':
      store.dispatch('logout')
      router.push('/')
      ElMessage.success('已退出登录')
      break
  }
}

onMounted(() => {
  store.dispatch('initializeAuth')
})
</script>

<template>
  <div id="app">
    <router-view></router-view>

    <!-- 登录对话框 -->
    <el-dialog v-model="loginDialogVisible" title="登录" width="400px">
      <el-form :model="loginForm" :rules="loginRules" ref="loginFormRef">
        <el-form-item prop="username" label="用户名">
          <el-input v-model="loginForm.username" placeholder="请输入用户名"></el-input>
        </el-form-item>
        <el-form-item prop="password" label="密码">
          <el-input v-model="loginForm.password" type="password" placeholder="请输入密码"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="loginDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleLogin">登录</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 注册对话框 -->
    <el-dialog v-model="registerDialogVisible" title="注册" width="400px">
      <el-form :model="registerForm" :rules="registerRules" ref="registerFormRef">
        <el-form-item prop="username" label="用户名">
          <el-input v-model="registerForm.username" placeholder="请输入用户名"></el-input>
        </el-form-item>
        <el-form-item prop="password" label="密码">
          <el-input v-model="registerForm.password" type="password" placeholder="请输入密码"></el-input>
        </el-form-item>
        <el-form-item prop="confirmPassword" label="确认密码">
          <el-input v-model="registerForm.confirmPassword" type="password" placeholder="请再次输入密码"></el-input>
        </el-form-item>
        <el-form-item prop="email" label="邮箱">
          <el-input v-model="registerForm.email" placeholder="请输入邮箱"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="registerDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleRegister">注册</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  height: 100vh;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 确保对话框显示在最上层 */
.el-dialog {
  z-index: 2000 !important;
}

.el-dialog__wrapper {
  z-index: 2000 !important;
}
</style>
