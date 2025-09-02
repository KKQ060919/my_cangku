<template>
  <div class="stock-advisor">
    <!-- 动态背景 -->
    <div class="background-effects">
      <div class="gradient-orb orb-1"></div>
      <div class="gradient-orb orb-2"></div>
      <div class="gradient-orb orb-3"></div>
    </div>

    <!-- 页面头部 -->
    <div class="header">
      <div class="header-content">
        <div class="icon-wrapper">
          <i class="el-icon-data-analysis header-icon"></i>
        </div>
        <h1 class="main-title">智能股票投资顾问</h1>
        <p class="subtitle">基于AI的专业股票分析与投资建议</p>
        <div class="header-divider"></div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 输入表单 -->
      <div class="input-section">
        <el-card class="glass-card input-card" shadow="never">
          <template #header>
            <div class="card-header">
              <i class="el-icon-trend-charts"></i>
              <span>股票分析工作台</span>
            </div>
          </template>
          
          <el-form ref="formRef" :model="form" label-width="100px" class="modern-form">
            <el-form-item label="股票名称" required class="form-item">
              <el-input 
                v-model="form.stockName" 
                placeholder="输入股票名称，如：苹果、特斯拉、茅台"
                clearable
                size="large"
                class="modern-input"
              >
                <template #prefix>
                  <i class="el-icon-search"></i>
                </template>
              </el-input>
            </el-form-item>
            
            <el-form-item label="投资金额" required class="form-item">
              <el-input 
                v-model="form.investmentAmount" 
                placeholder="输入投资金额，如：10000元"
                clearable
                size="large"
                class="modern-input"
              >
                <template #prefix>
                  <i class="el-icon-money"></i>
                </template>
              </el-input>
            </el-form-item>
            
            <el-form-item class="button-group">
              <el-button 
                type="primary" 
                @click="analyzeStock" 
                :loading="loading"
                size="large"
                class="primary-btn"
              >
                <i class="el-icon-data-analysis"></i>
                {{ loading ? '分析中...' : '开始智能分析' }}
              </el-button>
              <el-button 
                @click="clearHistory" 
                size="large"
                class="secondary-btn"
              >
                <i class="el-icon-delete"></i>
                清除记录
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </div>

      <!-- 右侧内容区域 -->
      <div class="content-section">
        <!-- 分析结果 -->
        <el-card v-if="analysisResult" class="glass-card result-card" shadow="never">
          <template #header>
            <div class="card-header result-header">
              <div class="header-left">
                <i class="el-icon-pie-chart"></i>
                <span>分析结果</span>
              </div>
              <div class="timestamp">{{ currentTimestamp }}</div>
            </div>
          </template>
          
          <div class="analysis-content">
            <el-alert 
              title="投资风险提醒" 
              type="warning" 
              description="以下分析仅供参考，投资有风险，入市需谨慎！"
              show-icon
              :closable="false"
              class="risk-alert"
            />
            
            <div class="result-text">
              <div class="result-content">{{ analysisResult }}</div>
            </div>
          </div>
        </el-card>

        <!-- 历史记录 -->
        <el-card class="glass-card history-card" shadow="never">
          <template #header>
            <div class="card-header">
              <div class="header-left">
                <i class="el-icon-chat-line-square"></i>
                <span>对话历史</span>
              </div>
              <el-button @click="loadHistory" size="small" class="refresh-btn">
                <i class="el-icon-refresh"></i>
                刷新
              </el-button>
            </div>
          </template>
          
          <div v-if="chatHistory.length === 0" class="no-history">
            <i class="el-icon-chat-dot-square"></i>
            <p>暂无对话记录</p>
            <span>开始您的第一次股票分析吧！</span>
          </div>
          
          <div v-else class="history-list">
            <div 
              v-for="(chat, index) in chatHistory" 
              :key="index" 
              class="chat-item"
              :class="{ 'fade-in': true }"
              :style="{ 'animation-delay': `${index * 0.1}s` }"
            >
              <div class="chat-time">
                <i class="el-icon-time"></i>
                {{ chat.时间戳 }}
              </div>
              <div class="chat-user">
                <div class="chat-avatar user-avatar">👤</div>
                <div class="chat-content">{{ chat.用户消息 }}</div>
              </div>
              <div class="chat-bot">
                <div class="chat-avatar bot-avatar">🤖</div>
                <div class="chat-content">{{ chat.机器人回复.substring(0, 100) }}...</div>
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

// 响应式数据
const loading = ref(false)
const analysisResult = ref('')
const currentTimestamp = ref('')
const chatHistory = ref([])
const sessionId = ref(localStorage.getItem('sessionId') || generateSessionId())

// 表单数据
const form = reactive({
  stockName: '',
  investmentAmount: ''
})

// 生成会话ID
function generateSessionId() {
  const id = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
  localStorage.setItem('sessionId', id)
  return id
}

// 分析股票
async function analyzeStock() {
  if (!form.stockName || !form.investmentAmount) {
    ElMessage.warning('请填写完整信息')
    return
  }

  loading.value = true
  try {
    const response = await axios.post('http://localhost:8000/Agentswenda/api/analyze/', {
      stock_name: form.stockName,
      investment_amount: form.investmentAmount,
      session_id: sessionId.value
    })

    if (response.data.success) {
      analysisResult.value = response.data.analysis
      currentTimestamp.value = response.data.timestamp
      ElMessage.success('分析完成')
      
      // 自动加载历史记录
      setTimeout(loadHistory, 1000)
    } else {
      ElMessage.error(response.data.error || '分析失败')
    }
  } catch (error) {
    console.error('分析错误:', error)
    ElMessage.error('网络错误，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 加载历史记录
async function loadHistory() {
  try {
    const response = await axios.get(`http://localhost:8000/Agentswenda/api/history/?session_id=${sessionId.value}`)
    
    if (response.data.success) {
      chatHistory.value = response.data.history
    }
  } catch (error) {
    console.error('加载历史失败:', error)
  }
}

// 清除记录
function clearHistory() {
  chatHistory.value = []
  analysisResult.value = ''
  currentTimestamp.value = ''
  sessionId.value = generateSessionId()
  ElMessage.success('记录已清除')
}

// 组件挂载时加载历史
onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
/* 全局变量定义 */
:root {
  --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  --success-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  --glass-bg: rgba(255, 255, 255, 0.1);
  --glass-border: rgba(255, 255, 255, 0.2);
  --text-primary: #2c3e50;
  --text-secondary: #7f8c8d;
  --shadow-light: 0 8px 32px rgba(31, 38, 135, 0.1);
  --shadow-medium: 0 15px 35px rgba(31, 38, 135, 0.2);
  --shadow-heavy: 0 20px 40px rgba(31, 38, 135, 0.3);
}

/* 主容器 */
.stock-advisor {
  position: relative;
  min-height: 100vh;
  padding: 40px 20px;
  background: linear-gradient(135deg, 
    #667eea 0%, 
    #764ba2 25%, 
    #f093fb 50%, 
    #f5576c 75%, 
    #4facfe 100%);
  background-size: 400% 400%;
  animation: gradientShift 15s ease infinite;
  overflow-x: hidden;
}

/* 动态背景效果 */
.background-effects {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.gradient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(40px);
  opacity: 0.7;
  animation: float 20s infinite ease-in-out;
}

.orb-1 {
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(102, 126, 234, 0.4) 0%, transparent 70%);
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.orb-2 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(245, 87, 108, 0.3) 0%, transparent 70%);
  top: 50%;
  right: 10%;
  animation-delay: 7s;
}

.orb-3 {
  width: 250px;
  height: 250px;
  background: radial-gradient(circle, rgba(79, 172, 254, 0.4) 0%, transparent 70%);
  bottom: 20%;
  left: 50%;
  animation-delay: 14s;
}

/* 页面头部 */
.header {
  position: relative;
  z-index: 1;
  text-align: center;
  margin-bottom: 50px;
  padding: 40px 0;
}

.header-content {
  backdrop-filter: blur(20px);
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  padding: 40px;
  box-shadow: var(--shadow-medium);
  max-width: 600px;
  margin: 0 auto;
  animation: slideInUp 0.8s ease-out;
}

.icon-wrapper {
  margin-bottom: 20px;
}

.header-icon {
  font-size: 4rem;
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: pulse 2s infinite;
}

.main-title {
  font-size: 2.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 20px 0;
  letter-spacing: -0.02em;
}

.subtitle {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
  font-weight: 300;
}

.header-divider {
  width: 60px;
  height: 4px;
  background: var(--success-gradient);
  margin: 30px auto 0;
  border-radius: 2px;
  animation: slideInLeft 1s ease-out 0.5s both;
}

/* 主要内容区域 */
.main-content {
  position: relative;
  z-index: 1;
  max-width: 1400px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 450px 1fr;
  gap: 40px;
  align-items: start;
}

.input-section, .content-section {
  animation: slideInUp 0.8s ease-out;
}

.content-section {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

/* 玻璃态卡片 */
.glass-card {
  backdrop-filter: blur(20px);
  background: var(--glass-bg) !important;
  border: 1px solid var(--glass-border) !important;
  border-radius: 20px !important;
  box-shadow: var(--shadow-medium);
  transition: all 0.3s ease;
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

.glass-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-heavy);
  border-color: rgba(255, 255, 255, 0.3);
}

/* 卡片头部 */
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: white;
  font-weight: 600;
  font-size: 1.1rem;
}

.card-header i {
  margin-right: 10px;
  font-size: 1.2rem;
  color: #4facfe;
}

.header-left {
  display: flex;
  align-items: center;
}

/* 表单样式 */
.modern-form {
  padding: 20px 0;
}

.form-item {
  margin-bottom: 25px;
}

.modern-input {
  border-radius: 12px;
  width: 100%;
}

/* Element Plus Input 样式覆盖 */
.modern-input :deep(.el-input) {
  --el-input-bg-color: rgba(255, 255, 255, 0.1);
  --el-input-border-color: rgba(255, 255, 255, 0.2);
  --el-input-hover-border-color: rgba(255, 255, 255, 0.3);
  --el-input-focus-border-color: #4facfe;
  --el-input-text-color: white;
  --el-input-placeholder-color: rgba(255, 255, 255, 0.6);
}

.modern-input :deep(.el-input__wrapper) {
  background-color: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  box-shadow: none;
  transition: all 0.3s ease;
}

.modern-input :deep(.el-input__wrapper:hover) {
  border-color: rgba(255, 255, 255, 0.3);
  box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.1);
}

.modern-input :deep(.el-input__wrapper.is-focus) {
  border-color: #4facfe;
  box-shadow: 0 0 0 2px rgba(79, 172, 254, 0.2);
}

.modern-input :deep(.el-input__inner) {
  color: white;
  font-size: 16px;
  padding: 12px 16px;
  background: transparent;
  border: none;
  outline: none;
}

.modern-input :deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.6);
}

.modern-input :deep(.el-input__prefix) {
  color: #4facfe;
}

.modern-input :deep(.el-input__prefix-inner) {
  color: #4facfe;
}

/* 确保输入框在所有状态下都正确显示 */
.modern-input :deep(.el-input__wrapper.is-disabled) {
  background-color: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.1);
}

.modern-input :deep(.el-input__inner:disabled) {
  color: rgba(255, 255, 255, 0.4);
}

/* 修复可能的显示问题 */
.modern-input :deep(.el-input__wrapper) {
  min-height: 48px;
  line-height: 1.2;
}

.modern-input :deep(.el-input__inner) {
  line-height: 1.2;
  height: auto;
}

/* 按钮样式 */
.button-group {
  display: flex;
  gap: 15px;
  margin-top: 30px;
}

.primary-btn {
  background: var(--success-gradient) !important;
  border: none !important;
  border-radius: 12px !important;
  padding: 12px 30px !important;
  font-weight: 600 !important;
  font-size: 16px !important;
  transition: all 0.3s ease !important;
  box-shadow: 0 4px 15px rgba(79, 172, 254, 0.3) !important;
}

.primary-btn:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 25px rgba(79, 172, 254, 0.4) !important;
}

.secondary-btn {
  background: rgba(255, 255, 255, 0.1) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  color: white !important;
  border-radius: 12px !important;
  padding: 12px 24px !important;
  font-weight: 500 !important;
  transition: all 0.3s ease !important;
}

.secondary-btn:hover {
  background: rgba(255, 255, 255, 0.2) !important;
  transform: translateY(-2px) !important;
}

.refresh-btn {
  background: rgba(255, 255, 255, 0.1) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  color: white !important;
  border-radius: 8px !important;
}

/* 时间戳 */
.timestamp {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.85rem;
  font-weight: 400;
}

/* 分析内容 */
.analysis-content {
  padding: 20px 0;
}

.risk-alert {
  margin-bottom: 20px;
  border-radius: 12px;
}

.result-text {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 25px;
  margin-top: 20px;
}

.result-content {
  color: white;
  line-height: 1.8;
  font-size: 15px;
  white-space: pre-wrap;
  font-family: 'SF Pro Text', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* 历史记录 */
.history-card {
  max-height: 600px;
  overflow: hidden;
}

.history-card :deep(.el-card__body) {
  max-height: 500px;
  overflow-y: auto;
  padding: 20px;
}

.no-history {
  text-align: center;
  padding: 60px 20px;
  color: rgba(255, 255, 255, 0.6);
}

.no-history i {
  font-size: 3rem;
  margin-bottom: 20px;
  color: #4facfe;
  display: block;
}

.no-history p {
  font-size: 1.1rem;
  margin: 10px 0;
  color: white;
}

.no-history span {
  font-size: 0.9rem;
  opacity: 0.8;
}

/* 聊天项目 */
.chat-item {
  padding: 20px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  animation: fadeIn 0.5s ease-out;
}

.chat-item:last-child {
  border-bottom: none;
}

.chat-time {
  display: flex;
  align-items: center;
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.85rem;
  margin-bottom: 12px;
}

.chat-time i {
  margin-right: 6px;
}

.chat-user, .chat-bot {
  display: flex;
  align-items: flex-start;
  margin-bottom: 15px;
  gap: 12px;
}

.chat-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  flex-shrink: 0;
}

.user-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.bot-avatar {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.chat-content {
  flex: 1;
  padding: 12px 16px;
  border-radius: 12px;
  line-height: 1.5;
}

.chat-user .chat-content {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-weight: 500;
}

.chat-bot .chat-content {
  background: rgba(79, 172, 254, 0.1);
  color: #e3f2fd;
  border: 1px solid rgba(79, 172, 254, 0.2);
}

/* 动画效果 */
@keyframes gradientShift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

@keyframes float {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  33% { transform: translateY(-30px) rotate(120deg); }
  66% { transform: translateY(15px) rotate(240deg); }
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.fade-in {
  animation: fadeIn 0.6s ease-out;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .main-content {
    grid-template-columns: 400px 1fr;
    gap: 30px;
  }
}

@media (max-width: 992px) {
  .main-content {
    grid-template-columns: 1fr;
    gap: 30px;
  }
  
  .header-content {
    padding: 30px 20px;
  }
  
  .main-title {
    font-size: 2rem;
  }
}

@media (max-width: 768px) {
  .stock-advisor {
    padding: 20px 15px;
  }
  
  .main-title {
    font-size: 1.8rem;
  }
  
  .button-group {
    flex-direction: column;
    gap: 10px;
  }
  
  .button-group .el-button {
    width: 100%;
  }
  
  .card-header {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
}

@media (max-width: 480px) {
  .header-content {
    padding: 25px 15px;
  }
  
  .main-title {
    font-size: 1.5rem;
  }
  
  .subtitle {
    font-size: 1rem;
  }
  
  .glass-card {
    border-radius: 15px !important;
  }
}

/* Element Plus 组件样式覆盖 */
:deep(.el-form-item__label) {
  color: white !important;
  font-weight: 500 !important;
}

:deep(.el-alert) {
  border-radius: 12px !important;
  background: rgba(245, 108, 108, 0.1) !important;
  border: 1px solid rgba(245, 108, 108, 0.2) !important;
}

:deep(.el-alert__title) {
  color: #f56c6c !important;
  font-weight: 600 !important;
}

:deep(.el-alert__description) {
  color: rgba(245, 108, 108, 0.8) !important;
}

:deep(.el-card__header) {
  background: transparent !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
  padding: 20px 25px !important;
}

:deep(.el-card__body) {
  padding: 25px !important;
}

/* 滚动条样式 */
:deep(*::-webkit-scrollbar) {
  width: 6px;
}

:deep(*::-webkit-scrollbar-track) {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

:deep(*::-webkit-scrollbar-thumb) {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
}

:deep(*::-webkit-scrollbar-thumb:hover) {
  background: rgba(255, 255, 255, 0.5);
}
</style>
