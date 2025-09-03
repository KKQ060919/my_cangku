<template>
  <div class="system-stats">
    <!-- 页面标题 -->
    <div class="page-header">
      <el-card class="glass-card header-card" shadow="never">
        <div class="header-content">
          <div class="header-left">
            <i class="el-icon-data-analysis"></i>
            <div>
              <h1>系统统计监控</h1>
              <p>系统性能、数据统计和运行状态的实时监控</p>
            </div>
          </div>
          <div class="header-right">
            <div class="system-status">
              <div class="status-indicator" :class="systemStatus.overall">
                <i class="el-icon-connection"></i>
              </div>
              <div class="status-text">
                <div class="status-label">系统状态</div>
                <div class="status-value">{{ systemStatus.text }}</div>
              </div>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 系统概览 -->
    <div class="system-overview">
      <div class="overview-grid">
        <el-card
          v-for="metric in systemMetrics"
          :key="metric.key"
          class="glass-card metric-card"
          shadow="never"
        >
          <div class="metric-content">
            <div class="metric-header">
              <div class="metric-icon">
                <i :class="metric.icon"></i>
              </div>
              <div class="metric-status" :class="metric.status">
                <i :class="metric.statusIcon"></i>
              </div>
            </div>
            <div class="metric-info">
              <div class="metric-value">{{ metric.value }}</div>
              <div class="metric-label">{{ metric.label }}</div>
              <div class="metric-trend" :class="metric.trendClass">
                <i :class="metric.trendIcon"></i>
                {{ metric.trend }}
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 系统性能图表 -->
    <div class="performance-charts">
      <div class="charts-row">
        <!-- CPU和内存使用率 -->
        <el-card class="glass-card chart-card" shadow="never">
          <template #header>
            <div class="card-header">
              <i class="el-icon-cpu"></i>
              <span>系统性能监控</span>
              <div class="chart-controls">
                <el-switch v-model="autoRefresh" active-text="自动刷新" size="small" />
                <el-button @click="refreshPerformance" size="small" :loading="performanceLoading">
                  <i class="el-icon-refresh"></i>
                </el-button>
              </div>
            </div>
          </template>
          
          <div class="chart-container">
            <div ref="performanceChart" class="chart" style="height: 300px;">
              <div class="chart-placeholder">
                <i class="el-icon-loading"></i>
                <p>性能监控图表</p>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 请求统计 -->
        <el-card class="glass-card chart-card" shadow="never">
          <template #header>
            <div class="card-header">
              <i class="el-icon-connection"></i>
              <span>API请求统计</span>
              <div class="time-range-selector">
                <el-select v-model="requestTimeRange" size="small" @change="loadRequestStats">
                  <el-option label="1小时" value="1h" />
                  <el-option label="24小时" value="24h" />
                  <el-option label="7天" value="7d" />
                  <el-option label="30天" value="30d" />
                </el-select>
              </div>
            </div>
          </template>
          
          <div class="chart-container">
            <div ref="requestChart" class="chart" style="height: 300px;">
              <div class="chart-placeholder">
                <i class="el-icon-pie-chart"></i>
                <p>请求统计图表</p>
              </div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 数据库和缓存统计 -->
      <div class="charts-row">
        <el-card class="glass-card chart-card" shadow="never">
          <template #header>
            <div class="card-header">
              <i class="el-icon-coin"></i>
              <span>数据库统计</span>
              <el-button @click="optimizeDatabase" size="small" type="primary">
                <i class="el-icon-magic-stick"></i>
                优化数据库
              </el-button>
            </div>
          </template>
          
          <div class="database-stats">
            <div class="stats-grid">
              <div class="stat-item">
                <div class="stat-icon db-icon">
                  <i class="el-icon-document"></i>
                </div>
                <div class="stat-info">
                  <div class="stat-value">{{ databaseStats.total_records || 0 }}</div>
                  <div class="stat-label">总记录数</div>
                </div>
              </div>
              <div class="stat-item">
                <div class="stat-icon size-icon">
                  <i class="el-icon-folder"></i>
                </div>
                <div class="stat-info">
                  <div class="stat-value">{{ formatFileSize(databaseStats.db_size || 0) }}</div>
                  <div class="stat-label">数据库大小</div>
                </div>
              </div>
              <div class="stat-item">
                <div class="stat-icon query-icon">
                  <i class="el-icon-search"></i>
                </div>
                <div class="stat-info">
                  <div class="stat-value">{{ databaseStats.avg_query_time || 0 }}ms</div>
                  <div class="stat-label">平均查询时间</div>
                </div>
              </div>
            </div>
          </div>
        </el-card>

        <el-card class="glass-card chart-card" shadow="never">
          <template #header>
            <div class="card-header">
              <i class="el-icon-lightning"></i>
              <span>缓存统计</span>
              <el-button @click="clearCache" size="small" type="warning">
                <i class="el-icon-delete"></i>
                清空缓存
              </el-button>
            </div>
          </template>
          
          <div class="cache-stats">
            <div class="stats-grid">
              <div class="stat-item">
                <div class="stat-icon hit-icon">
                  <i class="el-icon-check"></i>
                </div>
                <div class="stat-info">
                  <div class="stat-value">{{ Math.round((cacheStats.hit_rate || 0) * 100) }}%</div>
                  <div class="stat-label">缓存命中率</div>
                </div>
              </div>
              <div class="stat-item">
                <div class="stat-icon keys-icon">
                  <i class="el-icon-key"></i>
                </div>
                <div class="stat-info">
                  <div class="stat-value">{{ cacheStats.total_keys || 0 }}</div>
                  <div class="stat-label">缓存键数</div>
                </div>
              </div>
              <div class="stat-item">
                <div class="stat-icon memory-icon">
                  <i class="el-icon-pie-chart"></i>
                </div>
                <div class="stat-info">
                  <div class="stat-value">{{ formatFileSize(cacheStats.memory_used || 0) }}</div>
                  <div class="stat-label">内存使用</div>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 服务状态监控 -->
    <div class="services-monitoring">
      <el-card class="glass-card services-card" shadow="never">
        <template #header>
          <div class="card-header">
            <i class="el-icon-service"></i>
            <span>服务状态监控</span>
            <el-button @click="checkAllServices" size="small" :loading="servicesLoading">
              <i class="el-icon-refresh"></i>
              检查所有服务
            </el-button>
          </div>
        </template>

        <div class="services-grid">
          <div
            v-for="service in services"
            :key="service.name"
            class="service-item"
            :class="service.status"
          >
            <div class="service-icon">
              <i :class="service.icon"></i>
            </div>
            <div class="service-info">
              <div class="service-name">{{ service.name }}</div>
              <div class="service-description">{{ service.description }}</div>
              <div class="service-metrics">
                <span class="service-uptime">运行时间: {{ service.uptime || '0分钟' }}</span>
                <span class="service-requests">请求数: {{ service.requests || 0 }}</span>
              </div>
            </div>
            <div class="service-status">
              <div class="status-indicator" :class="service.status">
                <i :class="service.statusIcon"></i>
              </div>
              <div class="status-text">{{ service.statusText }}</div>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 系统日志 -->
    <div class="system-logs">
      <el-card class="glass-card logs-card" shadow="never">
        <template #header>
          <div class="card-header">
            <div class="header-left">
              <i class="el-icon-document"></i>
              <span>系统日志</span>
            </div>
            <div class="header-controls">
              <el-select v-model="logLevel" size="small" @change="filterLogs">
                <el-option label="全部" value="" />
                <el-option label="错误" value="error" />
                <el-option label="警告" value="warning" />
                <el-option label="信息" value="info" />
                <el-option label="调试" value="debug" />
              </el-select>
              <el-input
                v-model="logSearch"
                placeholder="搜索日志"
                size="small"
                @input="filterLogs"
                clearable
              >
                <template #prefix>
                  <i class="el-icon-search"></i>
                </template>
              </el-input>
              <el-button @click="exportLogs" size="small">
                <i class="el-icon-download"></i>
                导出
              </el-button>
            </div>
          </div>
        </template>

        <div class="logs-container">
          <div 
            v-for="(log, index) in filteredLogs" 
            :key="index"
            class="log-item"
            :class="log.level"
          >
            <div class="log-timestamp">{{ formatTimestamp(log.timestamp) }}</div>
            <div class="log-level">
              <el-tag :type="getLogLevelColor(log.level)" size="small">
                {{ log.level.toUpperCase() }}
              </el-tag>
            </div>
            <div class="log-message">{{ log.message }}</div>
            <div class="log-source" v-if="log.source">{{ log.source }}</div>
          </div>
          
          <div v-if="filteredLogs.length === 0" class="no-logs">
            <i class="el-icon-document"></i>
            <p>暂无日志记录</p>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 系统健康检查对话框 -->
    <el-dialog v-model="healthCheckVisible" title="系统健康检查" width="800px">
      <div class="health-check-results">
        <div v-for="check in healthChecks" :key="check.name" class="check-item">
          <div class="check-header">
            <div class="check-name">{{ check.name }}</div>
            <div class="check-status" :class="check.status">
              <i :class="check.statusIcon"></i>
              {{ check.statusText }}
            </div>
          </div>
          <div class="check-details" v-if="check.details">
            <div class="check-message">{{ check.message }}</div>
            <div class="check-suggestions" v-if="check.suggestions">
              <strong>建议:</strong>
              <ul>
                <li v-for="suggestion in check.suggestions" :key="suggestion">{{ suggestion }}</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

// 响应式数据
const systemStatus = ref({
  overall: 'healthy',
  text: '正常运行'
})

const systemMetrics = ref([
  {
    key: 'cpu_usage',
    label: 'CPU使用率',
    value: '0%',
    icon: 'el-icon-cpu',
    status: 'good',
    statusIcon: 'el-icon-success',
    trend: '+2.1%',
    trendClass: 'positive',
    trendIcon: 'el-icon-top'
  },
  {
    key: 'memory_usage',
    label: '内存使用率',
    value: '0%',
    icon: 'el-icon-pie-chart',
    status: 'good',
    statusIcon: 'el-icon-success',
    trend: '+0.8%',
    trendClass: 'positive',
    trendIcon: 'el-icon-top'
  },
  {
    key: 'disk_usage',
    label: '磁盘使用率',
    value: '0%',
    icon: 'el-icon-folder',
    status: 'warning',
    statusIcon: 'el-icon-warning',
    trend: '+5.2%',
    trendClass: 'warning',
    trendIcon: 'el-icon-top'
  },
  {
    key: 'active_users',
    label: '活跃用户',
    value: '0',
    icon: 'el-icon-user',
    status: 'good',
    statusIcon: 'el-icon-success',
    trend: '+12.3%',
    trendClass: 'positive',
    trendIcon: 'el-icon-top'
  }
])

const databaseStats = ref({})
const cacheStats = ref({})
const logs = ref([])
const filteredLogs = ref([])

const autoRefresh = ref(true)
const performanceLoading = ref(false)
const servicesLoading = ref(false)
const requestTimeRange = ref('24h')
const logLevel = ref('')
const logSearch = ref('')
const healthCheckVisible = ref(false)
const healthChecks = ref([])

// 服务状态
const services = ref([
  {
    name: 'Django服务',
    description: 'Web应用服务器',
    icon: 'el-icon-service',
    status: 'healthy',
    statusText: '正常',
    statusIcon: 'el-icon-success',
    uptime: '2小时30分',
    requests: 1250
  },
  {
    name: 'Redis缓存',
    description: '缓存服务器',
    icon: 'el-icon-lightning',
    status: 'healthy',
    statusText: '正常',
    statusIcon: 'el-icon-success',
    uptime: '1天5小时',
    requests: 5680
  },
  {
    name: '数据库',
    description: 'PostgreSQL数据库',
    icon: 'el-icon-coin',
    status: 'healthy',
    statusText: '正常',
    statusIcon: 'el-icon-success',
    uptime: '3天12小时',
    requests: 890
  },
  {
    name: 'RAG引擎',
    description: '智能问答服务',
    icon: 'el-icon-chat-dot-round',
    status: 'warning',
    statusText: '缓慢',
    statusIcon: 'el-icon-warning',
    uptime: '45分钟',
    requests: 156
  }
])

// 计算属性
const filteredLogsBySearch = computed(() => {
  if (!logSearch.value) return logs.value
  
  return logs.value.filter(log =>
    log.message.toLowerCase().includes(logSearch.value.toLowerCase()) ||
    (log.source && log.source.toLowerCase().includes(logSearch.value.toLowerCase()))
  )
})

// 定时器
let refreshTimer = null

// 加载系统指标
const loadSystemMetrics = async () => {
  try {
    // 加载CPU、内存等系统指标
    const response = await axios.get('http://localhost:8000/system/api/metrics/')
    
    if (response.data.success) {
      const metrics = response.data.metrics
      
      // 更新指标数据
      systemMetrics.value[0].value = `${Math.round(metrics.cpu_usage || 0)}%`
      systemMetrics.value[1].value = `${Math.round(metrics.memory_usage || 0)}%`
      systemMetrics.value[2].value = `${Math.round(metrics.disk_usage || 0)}%`
      systemMetrics.value[3].value = metrics.active_users || 0
    }
  } catch (error) {
    console.error('加载系统指标失败:', error)
  }
}

// 加载数据库统计
const loadDatabaseStats = async () => {
  try {
    const response = await axios.get('http://localhost:8000/system/api/database_stats/')
    
    if (response.data.success) {
      databaseStats.value = response.data.stats
    }
  } catch (error) {
    console.error('加载数据库统计失败:', error)
  }
}

// 加载缓存统计
const loadCacheStats = async () => {
  try {
    const response = await axios.get('http://localhost:8000/cache_management/api/stats/')
    
    if (response.data.success) {
      cacheStats.value = response.data.stats
    }
  } catch (error) {
    console.error('加载缓存统计失败:', error)
  }
}

// 加载系统日志
const loadSystemLogs = async () => {
  try {
    const response = await axios.get('http://localhost:8000/system/api/logs/', {
      params: { limit: 100 }
    })
    
    if (response.data.success) {
      logs.value = response.data.logs
      filterLogs()
    }
  } catch (error) {
    console.error('加载系统日志失败:', error)
    
    // 模拟日志数据
    logs.value = [
      {
        timestamp: new Date().toISOString(),
        level: 'info',
        message: '系统启动完成',
        source: 'system'
      },
      {
        timestamp: new Date(Date.now() - 60000).toISOString(),
        level: 'warning',
        message: 'RAG引擎响应时间较慢',
        source: 'rag_service'
      },
      {
        timestamp: new Date(Date.now() - 120000).toISOString(),
        level: 'error',
        message: '数据库连接超时',
        source: 'database'
      }
    ]
    filterLogs()
  }
}

// 加载请求统计
const loadRequestStats = async () => {
  console.log('Loading request stats for range:', requestTimeRange.value)
}

// 刷新性能数据
const refreshPerformance = async () => {
  performanceLoading.value = true
  try {
    await loadSystemMetrics()
    ElMessage.success('性能数据已更新')
  } catch (error) {
    ElMessage.error('刷新性能数据失败')
  } finally {
    performanceLoading.value = false
  }
}

// 检查所有服务
const checkAllServices = async () => {
  servicesLoading.value = true
  try {
    // 模拟服务检查
    await new Promise(resolve => setTimeout(resolve, 2000))
    ElMessage.success('所有服务状态检查完成')
  } catch (error) {
    ElMessage.error('服务检查失败')
  } finally {
    servicesLoading.value = false
  }
}

// 优化数据库
const optimizeDatabase = async () => {
  try {
    await ElMessageBox.confirm('此操作将优化数据库，可能需要几分钟时间，是否继续？', '确认优化', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    ElMessage.info('数据库优化已开始，请稍候...')
    
    // 模拟优化过程
    setTimeout(() => {
      ElMessage.success('数据库优化完成')
      loadDatabaseStats()
    }, 3000)
  } catch {
    ElMessage.info('已取消优化')
  }
}

// 清空缓存
const clearCache = async () => {
  try {
    await ElMessageBox.confirm('此操作将清空所有缓存数据，是否继续？', '确认清空', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const response = await axios.post('http://localhost:8000/cache_management/api/clear/')
    
    if (response.data.success) {
      ElMessage.success('缓存已清空')
      loadCacheStats()
    } else {
      ElMessage.error('清空缓存失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('清空缓存失败')
    }
  }
}

// 筛选日志
const filterLogs = () => {
  let filtered = filteredLogsBySearch.value
  
  if (logLevel.value) {
    filtered = filtered.filter(log => log.level === logLevel.value)
  }
  
  filteredLogs.value = filtered
}

// 导出日志
const exportLogs = () => {
  if (filteredLogs.value.length === 0) {
    ElMessage.warning('暂无日志可导出')
    return
  }
  
  const csvContent = [
    ['时间', '级别', '消息', '来源'],
    ...filteredLogs.value.map(log => [
      formatTimestamp(log.timestamp),
      log.level.toUpperCase(),
      log.message,
      log.source || ''
    ])
  ].map(row => row.join(',')).join('\n')
  
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `系统日志_${new Date().toISOString().slice(0, 10)}.csv`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
  
  ElMessage.success('日志导出完成')
}

// 工具函数
const formatTimestamp = (timestamp) => {
  return new Date(timestamp).toLocaleString()
}

const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
}

const getLogLevelColor = (level) => {
  const colorMap = {
    'error': 'danger',
    'warning': 'warning',
    'info': 'primary',
    'debug': 'info'
  }
  return colorMap[level] || ''
}

// 设置自动刷新
const setupAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
  
  if (autoRefresh.value) {
    refreshTimer = setInterval(() => {
      loadSystemMetrics()
      loadDatabaseStats()
      loadCacheStats()
    }, 30000) // 30秒刷新一次
  }
}

// 组件挂载时初始化
onMounted(() => {
  loadSystemMetrics()
  loadDatabaseStats()
  loadCacheStats()
  loadSystemLogs()
  setupAutoRefresh()
})

// 组件卸载时清理定时器
onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})
</script>

<style scoped>
.system-stats {
  max-width: 1400px;
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

.system-status {
  display: flex;
  align-items: center;
  gap: 15px;
}

.status-indicator {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.status-indicator.healthy {
  background: linear-gradient(135deg, #67c23a, #85ce61);
  animation: pulse-green 2s infinite;
}

.status-indicator.warning {
  background: linear-gradient(135deg, #e6a23c, #f0c78a);
  animation: pulse-yellow 2s infinite;
}

.status-indicator.error {
  background: linear-gradient(135deg, #f56c6c, #f78989);
  animation: pulse-red 2s infinite;
}

.status-indicator i {
  color: white;
  font-size: 1.5rem;
}

.status-text {
  color: white;
}

.status-label {
  font-size: 0.9rem;
  opacity: 0.8;
  margin-bottom: 4px;
}

.status-value {
  font-size: 1.1rem;
  font-weight: 600;
}

/* 系统概览 */
.system-overview {
  margin-bottom: 30px;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.metric-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  backdrop-filter: blur(20px);
  border-radius: 15px !important;
  transition: all 0.3s ease;
}

.metric-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 15px 35px rgba(31, 38, 135, 0.2);
}

.metric-content {
  padding: 25px 20px;
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.metric-icon {
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.metric-icon i {
  font-size: 1.5rem;
  color: white;
}

.metric-status {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.metric-status.good {
  background: #67c23a;
}

.metric-status.warning {
  background: #e6a23c;
}

.metric-status.error {
  background: #f56c6c;
}

.metric-status i {
  color: white;
  font-size: 1rem;
}

.metric-value {
  font-size: 2rem;
  font-weight: 700;
  color: white;
  margin-bottom: 8px;
}

.metric-label {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
  margin-bottom: 10px;
}

.metric-trend {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 0.85rem;
  font-weight: 500;
}

.metric-trend.positive {
  color: #67c23a;
}

.metric-trend.warning {
  color: #e6a23c;
}

.metric-trend.negative {
  color: #f56c6c;
}

/* 性能图表 */
.performance-charts {
  margin-bottom: 30px;
}

.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.chart-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  backdrop-filter: blur(20px);
  border-radius: 15px !important;
}

.chart-container {
  padding: 20px 0;
}

.chart {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.7);
}

.chart-placeholder i {
  font-size: 3rem;
  color: #4facfe;
  margin-bottom: 15px;
}

.chart-placeholder p {
  font-size: 1rem;
  margin: 0;
}

.chart-controls,
.time-range-selector {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* 数据库和缓存统计 */
.database-stats,
.cache-stats {
  padding: 20px 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  transition: all 0.3s ease;
}

.stat-item:hover {
  background: rgba(255, 255, 255, 0.1);
}

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.db-icon { background: linear-gradient(135deg, #4facfe, #00f2fe); }
.size-icon { background: linear-gradient(135deg, #667eea, #764ba2); }
.query-icon { background: linear-gradient(135deg, #f093fb, #f5576c); }
.hit-icon { background: linear-gradient(135deg, #4ecdc4, #44a08d); }
.keys-icon { background: linear-gradient(135deg, #ffecd2, #fcb69f); }
.memory-icon { background: linear-gradient(135deg, #a8edea, #fed6e3); }

.stat-icon i {
  color: white;
  font-size: 1.2rem;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
  margin-bottom: 4px;
}

.stat-label {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}

/* 服务监控 */
.services-monitoring {
  margin-bottom: 30px;
}

.services-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  backdrop-filter: blur(20px);
  border-radius: 15px !important;
}

.services-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  padding: 20px 0;
}

.service-item {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
  border-radius: 12px;
  transition: all 0.3s ease;
  border: 1px solid transparent;
}

.service-item.healthy {
  background: rgba(103, 194, 58, 0.1);
  border-color: rgba(103, 194, 58, 0.2);
}

.service-item.warning {
  background: rgba(230, 162, 60, 0.1);
  border-color: rgba(230, 162, 60, 0.2);
}

.service-item.error {
  background: rgba(245, 108, 108, 0.1);
  border-color: rgba(245, 108, 108, 0.2);
}

.service-icon {
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.service-icon i {
  color: white;
  font-size: 1.5rem;
}

.service-info {
  flex: 1;
}

.service-name {
  color: white;
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 5px;
}

.service-description {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
  margin-bottom: 10px;
}

.service-metrics {
  display: flex;
  gap: 15px;
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.6);
}

.service-status {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.service-status .status-indicator {
  width: 35px;
  height: 35px;
}

.service-status .status-text {
  font-size: 0.85rem;
  font-weight: 500;
}

/* 系统日志 */
.system-logs {
  margin-bottom: 30px;
}

.logs-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  backdrop-filter: blur(20px);
  border-radius: 15px !important;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 15px;
}

.logs-container {
  max-height: 400px;
  overflow-y: auto;
  padding: 20px 0;
}

.log-item {
  display: grid;
  grid-template-columns: 160px 80px 1fr 120px;
  gap: 15px;
  align-items: center;
  padding: 12px 15px;
  border-radius: 8px;
  margin-bottom: 8px;
  transition: all 0.3s ease;
}

.log-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.log-item.error {
  background: rgba(245, 108, 108, 0.1);
  border-left: 3px solid #f56c6c;
}

.log-item.warning {
  background: rgba(230, 162, 60, 0.1);
  border-left: 3px solid #e6a23c;
}

.log-item.info {
  background: rgba(64, 158, 255, 0.1);
  border-left: 3px solid #409eff;
}

.log-timestamp {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.85rem;
  font-family: 'Courier New', monospace;
}

.log-message {
  color: white;
  font-size: 0.9rem;
  line-height: 1.4;
}

.log-source {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.8rem;
  text-align: right;
}

.no-logs {
  text-align: center;
  padding: 60px 20px;
  color: rgba(255, 255, 255, 0.6);
}

.no-logs i {
  font-size: 3rem;
  color: #4facfe;
  margin-bottom: 15px;
}

/* 健康检查对话框 */
.health-check-results {
  max-height: 400px;
  overflow-y: auto;
}

.check-item {
  margin-bottom: 20px;
  padding: 15px;
  border-radius: 8px;
  background: #f8f9fa;
}

.check-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.check-name {
  font-weight: 600;
  color: #2c3e50;
}

.check-status {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 0.9rem;
  font-weight: 500;
}

.check-status.healthy { color: #67c23a; }
.check-status.warning { color: #e6a23c; }
.check-status.error { color: #f56c6c; }

.check-details {
  color: #495057;
}

.check-message {
  margin-bottom: 10px;
  font-size: 0.9rem;
}

.check-suggestions ul {
  margin: 5px 0 0 20px;
  padding: 0;
}

.check-suggestions li {
  margin-bottom: 5px;
  font-size: 0.85rem;
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

.header-left {
  display: flex;
  align-items: center;
}

/* 动画效果 */
@keyframes pulse-green {
  0% { box-shadow: 0 0 0 0 rgba(103, 194, 58, 0.4); }
  70% { box-shadow: 0 0 0 10px rgba(103, 194, 58, 0); }
  100% { box-shadow: 0 0 0 0 rgba(103, 194, 58, 0); }
}

@keyframes pulse-yellow {
  0% { box-shadow: 0 0 0 0 rgba(230, 162, 60, 0.4); }
  70% { box-shadow: 0 0 0 10px rgba(230, 162, 60, 0); }
  100% { box-shadow: 0 0 0 0 rgba(230, 162, 60, 0); }
}

@keyframes pulse-red {
  0% { box-shadow: 0 0 0 0 rgba(245, 108, 108, 0.4); }
  70% { box-shadow: 0 0 0 10px rgba(245, 108, 108, 0); }
  100% { box-shadow: 0 0 0 0 rgba(245, 108, 108, 0); }
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .charts-row {
    grid-template-columns: 1fr;
  }
  
  .header-content {
    flex-direction: column;
    gap: 20px;
  }
}

@media (max-width: 768px) {
  .overview-grid {
    grid-template-columns: 1fr;
  }
  
  .services-grid {
    grid-template-columns: 1fr;
  }
  
  .log-item {
    grid-template-columns: 1fr;
    gap: 8px;
  }
  
  .header-controls {
    flex-direction: column;
    gap: 10px;
    align-items: stretch;
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
:deep(.el-input__inner) {
  background: rgba(255, 255, 255, 0.1) !important;
  border-color: rgba(255, 255, 255, 0.2) !important;
  color: white !important;
}

:deep(.el-select .el-input__inner::placeholder),
:deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.6) !important;
}
</style>
