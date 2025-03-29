/**
 * 格式化日期
 * @param {string|Date} date - 日期字符串或Date对象
 * @param {string} format - 格式化模式，默认为 'YYYY-MM-DD HH:mm:ss'
 * @returns {string} 格式化后的日期字符串
 */
export function formatDate(date, format = 'YYYY-MM-DD HH:mm:ss') {
  if (!date) return ''
  
  const d = new Date(date)
  if (isNaN(d.getTime())) return ''

  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  const seconds = String(d.getSeconds()).padStart(2, '0')

  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds)
}

/**
 * 格式化相对时间
 * @param {string|Date} date - 日期字符串或Date对象
 * @returns {string} 相对时间字符串
 */
export function formatRelativeTime(date) {
  if (!date) return ''
  
  const d = new Date(date)
  if (isNaN(d.getTime())) return ''

  const now = new Date()
  const diff = now - d

  // 小于1分钟
  if (diff < 60000) {
    return '刚刚'
  }
  // 小于1小时
  if (diff < 3600000) {
    return `${Math.floor(diff / 60000)}分钟前`
  }
  // 小于24小时
  if (diff < 86400000) {
    return `${Math.floor(diff / 3600000)}小时前`
  }
  // 小于30天
  if (diff < 2592000000) {
    return `${Math.floor(diff / 86400000)}天前`
  }
  // 小于12个月
  if (diff < 31536000000) {
    return `${Math.floor(diff / 2592000000)}个月前`
  }
  // 大于12个月
  return `${Math.floor(diff / 31536000000)}年前`
}

/**
 * 格式化金额
 * @param {number} amount - 金额
 * @param {number} decimals - 小数位数，默认为2
 * @returns {string} 格式化后的金额字符串
 */
export function formatAmount(amount, decimals = 2) {
  if (amount === null || amount === undefined) return '0.00'
  return Number(amount).toFixed(decimals)
} 