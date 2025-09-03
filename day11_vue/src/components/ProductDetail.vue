<template>
  <div class="product-detail">
    <!-- 返回按钮 -->
    <div class="back-button">
      <el-button @click="goBack" size="large">
        <i class="el-icon-back"></i>
        返回商品列表
      </el-button>
    </div>

    <!-- 商品详情内容 -->
    <div v-if="product && !loading" class="product-content">
      <!-- 商品标题区域 -->
      <div class="product-header">
        <el-card class="glass-card header-card" shadow="never">
          <div class="header-content">
            <div class="header-left">
              <div class="product-image-large">
                <i class="el-icon-picture-outline"></i>
              </div>
              <div class="product-title-info">
                <h1 class="product-title">{{ product.name }}</h1>
                <div class="product-meta">
                  <el-tag type="info" size="large">{{ product.category }}</el-tag>
                  <el-tag v-if="product.is_hot" type="warning" size="large">热门商品</el-tag>
                  <el-tag v-if="product.stock < 10" type="danger" size="large">库存不足</el-tag>
                </div>
                <div class="product-brand">
                  <strong>品牌：</strong>{{ product.brand }}
                </div>
              </div>
            </div>
            <div class="header-right">
              <div class="product-price-section">
                <div class="current-price">
                  <span class="currency">¥</span>
                  <span class="amount">{{ formatPrice(product.price) }}</span>
                </div>
                <div class="stock-info" :class="{ 'low-stock': product.stock < 10 }">
                  库存：{{ product.stock }} 件
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 商品详细信息 -->
      <el-row :gutter="30">
        <!-- 商品描述 -->
        <el-col :span="16">
          <el-card class="glass-card" shadow="never">
            <template #header>
              <div class="card-header">
                <i class="el-icon-document"></i>
                <span>商品描述</span>
              </div>
            </template>
            <div class="product-description">
              <p v-if="product.description">{{ product.description }}</p>
              <p v-else class="no-description">暂无商品描述</p>
            </div>
          </el-card>

          <!-- 商品规格 -->
          <el-card class="glass-card" shadow="never" style="margin-top: 20px;" v-if="product.specifications && Object.keys(product.specifications).length > 0">
            <template #header>
              <div class="card-header">
                <i class="el-icon-setting"></i>
                <span>商品规格</span>
              </div>
            </template>
            <div class="specifications">
              <div class="spec-grid">
                <div 
                  v-for="(value, key) in product.specifications" 
                  :key="key"
                  class="spec-item"
                >
                  <div class="spec-label">{{ key }}:</div>
                  <div class="spec-value">{{ value }}</div>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>

        <!-- 操作区域 -->
        <el-col :span="8">
          <el-card class="glass-card action-card" shadow="never">
            <template #header>
              <div class="card-header">
                <i class="el-icon-shopping-cart-2"></i>
                <span>购买操作</span>
              </div>
            </template>
            
            <div class="action-content">
              <!-- 价格信息 -->
              <div class="price-info">
                <div class="price-row">
                  <span class="label">商品价格：</span>
                  <span class="price">
                    <span class="currency">¥</span>
                    <span class="amount">{{ formatPrice(product.price) }}</span>
                  </span>
                </div>
                <div class="price-row">
                  <span class="label">库存状态：</span>
                  <span class="stock" :class="{ 'in-stock': product.stock > 10, 'low-stock': product.stock <= 10 && product.stock > 0, 'out-of-stock': product.stock === 0 }">
                    {{ getStockStatus(product.stock) }}
                  </span>
                </div>
              </div>

              <!-- 购买数量 -->
              <div class="quantity-section">
                <div class="quantity-label">购买数量：</div>
                <el-input-number 
                  v-model="quantity" 
                  :min="1" 
                  :max="product.stock"
                  :disabled="product.stock === 0"
                />
              </div>

              <!-- 操作按钮 -->
              <div class="action-buttons">
                <el-button 
                  type="primary" 
                  size="large" 
                  @click="addToCart"
                  :disabled="product.stock === 0"
                  class="action-btn"
                >
                  <i class="el-icon-shopping-cart-2"></i>
                  加入收藏
                </el-button>
                <el-button 
                  type="success" 
                  size="large" 
                  @click="buyNow"
                  :disabled="product.stock === 0"
                  class="action-btn"
                >
                  <i class="el-icon-check"></i>
                  立即购买
                </el-button>
                <el-button 
                  size="large" 
                  @click="shareProduct"
                  class="action-btn"
                >
                  <i class="el-icon-share"></i>
                  分享商品
                </el-button>
              </div>

              <!-- 商品信息摘要 -->
              <div class="product-summary">
                <div class="summary-item">
                  <span class="label">商品编号：</span>
                  <span class="value">{{ product.product_id }}</span>
                </div>
                <div class="summary-item">
                  <span class="label">最后更新：</span>
                  <span class="value">{{ formatDate(product.updated_at) }}</span>
                </div>
              </div>
            </div>
          </el-card>

          <!-- 推荐商品 -->
          <el-card class="glass-card" shadow="never" style="margin-top: 20px;">
            <template #header>
              <div class="card-header">
                <i class="el-icon-star-on"></i>
                <span>相关推荐</span>
                <el-button @click="loadRecommendations" size="small" class="refresh-btn">
                  <i class="el-icon-refresh"></i>
                </el-button>
              </div>
            </template>
            
            <div class="recommendations" v-if="recommendations.length > 0">
              <div 
                v-for="rec in recommendations" 
                :key="rec.product_id"
                class="recommendation-item"
                @click="viewRecommendation(rec)"
              >
                <div class="rec-image">
                  <i class="el-icon-picture-outline"></i>
                </div>
                <div class="rec-info">
                  <div class="rec-name">{{ rec.name }}</div>
                  <div class="rec-price">¥{{ formatPrice(rec.price) }}</div>
                </div>
              </div>
            </div>
            <div v-else class="no-recommendations">
              <p>暂无相关推荐</p>
              <el-button @click="loadRecommendations" size="small" type="primary">
                获取推荐
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 加载状态 -->
    <div class="loading-state" v-if="loading">
      <el-card class="glass-card" shadow="never">
        <div class="loading-content">
          <el-icon class="is-loading">
            <Loading />
          </el-icon>
          <p>正在加载商品详情...</p>
        </div>
      </el-card>
    </div>

    <!-- 错误状态 -->
    <div class="error-state" v-if="error && !loading">
      <el-card class="glass-card" shadow="never">
        <div class="error-content">
          <i class="el-icon-warning"></i>
          <h3>加载失败</h3>
          <p>{{ error }}</p>
          <el-button type="primary" @click="loadProduct">重新加载</el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import axios from 'axios'

const route = useRoute()
const router = useRouter()

// 响应式数据
const loading = ref(false)
const error = ref('')
const product = ref(null)
const quantity = ref(1)
const recommendations = ref([])

// 获取商品详情
const loadProduct = async () => {
  const productId = route.params.productId
  if (!productId) {
    error.value = '商品ID不存在'
    return
  }

  loading.value = true
  error.value = ''

  try {
    const response = await axios.get(`http://localhost:8000/api/products/detail/${productId}/`)

    if (response.data.success) {
      product.value = response.data.product
      ElMessage.success('商品详情加载成功')
      
      // 记录用户浏览行为
      await recordViewBehavior(productId)
    } else {
      error.value = response.data.error || '加载商品详情失败'
    }
  } catch (err) {
    console.error('加载商品详情错误:', err)
    if (err.response?.status === 404) {
      error.value = '商品不存在'
    } else {
      error.value = '网络错误，请稍后重试'
    }
  } finally {
    loading.value = false
  }
}

// 记录用户浏览行为
const recordViewBehavior = async (productId) => {
  try {
    const currentUserId = localStorage.getItem('currentUserId') || 'user_001'
    
    const response = await axios.post('http://localhost:8000/user_behavior/api/record/', {
      user_id: currentUserId,
      product_id: productId
    })

    if (response.data.code === 1) {
      console.log('用户浏览行为记录成功:', response.data.message)
    } else {
      console.warn('用户浏览行为记录失败:', response.data.message)
    }
  } catch (error) {
    console.error('记录用户浏览行为失败:', error)
    // 不影响主要功能，只记录日志
  }
}

// 加载推荐商品
const loadRecommendations = async () => {
  try {
    // 这里可以调用推荐API，暂时使用模拟数据
    const response = await axios.post('http://localhost:8000/recommendation/api/recommend/', {
      user_id: window.getCurrentUserId ? window.getCurrentUserId() : 'user_001',
      recommendation_type: 'content',
      limit: 5,
      category: product.value?.category
    })

    if (response.data.success) {
      recommendations.value = response.data.recommendations.filter(
        rec => rec.product_id !== product.value?.product_id
      ).slice(0, 3)
    }
  } catch (error) {
    console.error('加载推荐失败:', error)
  }
}

// 返回商品列表
const goBack = () => {
  router.push({ name: 'ProductList' })
}

// 加入收藏
const addToCart = () => {
  ElMessage.success(`已将${quantity.value}件"${product.value.name}"加入收藏`)
  // 这里可以添加实际的收藏逻辑
}

// 立即购买
const buyNow = async () => {
  try {
    await ElMessageBox.confirm(
      `确认购买${quantity.value}件"${product.value.name}"？总价：¥${(product.value.price * quantity.value).toFixed(2)}`,
      '确认购买',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    ElMessage.success('购买成功！')
    // 这里可以添加实际的购买逻辑
  } catch {
    ElMessage.info('已取消购买')
  }
}

// 分享商品
const shareProduct = () => {
  const shareText = `推荐商品：${product.value.name} - ¥${formatPrice(product.value.price)}`
  
  if (navigator.share) {
    navigator.share({
      title: product.value.name,
      text: shareText,
      url: window.location.href,
    })
  } else {
    // 复制链接到剪贴板
    navigator.clipboard.writeText(window.location.href).then(() => {
      ElMessage.success('商品链接已复制到剪贴板')
    }).catch(() => {
      ElMessage.success('分享功能暂不可用')
    })
  }
}

// 查看推荐商品
const viewRecommendation = (rec) => {
  router.push({
    name: 'ProductDetail',
    params: { productId: rec.product_id }
  })
}

// 获取库存状态
const getStockStatus = (stock) => {
  if (stock === 0) return '缺货'
  if (stock <= 10) return '库存紧张'
  return '有库存'
}

// 格式化价格
const formatPrice = (price) => {
  return parseFloat(price || 0).toFixed(2)
}

// 格式化日期
const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

// 组件挂载时加载商品详情
onMounted(() => {
  loadProduct()
})

// 监听路由变化，重新加载商品
watch(() => route.params.productId, () => {
  if (route.params.productId) {
    loadProduct()
  }
})
</script>

<style scoped>
.product-detail {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* 返回按钮 */
.back-button {
  margin-bottom: 20px;
}

/* 商品标题区域 */
.product-header {
  margin-bottom: 30px;
}

.header-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  backdrop-filter: blur(20px);
  border-radius: 15px !important;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 30px 0;
}

.header-left {
  display: flex;
  gap: 30px;
  flex: 1;
}

.product-image-large {
  width: 200px;
  height: 200px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 4rem;
  color: rgba(255, 255, 255, 0.3);
}

.product-title-info {
  flex: 1;
}

.product-title {
  color: white;
  font-size: 2.5rem;
  margin: 0 0 20px 0;
  font-weight: 700;
  line-height: 1.2;
}

.product-meta {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.product-brand {
  color: rgba(255, 255, 255, 0.8);
  font-size: 1.1rem;
}

.product-brand strong {
  color: white;
}

.header-right {
  min-width: 200px;
}

.product-price-section {
  text-align: right;
}

.current-price {
  display: flex;
  align-items: baseline;
  justify-content: flex-end;
  gap: 5px;
  margin-bottom: 15px;
}

.currency {
  color: #4facfe;
  font-size: 1.5rem;
  font-weight: 500;
}

.amount {
  color: #4facfe;
  font-size: 3rem;
  font-weight: 700;
}

.stock-info {
  color: rgba(255, 255, 255, 0.8);
  font-size: 1.1rem;
  font-weight: 500;
}

.stock-info.low-stock {
  color: #f56c6c;
}

/* 商品描述 */
.product-description {
  color: rgba(255, 255, 255, 0.9);
  font-size: 1rem;
  line-height: 1.8;
  padding: 20px 0;
}

.no-description {
  color: rgba(255, 255, 255, 0.5);
  font-style: italic;
}

/* 规格参数 */
.specifications {
  padding: 20px 0;
}

.spec-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.spec-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.03);
  padding: 12px 15px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.spec-label {
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
}

.spec-value {
  color: white;
  font-weight: 600;
}

/* 操作卡片 */
.action-card {
  position: sticky;
  top: 20px;
}

.action-content {
  padding: 20px 0;
}

.price-info {
  margin-bottom: 25px;
}

.price-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  font-size: 1rem;
}

.price-row .label {
  color: rgba(255, 255, 255, 0.7);
}

.price-row .price {
  display: flex;
  align-items: baseline;
  gap: 2px;
}

.price-row .price .currency {
  font-size: 1rem;
}

.price-row .price .amount {
  font-size: 1.5rem;
}

.stock.in-stock {
  color: #67c23a;
}

.stock.low-stock {
  color: #e6a23c;
}

.stock.out-of-stock {
  color: #f56c6c;
}

/* 购买数量 */
.quantity-section {
  margin-bottom: 25px;
}

.quantity-label {
  color: white;
  margin-bottom: 10px;
  font-weight: 500;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 25px;
}

.action-btn {
  width: 100%;
  height: 45px;
  border-radius: 8px !important;
  font-size: 1rem !important;
  font-weight: 600 !important;
}

/* 商品信息摘要 */
.product-summary {
  padding: 15px 0;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.summary-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  font-size: 0.9rem;
}

.summary-item .label {
  color: rgba(255, 255, 255, 0.6);
}

.summary-item .value {
  color: white;
}

/* 推荐商品 */
.recommendations {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.recommendation-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.recommendation-item:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
}

.rec-image {
  width: 50px;
  height: 50px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: rgba(255, 255, 255, 0.3);
}

.rec-info {
  flex: 1;
}

.rec-name {
  color: white;
  font-size: 0.9rem;
  margin-bottom: 5px;
  font-weight: 500;
}

.rec-price {
  color: #4facfe;
  font-size: 0.9rem;
  font-weight: 600;
}

.no-recommendations {
  text-align: center;
  color: rgba(255, 255, 255, 0.6);
  padding: 30px 0;
}

/* 加载和错误状态 */
.loading-state, .error-state {
  margin: 50px 0;
}

.loading-content, .error-content {
  text-align: center;
  padding: 80px 20px;
  color: rgba(255, 255, 255, 0.7);
}

.loading-content i, .error-content i {
  font-size: 4rem;
  color: #4facfe;
  margin-bottom: 20px;
}

.error-content i {
  color: #f56c6c;
}

.error-content h3 {
  color: white;
  font-size: 1.5rem;
  margin: 20px 0;
}

.error-content p, .loading-content p {
  font-size: 1rem;
  margin: 0 0 20px 0;
}

/* 公共样式 */
.glass-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  backdrop-filter: blur(20px);
  border-radius: 15px !important;
  box-shadow: 0 8px 32px rgba(31, 38, 135, 0.1);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: white;
  font-weight: 600;
}

.card-header i {
  margin-right: 10px;
  color: #4facfe;
}

.refresh-btn {
  background: rgba(255, 255, 255, 0.1) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  color: white !important;
  border-radius: 8px !important;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 30px;
  }
  
  .header-left {
    flex-direction: column;
    gap: 20px;
    text-align: center;
  }
  
  .product-image-large {
    margin: 0 auto;
  }
  
  .product-title {
    font-size: 2rem;
  }
  
  .current-price .amount {
    font-size: 2rem;
  }
  
  .action-card {
    position: static;
  }
}

/* Element Plus 样式覆盖 */
:deep(.el-card__header) {
  background: transparent !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
  color: white !important;
}

:deep(.el-card__body) {
  background: transparent !important;
}

:deep(.el-input-number .el-input__inner) {
  background: rgba(255, 255, 255, 0.1) !important;
  border-color: rgba(255, 255, 255, 0.2) !important;
  color: white !important;
}
</style>
