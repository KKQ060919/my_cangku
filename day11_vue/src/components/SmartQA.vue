<template>
  <div class="smart-qa">
    <!-- 页面标题 -->
    <div class="page-header">
      <el-card class="glass-card header-card" shadow="never">
        <div class="header-content">
          <div class="header-left">
            <i class="el-icon-chat-dot-round"></i>
            <div>
              <h1>智能商品问答</h1>
              <p>基于RAG技术的商品咨询和知识问答系统</p>
            </div>
          </div>
          <div class="header-right">
            <el-tag type="success" size="large">RAG引擎: 已启动</el-tag>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 对话区域 -->
    <div class="chat-container">
      <el-card class="glass-card chat-card" shadow="never">
        <!-- 对话历史 -->
        <div class="chat-messages" ref="messagesContainer">
          <div v-if="messages.length === 0" class="welcome-message">
            <div class="welcome-content">
              <i class="el-icon-chat-dot-round"></i>
              <h3>欢迎使用智能问答助手</h3>
              <p>您可以询问关于商品的任何问题，我会基于商品数据库为您提供准确答案</p>
              <div class="suggested-questions">
                <h4>建议问题:</h4>
                <div class="suggestion-buttons">
                  <el-button 
                    v-for="suggestion in suggestedQuestions" 
                    :key="suggestion"
                    type="text" 
                    @click="askQuestion(suggestion)"
                    class="suggestion-btn"
                  >
                    {{ suggestion }}
                  </el-button>
                </div>
              </div>
            </div>
          </div>

          <!-- 消息列表 -->
          <div 
            v-for="(message, index) in messages" 
            :key="index" 
            class="message-item"
            :class="{ 'user-message': message.type === 'user', 'bot-message': message.type === 'bot' }"
          >
            <div class="message-avatar">
              <i :class="message.type === 'user' ? 'el-icon-user-solid' : 'el-icon-service'"></i>
            </div>
            <div class="message-content">
              <div class="message-header">
                <span class="message-sender">{{ message.type === 'user' ? '您' : 'AI助手' }}</span>
                <span class="message-time">{{ message.timestamp }}</span>
              </div>
              <div class="message-text" v-html="formatMessage(message.text)"></div>
              
              <!-- 相关商品推荐 -->
              <div v-if="message.related_products && message.related_products.length > 0" class="related-products">
                <h4>相关商品推荐:</h4>
                <div class="products-list">
                  <div 
                    v-for="product in message.related_products" 
                    :key="product.id"
                    class="product-item"
                    @click="viewProduct(product)"
                  >
                    <div class="product-info">
                      <h5>{{ product.name }}</h5>
                      <p class="product-price">¥{{ formatPrice(product.price) }}</p>
                    </div>
                    <div class="product-category">{{ product.category }}</div>
                  </div>
                </div>
              </div>

              <!-- 知识来源 -->
              <div v-if="message.sources && message.sources.length > 0" class="knowledge-sources">
                <h4>信息来源:</h4>
                <div class="sources-list">
                  <el-tag 
                    v-for="source in message.sources" 
                    :key="source"
                    size="small" 
                    type="info"
                    class="source-tag"
                  >
                    {{ source }}
                  </el-tag>
                </div>
              </div>

              <!-- 置信度 -->
              <div v-if="message.confidence" class="confidence-indicator">
                <span>回答置信度: </span>
                <el-progress 
                  :percentage="Math.round(message.confidence * 100)" 
                  :color="getConfidenceColor(message.confidence)"
                  :show-text="false"
                  :stroke-width="6"
                />
                <span class="confidence-text">{{ Math.round(message.confidence * 100) }}%</span>
              </div>

              <!-- 反馈按钮 -->
              <div v-if="message.type === 'bot'" class="message-feedback">
                <el-button-group size="small">
                  <el-button 
                    @click="giveFeedback(message, 'helpful')" 
                    :type="message.feedback === 'helpful' ? 'success' : ''"
                    size="small"
                  >
                    <i class="el-icon-thumb-up"></i>
                    有帮助
                  </el-button>
                  <el-button 
                    @click="giveFeedback(message, 'not_helpful')" 
                    :type="message.feedback === 'not_helpful' ? 'danger' : ''"
                    size="small"
                  >
                    <i class="el-icon-thumb-down"></i>
                    无帮助
                  </el-button>
                </el-button-group>
              </div>
            </div>
          </div>

          <!-- 加载指示器 -->
          <div v-if="isLoading" class="loading-message">
            <div class="message-avatar">
              <i class="el-icon-service"></i>
            </div>
            <div class="message-content">
              <div class="typing-indicator">
                <div class="typing-dots">
                  <div class="dot"></div>
                  <div class="dot"></div>
                  <div class="dot"></div>
                </div>
                <span>AI助手正在思考中...</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 输入区域 -->
        <div class="chat-input-area">
          <div class="input-container">
            <el-input
              v-model="currentQuestion"
              type="textarea"
              :autosize="{ minRows: 1, maxRows: 4 }"
              placeholder="请输入您想了解的商品问题..."
              @keydown.enter.prevent="handleEnterKey"
              ref="questionInput"
              class="question-input"
            />
            <div class="input-actions">
              <el-button-group>
                <el-button @click="clearChat" size="small">
                  <i class="el-icon-delete"></i>
                  清空
                </el-button>
                <el-button @click="exportChat" size="small">
                  <i class="el-icon-download"></i>
                  导出
                </el-button>
                <el-button 
                  type="primary" 
                  @click="sendQuestion" 
                  :loading="isLoading"
                  :disabled="!currentQuestion.trim()"
                  size="small"
                >
                  <i class="el-icon-position"></i>
                  发送
                </el-button>
              </el-button-group>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 侧边栏统计 -->
    <div class="sidebar-stats">
      <el-card class="glass-card stats-card" shadow="never">
        <template #header>
          <div class="card-header">
            <i class="el-icon-pie-chart"></i>
            <span>对话统计</span>
            <el-button @click="loadStats" size="small" class="refresh-btn">
              <i class="el-icon-refresh"></i>
            </el-button>
          </div>
        </template>

        <div class="stats-list">
          <div class="stat-item">
            <div class="stat-label">本次对话</div>
            <div class="stat-value">{{ messages.filter(m => m.type === 'user').length }}</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">今日问答</div>
            <div class="stat-value">{{ stats.today_questions || 0 }}</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">知识库文档</div>
            <div class="stat-value">{{ stats.knowledge_docs || 0 }}</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">平均响应时间</div>
            <div class="stat-value">{{ stats.avg_response_time || 0 }}ms</div>
          </div>
        </div>
      </el-card>

      <!-- 热门问题 -->
      <el-card class="glass-card popular-questions-card" shadow="never">
        <template #header>
          <div class="card-header">
            <i class="el-icon-star-on"></i>
            <span>热门问题</span>
          </div>
        </template>

        <div class="popular-questions">
          <div 
            v-for="(question, index) in popularQuestions" 
            :key="index"
            class="popular-question-item"
            @click="askQuestion(question.text)"
          >
            <div class="question-rank">{{ index + 1 }}</div>
            <div class="question-content">
              <div class="question-text">{{ question.text }}</div>
              <div class="question-count">{{ question.count }} 次询问</div>
            </div>
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
        </div>
        <div class="product-full-description" v-if="selectedProduct.description">
          <strong>商品描述:</strong>
          <p>{{ selectedProduct.description }}</p>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, nextTick, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

// 响应式数据
const currentQuestion = ref('')
const messages = ref([])
const isLoading = ref(false)
const stats = ref({})
const popularQuestions = ref([])
const productDialogVisible = ref(false)
const selectedProduct = ref(null)
const messagesContainer = ref(null)
const questionInput = ref(null)

// 建议问题
const suggestedQuestions = [
  "推荐一些性价比高的手机",
  "有什么好的笔记本电脑推荐？",
  "运动鞋什么牌子好？",
  "最近有什么热门的图书？",
  "家用电器有哪些优惠？"
]

// 发送问题
const sendQuestion = async () => {
  if (!currentQuestion.value.trim() || isLoading.value) return

  const question = currentQuestion.value.trim()
  
  // 添加用户消息
  messages.value.push({
    type: 'user',
    text: question,
    timestamp: new Date().toLocaleTimeString()
  })

  currentQuestion.value = ''
  isLoading.value = true

  // 滚动到底部
  scrollToBottom()

  try {
    const response = await axios.post('http://localhost:8000/rag/api/ask/', {
      question: question,
      session_id: generateSessionId(),
      include_products: true
    })

    if (response.data.success) {
      // 添加AI回答
      messages.value.push({
        type: 'bot',
        text: response.data.answer,
        timestamp: new Date().toLocaleTimeString(),
        confidence: response.data.confidence,
        sources: response.data.sources || [],
        related_products: response.data.related_products || [],
        response_time: response.data.response_time
      })

      // 更新统计
      loadStats()
    } else {
      throw new Error(response.data.error || '服务器错误')
    }
  } catch (error) {
    console.error('问答请求失败:', error)
    
    // 添加错误消息
    messages.value.push({
      type: 'bot',
      text: '抱歉，我暂时无法回答您的问题。请稍后再试，或者尝试换个方式提问。',
      timestamp: new Date().toLocaleTimeString(),
      confidence: 0,
      error: true
    })

    ElMessage.error('获取答案失败，请稍后重试')
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}

// 处理回车键
const handleEnterKey = (event) => {
  if (!event.shiftKey) {
    event.preventDefault()
    sendQuestion()
  }
}

// 询问建议问题
const askQuestion = (question) => {
  currentQuestion.value = question
  nextTick(() => {
    questionInput.value?.focus()
  })
}

// 清空对话
const clearChat = () => {
  messages.value = []
  ElMessage.success('对话已清空')
}

// 导出对话
const exportChat = () => {
  if (messages.value.length === 0) {
    ElMessage.warning('暂无对话内容可导出')
    return
  }

  const content = messages.value.map(msg => {
    return `[${msg.timestamp}] ${msg.type === 'user' ? '用户' : 'AI助手'}: ${msg.text}`
  }).join('\n\n')

  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `智能问答对话记录_${new Date().toISOString().slice(0, 10)}.txt`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)

  ElMessage.success('对话记录已导出')
}

// 给出反馈
const giveFeedback = async (message, feedbackType) => {
  try {
    await axios.post('http://localhost:8000/rag/api/feedback/', {
      question: messages.value[messages.value.indexOf(message) - 1]?.text || '',
      answer: message.text,
      feedback_type: feedbackType,
      session_id: generateSessionId()
    })

    message.feedback = feedbackType
    ElMessage.success('感谢您的反馈')
  } catch (error) {
    console.error('提交反馈失败:', error)
    ElMessage.error('提交反馈失败')
  }
}

// 查看商品详情
const viewProduct = (product) => {
  selectedProduct.value = product
  productDialogVisible.value = true
}

// 加载统计数据
const loadStats = async () => {
  try {
    const response = await axios.get('http://localhost:8000/rag/api/stats/')
    
    if (response.data.success) {
      stats.value = response.data.stats
    }
  } catch (error) {
    console.error('加载统计失败:', error)
  }
}

// 加载热门问题
const loadPopularQuestions = async () => {
  try {
    const response = await axios.get('http://localhost:8000/rag/api/popular_questions/')
    
    if (response.data.success) {
      popularQuestions.value = response.data.questions
    }
  } catch (error) {
    console.error('加载热门问题失败:', error)
  }
}

// 格式化消息文本
const formatMessage = (text) => {
  // 简单的文本格式化，将换行符转换为<br>
  return text.replace(/\n/g, '<br>')
}

// 格式化价格
const formatPrice = (price) => {
  return parseFloat(price || 0).toFixed(2)
}

// 获取置信度颜色
const getConfidenceColor = (confidence) => {
  if (confidence >= 0.8) return '#67c23a'
  if (confidence >= 0.6) return '#e6a23c'
  return '#f56c6c'
}

// 生成会话ID
const generateSessionId = () => {
  return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// 组件挂载时加载数据
onMounted(() => {
  loadStats()
  loadPopularQuestions()
})
</script>

<style scoped>
.smart-qa {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 30px;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
  height: calc(100vh - 140px);
}

/* 页面标题 */
.page-header {
  grid-column: 1 / -1;
  margin-bottom: 0;
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
  padding: 20px 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.header-left i {
  font-size: 2.5rem;
  color: #4facfe;
}

.header-left h1 {
  color: white;
  font-size: 1.8rem;
  margin: 0 0 8px 0;
  font-weight: 700;
}

.header-left p {
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
  font-size: 1rem;
}

/* 对话容器 */
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.chat-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  backdrop-filter: blur(20px);
  border-radius: 15px !important;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  max-height: calc(100vh - 300px);
}

/* 欢迎消息 */
.welcome-message {
  text-align: center;
  padding: 60px 20px;
}

.welcome-content i {
  font-size: 4rem;
  color: #4facfe;
  margin-bottom: 20px;
}

.welcome-content h3 {
  color: white;
  font-size: 1.5rem;
  margin: 20px 0;
}

.welcome-content p {
  color: rgba(255, 255, 255, 0.7);
  font-size: 1rem;
  margin-bottom: 30px;
}

.suggested-questions h4 {
  color: white;
  font-size: 1.1rem;
  margin-bottom: 15px;
}

.suggestion-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}

.suggestion-btn {
  background: rgba(255, 255, 255, 0.1) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  color: white !important;
  border-radius: 20px !important;
  padding: 8px 16px !important;
  transition: all 0.3s ease;
}

.suggestion-btn:hover {
  background: rgba(255, 255, 255, 0.2) !important;
  border-color: #4facfe !important;
  color: #4facfe !important;
}

/* 消息样式 */
.message-item {
  display: flex;
  margin-bottom: 30px;
  animation: fadeInUp 0.5s ease;
}

.user-message {
  flex-direction: row-reverse;
}

.user-message .message-content {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 15px;
  flex-shrink: 0;
}

.user-message .message-avatar {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.bot-message .message-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.message-avatar i {
  color: white;
  font-size: 1.2rem;
}

.message-content {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 15px;
  padding: 15px 20px;
  max-width: 70%;
  flex: 1;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.message-sender {
  font-weight: 600;
  font-size: 0.9rem;
}

.message-time {
  font-size: 0.8rem;
  opacity: 0.7;
}

.message-text {
  line-height: 1.6;
  word-wrap: break-word;
}

/* 相关商品 */
.related-products {
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.related-products h4 {
  color: #4facfe;
  font-size: 0.9rem;
  margin-bottom: 10px;
}

.products-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.product-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.product-item:hover {
  background: rgba(255, 255, 255, 0.1);
}

.product-info h5 {
  margin: 0 0 5px 0;
  font-size: 0.9rem;
}

.product-price {
  color: #4facfe;
  font-weight: 600;
  margin: 0;
}

.product-category {
  background: rgba(255, 255, 255, 0.1);
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
}

/* 知识来源 */
.knowledge-sources {
  margin-top: 15px;
}

.knowledge-sources h4 {
  color: #4facfe;
  font-size: 0.9rem;
  margin-bottom: 8px;
}

.sources-list {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.source-tag {
  font-size: 0.8rem;
}

/* 置信度指示器 */
.confidence-indicator {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 15px;
  font-size: 0.9rem;
}

.confidence-indicator .el-progress {
  flex: 1;
  max-width: 100px;
}

.confidence-text {
  font-weight: 600;
  min-width: 35px;
}

/* 消息反馈 */
.message-feedback {
  margin-top: 15px;
  padding-top: 10px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

/* 加载指示器 */
.loading-message {
  display: flex;
  margin-bottom: 30px;
}

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 15px;
  color: rgba(255, 255, 255, 0.7);
}

.typing-dots {
  display: flex;
  gap: 4px;
}

.dot {
  width: 8px;
  height: 8px;
  background: #4facfe;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out both;
}

.dot:nth-child(1) { animation-delay: -0.32s; }
.dot:nth-child(2) { animation-delay: -0.16s; }

/* 输入区域 */
.chat-input-area {
  padding: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.input-container {
  display: flex;
  gap: 15px;
  align-items: flex-end;
}

.question-input {
  flex: 1;
}

.question-input :deep(.el-textarea__inner) {
  background: rgba(255, 255, 255, 0.1) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  color: white !important;
  border-radius: 10px !important;
  resize: none !important;
}

.question-input :deep(.el-textarea__inner):focus {
  border-color: #4facfe !important;
  box-shadow: 0 0 0 2px rgba(79, 172, 254, 0.2) !important;
}

.question-input :deep(.el-textarea__inner)::placeholder {
  color: rgba(255, 255, 255, 0.6) !important;
}

/* 侧边栏 */
.sidebar-stats {
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: fit-content;
}

.stats-card,
.popular-questions-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  backdrop-filter: blur(20px);
  border-radius: 15px !important;
}

.stats-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-label {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}

.stat-value {
  color: #4facfe;
  font-weight: 600;
  font-size: 1.1rem;
}

/* 热门问题 */
.popular-questions {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.popular-question-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.popular-question-item:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateX(5px);
}

.question-rank {
  width: 24px;
  height: 24px;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 0.8rem;
  flex-shrink: 0;
}

.question-content {
  flex: 1;
}

.question-text {
  color: white;
  font-size: 0.9rem;
  line-height: 1.4;
  margin-bottom: 4px;
}

.question-count {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.8rem;
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

.product-full-description {
  margin-top: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.product-full-description strong {
  color: #495057;
  display: block;
  margin-bottom: 10px;
}

/* 公共样式 */
.glass-card {
  backdrop-filter: blur(20px);
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

/* 动画效果 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .smart-qa {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr;
    height: auto;
  }
  
  .sidebar-stats {
    order: -1;
  }
  
  .chat-messages {
    max-height: 400px;
  }
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .message-content {
    max-width: 85%;
  }
  
  .input-container {
    flex-direction: column;
    gap: 10px;
  }
  
  .input-actions {
    width: 100%;
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

:deep(.el-progress-bar__outer) {
  background: rgba(255, 255, 255, 0.2) !important;
}

:deep(.el-button-group .el-button) {
  border-color: rgba(255, 255, 255, 0.2) !important;
}
</style>
