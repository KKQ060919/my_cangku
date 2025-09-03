<template>
  <div class="product-recommendation">
    <!-- 页面标题 -->
    <div class="page-header">
      <el-card class="glass-card header-card" shadow="never">
        <div class="header-content">
          <div class="header-left">
            <i class="el-icon-magic-stick"></i>
            <div>
              <h1>智能商品推荐</h1>
              <p>基于用户行为的个性化推荐系统</p>
            </div>
          </div>
          <div class="header-right">
            <el-tag type="success" size="large">当前用户: {{ currentUserId }}</el-tag>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 推荐控制面板 -->
    <div class="control-panel">
      <el-card class="glass-card" shadow="never">
        <template #header>
          <div class="card-header">
            <i class="el-icon-setting"></i>
            <span>推荐设置</span>
          </div>
        </template>

        <el-form :model="form" label-width="120px" class="recommendation-form">
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="推荐类型:">
                <el-select v-model="form.recommendationType" placeholder="选择推荐类型">
                  <el-option label="基于内容" value="content" />
                  <el-option label="协同过滤" value="collaborative" />
                  <el-option label="混合推荐" value="hybrid" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="商品数量:">
                <el-input-number v-model="form.limit" :min="1" :max="50" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="商品类别:">
                <el-select v-model="form.category" placeholder="选择商品类别" clearable>
                  <el-option label="全部类别" value="" />
                  <el-option 
                    v-for="category in categories" 
                    :key="category" 
                    :label="category" 
                    :value="category" 
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-form-item>
            <el-button 
              type="primary" 
              @click="getRecommendations" 
              :loading="loading"
              size="large"
            >
              <i class="el-icon-magic-stick"></i>
              获取推荐
            </el-button>
            <el-button @click="clearRecommendations" size="large">
              <i class="el-icon-delete"></i>
              清空结果
            </el-button>
            <el-button 
              @click="refreshRecommendations" 
              size="large"
              :disabled="recommendations.length === 0"
              title="手动刷新推荐"
            >
              <i class="el-icon-refresh"></i>
              刷新
            </el-button>
            <el-button 
              :type="autoRefreshEnabled ? 'success' : 'info'" 
              @click="toggleAutoRefresh" 
              size="large"
              title="切换自动刷新"
            >
              <i :class="autoRefreshEnabled ? 'el-icon-video-play' : 'el-icon-video-pause'"></i>
              {{ autoRefreshEnabled ? '自动刷新开' : '自动刷新关' }}
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>

    <!-- 推荐结果 -->
    <div class="recommendations-section" v-if="recommendations.length > 0">
      <el-card class="glass-card" shadow="never">
        <template #header>
          <div class="card-header">
            <div class="header-left">
              <i class="el-icon-goods"></i>
              <span>推荐结果 ({{ recommendations.length }})</span>
            </div>
            <div class="recommendation-stats">
              <el-tag size="small">{{ form.recommendationType }}</el-tag>
              <span class="timestamp">{{ lastUpdateTime }}</span>
            </div>
          </div>
        </template>

        <div class="products-grid">
          <div 
            v-for="(product, index) in recommendations" 
            :key="product.product_id || index"
            class="product-card"
            @click="viewProduct(product)"
          >
            <div class="product-rank">{{ index + 1 }}</div>
            <div class="product-content">
              <h3 class="product-name">{{ product.name || product.title }}</h3>
              <div class="product-details">
                <div class="product-price">
                  <span class="currency">¥</span>
                  <span class="amount">{{ formatPrice(product.price) }}</span>
                </div>
                <div class="product-category">{{ product.category }}</div>
              </div>
              <div class="product-meta">
                <el-tag v-if="product.brand" size="small" type="info">{{ product.brand }}</el-tag>
                <el-tag v-if="product.is_hot" size="small" type="warning">热门</el-tag>
                <el-tag v-if="product.source" size="small" :type="getSourceTagType(product.source)">
                  {{ getSourceLabel(product.source) }}
                </el-tag>
                <div class="confidence-score" v-if="product.score || product.final_score">
                  匹配度: {{ Math.round((product.score || product.final_score) * 100) }}%
                </div>
                <div class="similarity-info" v-if="product.similar_user_count">
                  {{ product.similar_user_count }}位用户喜欢
                </div>
              </div>
              <div class="product-reason" v-if="product.reason">
                <i class="el-icon-lightbulb"></i>
                <span>{{ product.reason }}</span>
              </div>
              <p class="product-description" v-if="product.description">
                {{ product.description.substring(0, 100) }}...
              </p>
            </div>
            <div class="product-actions">
              <el-button size="small" type="primary" @click.stop="addToInterested(product)">
                <i class="el-icon-heart"></i>
                感兴趣
              </el-button>
              <el-button size="small" @click.stop="notInterested(product)">
                <i class="el-icon-close"></i>
                不感兴趣
              </el-button>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 无推荐结果时的占位符 -->
    <div class="no-recommendations" v-else-if="!loading">
      <el-card class="glass-card" shadow="never">
        <div class="empty-state">
          <i class="el-icon-magic-stick"></i>
          <h3>开始获取个性化推荐</h3>
          <p>选择推荐类型和参数，点击"获取推荐"按钮开始</p>
        </div>
      </el-card>
    </div>

    <!-- 用户行为统计 -->
    <div class="behavior-stats">
      <el-card class="glass-card" shadow="never">
        <template #header>
          <div class="card-header">
            <i class="el-icon-pie-chart"></i>
            <span>推荐统计</span>
            <el-button @click="loadStats" size="small" class="refresh-btn">
              <i class="el-icon-refresh"></i>
            </el-button>
          </div>
        </template>

        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-value">{{ stats.total_recommendations || 0 }}</div>
            <div class="stat-label">推荐次数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ stats.total_views || 0 }}</div>
            <div class="stat-label">浏览商品</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ stats.interested_count || 0 }}</div>
            <div class="stat-label">感兴趣</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ Math.round(stats.avg_confidence || 0) }}%</div>
            <div class="stat-label">平均匹配度</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 商品详情对话框 -->
    <el-dialog v-model="productDialogVisible" title="商品详情" width="600px">
      <div v-if="selectedProduct" class="product-detail">
        <h2>{{ selectedProduct.name }}</h2>
        <div class="detail-grid">
          <div class="detail-item">
            <strong>价格:</strong>
            <span class="price">¥{{ formatPrice(selectedProduct.price) }}</span>
          </div>
          <div class="detail-item">
            <strong>类别:</strong>
            <span>{{ selectedProduct.category }}</span>
          </div>
          <div class="detail-item" v-if="selectedProduct.brand">
            <strong>品牌:</strong>
            <span>{{ selectedProduct.brand }}</span>
          </div>
          <div class="detail-item" v-if="selectedProduct.stock">
            <strong>库存:</strong>
            <span>{{ selectedProduct.stock }}</span>
          </div>
        </div>
        <div class="product-full-description" v-if="selectedProduct.description">
          <strong>商品描述:</strong>
          <p>{{ selectedProduct.description }}</p>
        </div>
        <div class="product-specs" v-if="selectedProduct.specifications">
          <strong>规格参数:</strong>
          <pre>{{ selectedProduct.specifications }}</pre>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

// 响应式数据
const loading = ref(false)
const recommendations = ref([])
const lastUpdateTime = ref('')
const stats = ref({})
const categories = ref(['电子产品', '服装', '家居', '图书', '运动'])
const currentUserId = ref(window.getCurrentUserId ? window.getCurrentUserId() : 'user_001')
const productDialogVisible = ref(false)
const selectedProduct = ref(null)
const autoRefreshEnabled = ref(true)
const refreshInterval = ref(null)
const lastInteractionTime = ref(Date.now())

// 表单数据
const form = reactive({
  recommendationType: 'hybrid',
  limit: 10,
  category: ''
})

// 获取推荐
const getRecommendations = async () => {
  loading.value = true
  
  // 记录推荐请求行为
  const startTime = Date.now()
  recordAlgorithmChoice(form.recommendationType)
  
  try {
    const response = await axios.post('http://localhost:8000/recommendation/api/recommend/', {
      user_id: currentUserId.value,
      recommendation_type: form.recommendationType,
      limit: form.limit,
      category: form.category || null
    })

    if (response.data.success) {
      recommendations.value = response.data.recommendations
      lastUpdateTime.value = new Date().toLocaleString()
      ElMessage.success(`获取到 ${recommendations.value.length} 个推荐商品`)
      
      // 记录成功的推荐获取
      const responseTime = Date.now() - startTime
      recordBehaviorAction('recommendation_success', {
        algorithm: form.recommendationType,
        result_count: recommendations.value.length,
        response_time: responseTime,
        category_filter: form.category
      })
      
      // 更新统计
      loadStats()
    } else {
      ElMessage.error(response.data.error || '获取推荐失败')
      
      // 记录失败的推荐获取
      recordBehaviorAction('recommendation_error', {
        algorithm: form.recommendationType,
        error_message: response.data.error || '未知错误'
      })
    }
  } catch (error) {
    console.error('获取推荐错误:', error)
    ElMessage.error('网络错误，请稍后重试')
    
    // 记录网络错误
    recordBehaviorAction('recommendation_network_error', {
      algorithm: form.recommendationType,
      error_message: error.message
    })
  } finally {
    loading.value = false
  }
}

// 清空推荐结果
const clearRecommendations = () => {
  recommendations.value = []
  lastUpdateTime.value = ''
  ElMessage.success('已清空推荐结果')
}

// 查看商品详情
const viewProduct = (product) => {
  selectedProduct.value = product
  productDialogVisible.value = true
  
  // 记录浏览行为
  recordProductView(product)
}

// 记录商品浏览
const recordProductView = async (product) => {
  try {
    await axios.post('http://localhost:8000/user_behavior/api/view/', {
      user_id: currentUserId.value,
      product_id: product.product_id,
      action_type: 'view'
    })
    
    // 自动记录浏览行为到统计中
    await recordBehaviorAction('product_view', {
      product_id: product.product_id,
      product_name: product.name,
      category: product.category,
      price: product.price
    })
    
  } catch (error) {
    console.error('记录浏览行为失败:', error)
  }
}

// 通用行为记录函数
const recordBehaviorAction = async (actionType, data = {}) => {
  try {
    const behaviorData = {
      user_id: currentUserId.value,
      action_type: actionType,
      timestamp: new Date().toISOString(),
      data: data
    }
    
    // 可以选择发送到后端或存储到本地
    console.log('用户行为记录:', behaviorData)
    
    // 可选：发送到用户行为统计接口
    // await axios.post('http://localhost:8000/user_behavior/api/record/', behaviorData)
    
  } catch (error) {
    console.error('记录用户行为失败:', error)
  }
}

// 自动记录页面访问
const recordPageVisit = () => {
  recordBehaviorAction('page_visit', {
    page: 'product_recommendation',
    section: 'main'
  })
}

// 记录推荐算法选择
const recordAlgorithmChoice = (algorithm) => {
  recordBehaviorAction('algorithm_selection', {
    algorithm: algorithm,
    previous_algorithm: form.recommendationType
  })
}

// 记录搜索/筛选行为
const recordFilterAction = (filterType, filterValue) => {
  recordBehaviorAction('filter_action', {
    filter_type: filterType,
    filter_value: filterValue,
    current_recommendations: recommendations.value.length
  })
}

// 添加到感兴趣
const addToInterested = async (product) => {
  try {
    await axios.post('http://localhost:8000/recommendation/api/feedback/', {
      user_id: currentUserId.value,
      product_id: product.product_id,
      feedback_type: 'interested',
      product_info: product
    })
    
    ElMessage.success('已标记为感兴趣')
    
    // 记录用户反馈行为
    recordBehaviorAction('feedback_positive', {
      product_id: product.product_id,
      product_name: product.name,
      category: product.category,
      recommendation_source: product.source || 'unknown',
      recommendation_score: product.score || product.final_score
    })
    
    // 更新统计
    loadStats()
    
  } catch (error) {
    console.error('反馈失败:', error)
    ElMessage.error('操作失败')
    
    // 记录反馈失败
    recordBehaviorAction('feedback_error', {
      product_id: product.product_id,
      feedback_type: 'interested',
      error_message: error.message
    })
  }
}

// 标记为不感兴趣
const notInterested = async (product) => {
  try {
    await axios.post('http://localhost:8000/recommendation/api/feedback/', {
      user_id: currentUserId.value,
      product_id: product.product_id,
      feedback_type: 'not_interested',
      product_info: product
    })
    
    ElMessage.success('已标记为不感兴趣')
    
    // 记录用户反馈行为
    recordBehaviorAction('feedback_negative', {
      product_id: product.product_id,
      product_name: product.name,
      category: product.category,
      recommendation_source: product.source || 'unknown',
      recommendation_score: product.score || product.final_score
    })
    
    // 从推荐结果中移除
    const index = recommendations.value.findIndex(r => r.product_id === product.product_id)
    if (index > -1) {
      recommendations.value.splice(index, 1)
      
      // 记录商品移除行为
      recordBehaviorAction('product_removed_from_recommendations', {
        product_id: product.product_id,
        remaining_count: recommendations.value.length
      })
    }
    
    // 更新统计
    loadStats()
    
  } catch (error) {
    console.error('反馈失败:', error)
    ElMessage.error('操作失败')
    
    // 记录反馈失败
    recordBehaviorAction('feedback_error', {
      product_id: product.product_id,
      feedback_type: 'not_interested',
      error_message: error.message
    })
  }
}

// 加载统计数据
const loadStats = async () => {
  try {
    const response = await axios.get(`http://localhost:8000/recommendation/api/stats/?user_id=${currentUserId.value}`)
    
    if (response.data.success) {
      stats.value = response.data.stats
    }
  } catch (error) {
    console.error('加载统计失败:', error)
  }
}

// 格式化价格
const formatPrice = (price) => {
  return parseFloat(price || 0).toFixed(2)
}

// 获取推荐来源标签类型
const getSourceTagType = (source) => {
  const typeMap = {
    'content': 'success',
    'collaborative': 'primary', 
    'hybrid': 'info'
  }
  return typeMap[source] || 'info'
}

// 获取推荐来源标签文本
const getSourceLabel = (source) => {
  const labelMap = {
    'content': '内容推荐',
    'collaborative': '协同过滤',
    'hybrid': '混合推荐'
  }
  return labelMap[source] || source
}

// 智能刷新机制 - 基于用户行为动态调整
const setupSmartRefresh = () => {
  if (!autoRefreshEnabled.value) return
  
  // 清除现有定时器
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
  }
  
  // 根据用户活跃度决定刷新间隔
  const timeSinceLastInteraction = Date.now() - lastInteractionTime.value
  let refreshDelay = 300000 // 默认5分钟
  
  if (timeSinceLastInteraction < 60000) { // 1分钟内有交互
    refreshDelay = 120000 // 2分钟
  } else if (timeSinceLastInteraction < 300000) { // 5分钟内有交互
    refreshDelay = 240000 // 4分钟
  }
  
  refreshInterval.value = setInterval(async () => {
    // 如果有推荐结果且用户最近有交互，才自动刷新
    if (recommendations.value.length > 0 && Date.now() - lastInteractionTime.value < 600000) {
      await refreshRecommendations()
    }
  }, refreshDelay)
}

// 刷新推荐（静默更新）
const refreshRecommendations = async () => {
  if (loading.value) return // 避免重复请求
  
  try {
    const response = await axios.post('http://localhost:8000/recommendation/api/recommend/', {
      user_id: currentUserId.value,
      recommendation_type: form.recommendationType,
      limit: form.limit,
      category: form.category || null
    })

    if (response.data.success) {
      const newRecommendations = response.data.recommendations
      
      // 智能更新：只有当推荐结果有明显变化时才通知用户
      const hasSignificantChange = checkRecommendationChanges(recommendations.value, newRecommendations)
      
      recommendations.value = newRecommendations
      lastUpdateTime.value = new Date().toLocaleString()
      
      if (hasSignificantChange) {
        ElMessage.success(`推荐已更新，发现 ${newRecommendations.length} 个新商品`)
        
        // 记录自动更新行为
        recordBehaviorAction('auto_recommendation_update', {
          new_count: newRecommendations.length,
          has_significant_change: hasSignificantChange
        })
      }
      
      // 更新统计
      loadStats()
    }
  } catch (error) {
    console.error('自动刷新推荐失败:', error)
  }
}

// 检查推荐变化
const checkRecommendationChanges = (oldRecs, newRecs) => {
  if (oldRecs.length === 0) return true
  if (Math.abs(oldRecs.length - newRecs.length) > 2) return true
  
  // 检查前5个推荐是否有变化
  const oldTop5 = oldRecs.slice(0, 5).map(r => r.product_id)
  const newTop5 = newRecs.slice(0, 5).map(r => r.product_id)
  
  const changedCount = newTop5.filter(id => !oldTop5.includes(id)).length
  return changedCount >= 2 // 如果前5个中有2个或更多不同，认为有显著变化
}

// 更新用户交互时间
const updateInteractionTime = () => {
  lastInteractionTime.value = Date.now()
}

// 切换自动刷新
const toggleAutoRefresh = () => {
  autoRefreshEnabled.value = !autoRefreshEnabled.value
  
  if (autoRefreshEnabled.value) {
    setupSmartRefresh()
    ElMessage.success('自动刷新已开启')
    recordBehaviorAction('auto_refresh_enabled')
  } else {
    if (refreshInterval.value) {
      clearInterval(refreshInterval.value)
      refreshInterval.value = null
    }
    ElMessage.info('自动刷新已关闭')
    recordBehaviorAction('auto_refresh_disabled')
  }
}

// 组件挂载时加载统计数据和记录页面访问
onMounted(() => {
  recordPageVisit()
  loadStats()
  
  // 监听表单变化，记录用户筛选行为
  watchFormChanges()
  
  // 启动智能刷新
  setupSmartRefresh()
  
  // 监听用户交互
  document.addEventListener('click', updateInteractionTime)
  document.addEventListener('scroll', updateInteractionTime)
  document.addEventListener('keypress', updateInteractionTime)
})

// 组件卸载时清理
onUnmounted(() => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
  }
  
  // 移除事件监听器
  document.removeEventListener('click', updateInteractionTime)
  document.removeEventListener('scroll', updateInteractionTime)
  document.removeEventListener('keypress', updateInteractionTime)
})

// 监听表单变化
const watchFormChanges = () => {
  // 监听推荐类型变化
  let previousRecommendationType = form.recommendationType
  
  // 添加表单监听器（这里简化，实际可以用watch）
  const formChangeHandler = () => {
    if (form.recommendationType !== previousRecommendationType) {
      recordFilterAction('recommendation_type', form.recommendationType)
      previousRecommendationType = form.recommendationType
      updateInteractionTime()
    }
  }
  
  // 可以添加其他表单监听逻辑
}
</script>

<style scoped>
.product-recommendation {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* 页面标题 */
.page-header {
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
  align-items: center;
  padding: 30px 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.header-left i {
  font-size: 3rem;
  color: #4facfe;
}

.header-left h1 {
  color: white;
  font-size: 2rem;
  margin: 0 0 10px 0;
  font-weight: 700;
}

.header-left p {
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
  font-size: 1.1rem;
}

/* 控制面板 */
.control-panel {
  margin-bottom: 30px;
}

.recommendation-form {
  padding: 20px 0;
}

.recommendation-form :deep(.el-form-item__label) {
  color: white !important;
  font-weight: 500 !important;
}

.recommendation-form :deep(.el-select),
.recommendation-form :deep(.el-input-number) {
  width: 100%;
}

/* 推荐结果 */
.recommendations-section {
  margin-bottom: 30px;
}

.recommendation-stats {
  display: flex;
  align-items: center;
  gap: 15px;
}

.timestamp {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.85rem;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
  padding: 20px 0;
}

.product-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 20px;
  position: relative;
  cursor: pointer;
  transition: all 0.3s ease;
}

.product-card:hover {
  transform: translateY(-3px);
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

.product-rank {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 30px;
  height: 30px;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 0.9rem;
}

.product-name {
  color: white;
  font-size: 1.2rem;
  margin: 0 0 15px 0;
  font-weight: 600;
  line-height: 1.3;
}

.product-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.product-price {
  display: flex;
  align-items: baseline;
  gap: 2px;
}

.currency {
  color: #4facfe;
  font-size: 1.1rem;
  font-weight: 500;
}

.amount {
  color: #4facfe;
  font-size: 1.4rem;
  font-weight: 700;
}

.product-category {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
  background: rgba(255, 255, 255, 0.1);
  padding: 4px 8px;
  border-radius: 4px;
}

.product-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

.confidence-score {
  color: #4facfe;
  font-size: 0.85rem;
  font-weight: 500;
}

.similarity-info {
  color: #67C23A;
  font-size: 0.8rem;
  font-weight: 500;
}

.product-reason {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 12px 0;
  padding: 8px 12px;
  background: rgba(79, 172, 254, 0.1);
  border-radius: 8px;
  border-left: 3px solid #4facfe;
}

.product-reason i {
  color: #4facfe;
  font-size: 0.9rem;
}

.product-reason span {
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.85rem;
  line-height: 1.4;
}

.product-description {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
  line-height: 1.5;
  margin: 15px 0;
}

.product-actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

.product-actions .el-button {
  flex: 1;
  border-radius: 8px !important;
}

/* 空状态 */
.no-recommendations {
  margin-bottom: 30px;
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: rgba(255, 255, 255, 0.7);
}

.empty-state i {
  font-size: 4rem;
  color: #4facfe;
  margin-bottom: 20px;
}

.empty-state h3 {
  color: white;
  font-size: 1.5rem;
  margin: 20px 0;
}

.empty-state p {
  font-size: 1rem;
  margin: 0;
}

/* 统计面板 */
.behavior-stats {
  margin-bottom: 30px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 30px;
  padding: 20px 0;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: #4facfe;
  margin-bottom: 8px;
}

.stat-label {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}

/* 商品详情对话框 */
.product-detail h2 {
  color: #2c3e50;
  margin-bottom: 20px;
  font-size: 1.5rem;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 8px;
}

.detail-item strong {
  color: #495057;
}

.detail-item .price {
  color: #4facfe;
  font-weight: 600;
  font-size: 1.1rem;
}

.product-full-description,
.product-specs {
  margin-top: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.product-full-description strong,
.product-specs strong {
  color: #495057;
  display: block;
  margin-bottom: 10px;
}

.product-specs pre {
  white-space: pre-wrap;
  font-family: inherit;
  margin: 0;
  color: #6c757d;
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

.header-left {
  display: flex;
  align-items: center;
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
    gap: 20px;
    text-align: center;
  }
  
  .products-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
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

:deep(.el-select .el-input__inner),
:deep(.el-input-number .el-input__inner) {
  background: rgba(255, 255, 255, 0.1) !important;
  border-color: rgba(255, 255, 255, 0.2) !important;
  color: white !important;
}

:deep(.el-select .el-input__inner::placeholder),
:deep(.el-input-number .el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.6) !important;
}
</style>
