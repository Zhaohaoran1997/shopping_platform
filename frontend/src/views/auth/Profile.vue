<template>
  <div class="profile-container">
    <el-card class="profile-card">
      <template #header>
        <h2>个人信息</h2>
      </template>
      
      <el-tabs v-model="activeTab">
        <el-tab-pane label="基本信息" name="basic">
          <el-form
            ref="profileFormRef"
            :model="profileForm"
            :rules="profileRules"
            label-width="100px"
          >
            <el-form-item label="用户名" prop="username">
              <el-input v-model="profileForm.username" disabled />
            </el-form-item>
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="profileForm.email" />
            </el-form-item>
            <el-form-item label="手机号" prop="phone">
              <el-input v-model="profileForm.phone" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleUpdateProfile" :loading="loading">
                保存修改
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="修改密码" name="password">
          <el-form
            ref="passwordFormRef"
            :model="passwordForm"
            :rules="passwordRules"
            label-width="100px"
          >
            <el-form-item label="当前密码" prop="currentPassword">
              <el-input
                v-model="passwordForm.currentPassword"
                type="password"
                show-password
              />
            </el-form-item>
            <el-form-item label="新密码" prop="newPassword">
              <el-input
                v-model="passwordForm.newPassword"
                type="password"
                show-password
              />
            </el-form-item>
            <el-form-item label="确认新密码" prop="confirmPassword">
              <el-input
                v-model="passwordForm.confirmPassword"
                type="password"
                show-password
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleChangePassword" :loading="loading">
                修改密码
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const authStore = useAuthStore()
const activeTab = ref('basic')
const loading = ref(false)
const profileFormRef = ref(null)
const passwordFormRef = ref(null)

const profileForm = reactive({
  username: '',
  email: '',
  phone: ''
})

const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const validatePass = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请输入新密码'))
  } else {
    if (passwordForm.confirmPassword !== '') {
      passwordFormRef.value?.validateField('confirmPassword')
    }
    callback()
  }
}

const validatePass2 = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入新密码'))
  } else if (value !== passwordForm.newPassword) {
    callback(new Error('两次输入密码不一致!'))
  } else {
    callback()
  }
}

const profileRules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ]
}

const passwordRules = {
  currentPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, validator: validatePass, trigger: 'blur' },
    { min: 6, max: 20, message: '长度在 6 到 20 个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, validator: validatePass2, trigger: 'blur' }
  ]
}

onMounted(() => {
  const user = authStore.user
  if (user) {
    profileForm.username = user.username
    profileForm.email = user.email
    profileForm.phone = user.phone || ''
  }
})

const handleUpdateProfile = async () => {
  if (!profileFormRef.value) return
  
  try {
    await profileFormRef.value.validate()
    loading.value = true
    
    await authStore.updateProfile(profileForm)
    ElMessage.success('个人信息更新成功')
  } catch (error) {
    ElMessage.error(error.message || '更新失败')
  } finally {
    loading.value = false
  }
}

const handleChangePassword = async () => {
  if (!passwordFormRef.value) return
  
  try {
    await passwordFormRef.value.validate()
    loading.value = true
    
    await authStore.changePassword({
      current_password: passwordForm.currentPassword,
      new_password: passwordForm.newPassword
    })
    
    ElMessage.success('密码修改成功')
    passwordForm.currentPassword = ''
    passwordForm.newPassword = ''
    passwordForm.confirmPassword = ''
  } catch (error) {
    ElMessage.error(error.message || '密码修改失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.profile-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.profile-card {
  margin-top: 20px;
}

.profile-card :deep(.el-card__header) {
  text-align: center;
}

h2 {
  margin: 0;
  color: #303133;
}
</style> 