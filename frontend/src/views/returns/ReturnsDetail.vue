import request from '@/utils/request'

const fetchReturnDetail = async () => {
  loading.value = true
  try {
    const response = await request({
      url: `/returns/requests/${route.params.id}/`,
      method: 'get'
    })
    
    returnDetail.value = response
  } catch (error) {
    console.error('获取退换货详情失败:', error)
    ElMessage.error(error.message || '获取退换货详情失败')
  } finally {
    loading.value = false
  }
} 