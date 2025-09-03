<template>
  <div class="home-page">
    <!-- 欢迎横幅 -->
    <div class="hero-section">
      <el-card class="glass-card hero-card" shadow="never">
        <div class="hero-content">
          <div class="hero-text">
            <h1>欢迎使用智能商品推荐系统</h1>
            <p>基于AI的个性化推荐，让购物更智能</p>
            <div class="hero-features">
              <div class="feature-item">
                <i class="el-icon-magic-stick"></i>
                <span>智能推荐</span>
              </div>
              <div class="feature-item">
                <i class="el-icon-chat-dot-round"></i>
                <span>智能问答</span>
              </div>
              <div class="feature-item">
                <i class="el-icon-user-solid"></i>
                <span>行为分析</span>
              </div>
            </div>
            <div class="hero-actions">
              <el-button type="primary" size="large" @click="goToRecommendations">
                <i class="el-icon-magic-stick"></i>
                开始推荐
              </el-button>
              <el-button size="large" @click="goToQA">
                <i class="el-icon-chat-dot-round"></i>
                智能问答
              </el-button>
            </div>
          </div>
          <div class="hero-image">
            <div class="floating-cards">
              <div class="card-item card-1">📱</div>
              <div class="card-item card-2">💻</div>
              <div class="card-item card-3">🎧</div>
              <div class="card-item card-4">📚</div>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 快速功能区 -->
    <div class="features-section">
      <div class="features-grid">
        <el-card
          v-for="feature in features"
          :key="feature.name"
          class="glass-card feature-card"
          shadow="never"
          @click="goToPage(feature.path)"
        >
          <div class="feature-content">
            <div class="feature-icon">
              <i :class="feature.icon"></i>
            </div>
            <h3>{{ feature.name }}</h3>
            <p>{{ feature.description }}</p>
            <div class="feature-stats" v-if="feature.stats">
              <span class="stat-item">
                <strong>{{ feature.stats.count || 0 }}</strong>
                <small>{{ feature.stats.label }}</small>
              </span>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 系统状态概览 -->
    <div class="status-section">
      <el-card class="glass-card status-card" shadow="never">
        <template #header>
          <div class="card-header">
            <i class="el-icon-monitor"></i>
            <span>系统状态</span>
            <el-button @click="loadSystemStatus" size="small" class="refresh-btn">
              <i class="el-icon-refresh"></i>
            </el-button>
          </div>
        </template>
        
        <div class="status-grid">
          <div class="status-item">
            <div class="status-value">{{ systemStatus.product_count || 0 }}</div>
            <div class="status-label">商品总数</div>
          </div>
          <div class="status-item">
            <div class="status-value">{{ systemStatus.hot_products_count || 0 }}</div>
            <div class="status-label">热门商品</div>
          </div>
          <div class="status-item">
            <div class="status-value">{{ systemStatus.cache_stats?.total_products || 0 }}</div>
            <div class="status-label">缓存商品</div>
          </div>
          <div class="status-item">
            <div class="status-value">{{ systemStatus.behavior_stats?.total_users || 0 }}</div>
            <div class="status-label">活跃用户</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 最近活动 -->
    <div class="activity-section">
      <el-card class="glass-card activity-card" shadow="never">
        <template #header>
          <div class="card-header">
            <i class="el-icon-bell"></i>
            <span>系统活动</span>
          </div>
        </template>
        
        <div v-if="activities.length === 0" class="no-activity">
          <i class="el-icon-info"></i>
          <p>暂无系统活动记录</p>
        </div>
        
        <div v-else class="activity-list">
          <div 
            v-for="(activity, index) in activities" 
            :key="index" 
            class="activity-item"
          >
            <div class="activity-icon">
              <i :class="activity.icon"></i>
            </div>
            <div class="activity-content">
              <div class="activity-title">{{ activity.title }}</div>
              <div class="activity-time">{{ activity.time }}</div>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const router = useRouter()

// 响应式数据
const systemStatus = ref({})
const activities = ref([])

// 功能配置
const features = [
  {
    name: '智能推荐',
    description: '基于用户行为的个性化商品推荐',
    icon: 'el-icon-magic-stick',
    path: '/recommendations',
    stats: { count: 0, label: '推荐商品' }
  },
  {
    name: '智能问答',
    description: 'RAG技术驱动的商品咨询问答',
    icon: 'el-icon-chat-dot-round',
    path: '/qa',
    stats: { count: 0, label: '对话次数' }
  },
  {
    name: '用户行为',
    description: '用户浏览和购买行为分析',
    icon: 'el-icon-user-solid',
    path: '/behavior',
    stats: { count: 0, label: '行为记录' }
  },
  {
    name: '系统统计',
    description: '系统运行状态和性能监控',
    icon: 'el-icon-data-analysis',
    path: '/stats',
    stats: { count: 0, label: '统计数据' }
  }
]

// 跳转到推荐页面
const goToRecommendations = () => {
  router.push('/recommendations')
}

// 跳转到问答页面
const goToQA = () => {
  router.push('/qa')
}

// 跳转到指定页面
const goToPage = (path) => {
  router.push(path)
}

// 加载系统状态
const loadSystemStatus = async () => {
  try {
    // 加载缓存状态
    const cacheResponse = await axios.get('http://localhost:8000/cache_management/api/stats/')
    if (cacheResponse.data.success) {
      systemStatus.value.cache_stats = cacheResponse.data.stats
    }

    // 加载用户行为状态
    const behaviorResponse = await axios.get('http://localhost:8000/user_behavior/api/stats/')
    if (behaviorResponse.data.success) {
      systemStatus.value.behavior_stats = behaviorResponse.data.stats
    }

    // 加载推荐系统状态
    const recommendationResponse = await axios.get('http://localhost:8000/recommendation/api/stats/')
    if (recommendationResponse.data.success) {
      systemStatus.value.recommendation_stats = recommendationResponse.data.stats
    }

    // 模拟商品统计数据
    systemStatus.value.product_count = 100
    systemStatus.value.hot_products_count = 20

    // 更新功能卡片统计
    features[0].stats.count = systemStatus.value.recommendation_stats?.recommended_products || 0
    features[1].stats.count = systemStatus.value.cache_stats?.total_queries || 0
    features[2].stats.count = systemStatus.value.behavior_stats?.total_views || 0
    features[3].stats.count = Object.keys(systemStatus.value).length

  } catch (error) {
    console.error('加载系统状态失败:', error)
  }
}

// 加载活动记录
const loadActivities = () => {
  // 模拟活动数据
  activities.value = [
    {
      title: '系统初始化完成',
      time: '刚刚',
      icon: 'el-icon-check'
    },
    {
      title: '缓存预热完成',
      time: '2分钟前',
      icon: 'el-icon-loading'
    },
    {
      title: '向量数据库构建完成',
      time: '5分钟前',
      icon: 'el-icon-document'
    }
  ]
}

// 组件挂载时加载数据
onMounted(() => {
  loadSystemStatus()
  loadActivities()
})
</script>

<style scoped>
.home-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* 欢迎横幅 */
.hero-section {
  margin-bottom: 40px;
}

.hero-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  backdrop-filter: blur(20px);
  border-radius: 20px !important;
}

.hero-content {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 40px;
  align-items: center;
  padding: 40px 0;
}

.hero-text h1 {
  font-size: 2.5rem;
  color: white;
  margin-bottom: 20px;
  font-weight: 700;
  line-height: 1.2;
}

.hero-text p {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 30px;
}

.hero-features {
  display: flex;
  gap: 30px;
  margin-bottom: 40px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
}

.feature-item i {
  color: #4facfe;
  font-size: 1.2rem;
}

.hero-actions {
  display: flex;
  gap: 15px;
}

.hero-actions .el-button {
  border-radius: 12px !important;
  padding: 12px 24px !important;
  font-weight: 600 !important;
}

/* 浮动卡片动画 */
.hero-image {
  position: relative;
  height: 250px;
}

.floating-cards {
  position: relative;
  width: 100%;
  height: 100%;
}

.card-item {
  position: absolute;
  width: 60px;
  height: 60px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  animation: float 6s ease-in-out infinite;
}

.card-1 { top: 20px; left: 20px; animation-delay: 0s; }
.card-2 { top: 20px; right: 20px; animation-delay: 1.5s; }
.card-3 { bottom: 60px; left: 40px; animation-delay: 3s; }
.card-4 { bottom: 20px; right: 40px; animation-delay: 4.5s; }

/* 功能区 */
.features-section {
  margin-bottom: 40px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.feature-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  backdrop-filter: blur(20px);
  border-radius: 15px !important;
  cursor: pointer;
  transition: all 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 35px rgba(31, 38, 135, 0.2);
  border-color: rgba(255, 255, 255, 0.3) !important;
}

.feature-content {
  text-align: center;
  padding: 30px 20px;
}

.feature-icon {
  margin-bottom: 20px;
}

.feature-icon i {
  font-size: 3rem;
  color: #4facfe;
}

.feature-content h3 {
  color: white;
  font-size: 1.3rem;
  margin-bottom: 15px;
  font-weight: 600;
}

.feature-content p {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
  line-height: 1.6;
  margin-bottom: 20px;
}

.feature-stats {
  display: flex;
  justify-content: center;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.stat-item strong {
  color: #4facfe;
  font-size: 1.5rem;
  font-weight: 700;
}

.stat-item small {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.8rem;
}

/* 系统状态 */
.status-section {
  margin-bottom: 40px;
}

.status-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  backdrop-filter: blur(20px);
  border-radius: 15px !important;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 30px;
  padding: 20px 0;
}

.status-item {
  text-align: center;
}

.status-value {
  font-size: 2rem;
  font-weight: 700;
  color: #4facfe;
  margin-bottom: 8px;
}

.status-label {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}

/* 系统活动 */
.activity-section {
  margin-bottom: 40px;
}

.activity-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  backdrop-filter: blur(20px);
  border-radius: 15px !important;
}

.no-activity {
  text-align: center;
  padding: 40px;
  color: rgba(255, 255, 255, 0.6);
}

.no-activity i {
  font-size: 2rem;
  margin-bottom: 15px;
  color: #4facfe;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  transition: all 0.3s ease;
}

.activity-item:hover {
  background: rgba(255, 255, 255, 0.1);
}

.activity-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.activity-icon i {
  color: white;
  font-size: 1.1rem;
}

.activity-content {
  flex: 1;
}

.activity-title {
  color: white;
  font-weight: 500;
  margin-bottom: 4px;
}

.activity-time {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.8rem;
}

/* 公共样式 */
.glass-card {
  backdrop-filter: blur(20px);
  box-shadow: 0 8px 32px rgba(31, 38, 135, 0.1);
  position: relative;
  overflow: hidden;
}

.glass-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
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

/* 动画效果 */
@keyframes float {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  25% { transform: translateY(-20px) rotate(5deg); }
  50% { transform: translateY(-10px) rotate(-5deg); }
  75% { transform: translateY(-15px) rotate(3deg); }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .hero-content {
    grid-template-columns: 1fr;
    gap: 30px;
    text-align: center;
  }
  
  .hero-text h1 {
    font-size: 2rem;
  }
  
  .hero-features {
    justify-content: center;
    gap: 20px;
  }
  
  .hero-actions {
    justify-content: center;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .status-grid {
    grid-template-columns: repeat(2, 1fr);
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
</style>
