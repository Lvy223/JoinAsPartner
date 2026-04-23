// API配置文件
// 这里配置后端API的基础URL

// 开发环境
const DEV_BASE_URL = 'http://localhost:8000/api'

// 生产环境
const PROD_BASE_URL = 'https://your-production-api.com/api'

// 根据环境选择基础URL
const BASE_URL = process.env.NODE_ENV === 'production' ? PROD_BASE_URL : DEV_BASE_URL

export default BASE_URL
