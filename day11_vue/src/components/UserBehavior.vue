<template>
  <div class="user-behavior">
    <!-- 页面标题 -->
    <div class="page-header">
      <el-card class="glass-card header-card" shadow="never">
        <div class="header-content">
          <div class="header-left">
            <i class="el-icon-user-solid"></i>
            <div>
              <h1>用户行为分析</h1>
              <p>用户浏览、购买行为的数据分析与可视化</p>
            </div>
          </div>
          <div class="header-right">
            <el-select v-model="selectedUserId" placeholder="选择用户" @change="loadUserData">
              <el-option
                v-for="user in users"
                :key="user.id"
                :label="user.name"
                :value="user.id"
              />
            </el-select>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 行为统计概览 -->
    <div class="behavior-overview">
      <div class="overview-grid">
        <el-card
          v-for="stat in behaviorStats"
          :key="stat.key"
          class="glass-card stat-card"
          shadow="never"
        >
          <div class="stat-content">
            <div class="stat-icon">
              <i :class="stat.icon"></i>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-label">{{ stat.label }}</div>
              <div class="stat-change" :class="stat.changeClass">
                <i :class="stat.changeIcon"></i>
                {{ stat.change }}
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 行为分析图表 -->
    <div class="behavior-charts">
      <div class="charts-grid">
        <!-- 浏览行为趋势 -->
        <el-card class="glass-card chart-card" shadow="never">
          <template #header>
            <div class="card-header">
              <i class="el-icon-view"></i>
              <span>浏览行为趋势</span>
              <el-button-group size="small">
                <el-button
                  v-for="period in timePeriods"
                  :key="period.value"
                  :type="selectedPeriod === period.value ? 'primary' : ''"
                  @click="changePeriod(period.value)"
                  size="small"
                >
                  {{ period.label }}
                </el-button>
              </el-button-group>
            </div>
          </template>
          
          <div class="chart-container">
            <div ref="viewTrendChart" class="chart" style="height: 300px;"></div>
          </div>
        </el-card>

        <!-- 商品类别偏好 -->
        <el-card class="glass-card chart-card" shadow="never">
          <template #header>
            <div class="card-header">
              <i class="el-icon-pie-chart"></i>
              <span>商品类别偏好</span>
              <div class="chart-controls">
                <el-switch v-model="showPercentage" active-text="显示百分比" size="small" />
              </div>
            </div>
          </template>
          
          <div class="chart-container">
            <div ref="categoryChart" class="chart" style="height: 300px;"></div>
          </div>
        </el-card>
      </div>

      <!-- 行为热力图 -->
      <el-card class="glass-card full-width-chart" shadow="never">
        <template #header>
          <div class="card-header">
            <i class="el-icon-calendar"></i>
            <span>行为活跃度热力图</span>
            <el-date-picker
              v-model="heatmapDateRange"
              type="monthrange"
              range-separator="至"
              start-placeholder="开始月份"
              end-placeholder="结束月份"
              @change="loadHeatmapData"
              size="small"
            />
          </div>
        </template>
        
        <div class="chart-container">
          <div ref="heatmapChart" class="chart" style="height: 200px;"></div>
        </div>
      </el-card>
    </div>

    <!-- 行为详情列表 -->
    <div class="behavior-details">
      <el-card class="glass-card details-card" shadow="never">
        <template #header>
          <div class="card-header">
            <div class="header-left">
              <i class="el-icon-document"></i>
              <span>行为记录 ({{ behaviorRecords.length }})</span>
            </div>
            <div class="header-controls">
              <el-select v-model="filterType" placeholder="行为类型" size="small" clearable>
                <el-option label="全部" value="" />
                <el-option label="浏览" value="view" />
                <el-option label="点击" value="click" />
                <el-option label="收藏" value="favorite" />
                <el-option label="购买" value="purchase" />
              </el-select>
              <el-date-picker
                v-model="dateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                @change="loadBehaviorRecords"
                size="small"
              />
              <el-button @click="exportBehaviorData" size="small">
                <i class="el-icon-download"></i>
                导出数据
              </el-button>
            </div>
          </div>
        </template>

        <el-table
          :data="paginatedRecords"
          stripe
          class="behavior-table"
          @sort-change="handleSortChange"
          v-loading="loading"
        >
          <el-table-column prop="timestamp" label="时间" width="160" sortable>
            <template #default="{ row }">
              <div class="timestamp-cell">
                <i class="el-icon-time"></i>
                {{ formatTimestamp(row.timestamp) }}
              </div>
            </template>
          </el-table-column>
          
          <el-table-column prop="behavior_type" label="行为类型" width="100">
            <template #default="{ row }">
              <el-tag :type="getBehaviorTypeColor(row.behavior_type)" size="small">
                {{ getBehaviorTypeText(row.behavior_type) }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column prop="product_name" label="商品名称" min-width="200">
            <template #default="{ row }">
              <div class="product-cell">
                <div class="product-name">{{ row.product_info?.name || '未知商品' }}</div>
                <div class="product-category">{{ row.product_info?.category }}</div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column prop="product_price" label="商品价格" width="120">
            <template #default="{ row }">
              <div class="price-cell">
                <span class="currency">¥</span>
                <span class="amount">{{ formatPrice(row.product_info?.price) }}</span>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column prop="duration" label="停留时长" width="120">
            <template #default="{ row }">
              <span v-if="row.duration">{{ formatDuration(row.duration) }}</span>
              <span v-else class="no-data">-</span>
            </template>
          </el-table-column>
          
          <el-table-column prop="source" label="来源" width="120">
            <template #default="{ row }">
              <el-tag size="small" type="info">{{ row.source || '直接访问' }}</el-tag>
            </template>
          </el-table-column>
          
          <el-table-column label="操作" width="150">
            <template #default="{ row }">
              <el-button-group size="small">
                <el-button @click="viewBehaviorDetail(row)" size="small">
                  <i class="el-icon-view"></i>
                  详情
                </el-button>
                <el-button @click="analyzeBehavior(row)" size="small" type="primary">
                  <i class="el-icon-data-analysis"></i>
                  分析
                </el-button>
              </el-button-group>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination-container">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredRecords.length"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </el-card>
    </div>

    <!-- 行为详情对话框 -->
    <el-dialog v-model="behaviorDetailVisible" title="行为详情" width="600px">
      <div v-if="selectedBehavior" class="behavior-detail">
        <div class="detail-grid">
          <div class="detail-item">
            <strong>行为类型:</strong>
            <el-tag :type="getBehaviorTypeColor(selectedBehavior.behavior_type)">
              {{ getBehaviorTypeText(selectedBehavior.behavior_type) }}
            </el-tag>
          </div>
          <div class="detail-item">
            <strong>发生时间:</strong>
            <span>{{ formatTimestamp(selectedBehavior.timestamp) }}</span>
          </div>
          <div class="detail-item">
            <strong>用户ID:</strong>
            <span>{{ selectedBehavior.user_id }}</span>
          </div>
          <div class="detail-item">
            <strong>会话ID:</strong>
            <span>{{ selectedBehavior.session_id }}</span>
          </div>
        </div>
        
        <div class="product-detail-section" v-if="selectedBehavior.product_info">
          <h3>商品信息</h3>
          <div class="product-detail-grid">
            <div class="detail-item">
              <strong>商品名称:</strong>
              <span>{{ selectedBehavior.product_info.name }}</span>
            </div>
            <div class="detail-item">
              <strong>商品价格:</strong>
              <span class="price">¥{{ formatPrice(selectedBehavior.product_info.price) }}</span>
            </div>
            <div class="detail-item">
              <strong>商品类别:</strong>
              <span>{{ selectedBehavior.product_info.category }}</span>
            </div>
            <div class="detail-item" v-if="selectedBehavior.product_info.brand">
              <strong>商品品牌:</strong>
              <span>{{ selectedBehavior.product_info.brand }}</span>
            </div>
          </div>
        </div>
        
        <div class="behavior-context" v-if="selectedBehavior.context">
          <h3>上下文信息</h3>
          <pre class="context-data">{{ JSON.stringify(selectedBehavior.context, null, 2) }}</pre>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

// 响应式数据
const selectedUserId = ref('user_001')
const users = ref([
  { id: 'user_001', name: '用户001' },
  { id: 'user_002', name: '用户002' },
  { id: 'user_003', name: '用户003' }
])
const behaviorRecords = ref([])
const loading = ref(false)
const selectedPeriod = ref('7d')
const showPercentage = ref(true)
const heatmapDateRange = ref([])
const filterType = ref('')
const dateRange = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const behaviorDetailVisible = ref(false)
const selectedBehavior = ref(null)

// 图表引用
const viewTrendChart = ref(null)
const categoryChart = ref(null)
const heatmapChart = ref(null)

// 时间周期选项
const timePeriods = [
  { label: '7天', value: '7d' },
  { label: '30天', value: '30d' },
  { label: '90天', value: '90d' }
]

// 行为统计数据
const behaviorStats = ref([
  {
    key: 'total_views',
    label: '总浏览量',
    value: 0,
    icon: 'el-icon-view',
    change: '+12.5%',
    changeClass: 'positive',
    changeIcon: 'el-icon-top'
  },
  {
    key: 'unique_products',
    label: '浏览商品数',
    value: 0,
    icon: 'el-icon-goods',
    change: '+8.2%',
    changeClass: 'positive',
    changeIcon: 'el-icon-top'
  },
  {
    key: 'avg_session_duration',
    label: '平均会话时长',
    value: '0分钟',
    icon: 'el-icon-time',
    change: '-2.1%',
    changeClass: 'negative',
    changeIcon: 'el-icon-bottom'
  },
  {
    key: 'conversion_rate',
    label: '转化率',
    value: '0%',
    icon: 'el-icon-trophy',
    change: '+5.3%',
    changeClass: 'positive',
    changeIcon: 'el-icon-top'
  }
])

// 计算属性
const filteredRecords = computed(() => {
  let filtered = behaviorRecords.value

  // 按类型筛选
  if (filterType.value) {
    filtered = filtered.filter(record => record.behavior_type === filterType.value)
  }

  // 按日期筛选
  if (dateRange.value && dateRange.value.length === 2) {
    const startDate = new Date(dateRange.value[0])
    const endDate = new Date(dateRange.value[1])
    filtered = filtered.filter(record => {
      const recordDate = new Date(record.timestamp)
      return recordDate >= startDate && recordDate <= endDate
    })
  }

  return filtered
})

const paginatedRecords = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredRecords.value.slice(start, end)
})

// 加载用户数据
const loadUserData = async () => {
  loading.value = true
  try {
    // 加载行为记录
    await loadBehaviorRecords()
    
    // 加载统计数据
    await loadBehaviorStats()
    
    // 加载图表数据
    await loadChartData()
    
    ElMessage.success('用户数据加载完成')
  } catch (error) {
    console.error('加载用户数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 加载行为记录
const loadBehaviorRecords = async () => {
  try {
    const params = {
      user_id: selectedUserId.value,
      limit: 1000
    }
    
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0].toISOString()
      params.end_date = dateRange.value[1].toISOString()
    }

    const response = await axios.get('http://localhost:8000/user_behavior/api/records/', { params })
    
    if (response.data.success) {
      behaviorRecords.value = response.data.records
    }
  } catch (error) {
    console.error('加载行为记录失败:', error)
  }
}

// 加载行为统计
const loadBehaviorStats = async () => {
  try {
    const response = await axios.get(`http://localhost:8000/user_behavior/api/stats/?user_id=${selectedUserId.value}&period=${selectedPeriod.value}`)
    
    if (response.data.success) {
      const stats = response.data.stats
      
      // 更新统计数据
      behaviorStats.value[0].value = stats.total_views || 0
      behaviorStats.value[1].value = stats.unique_products || 0
      behaviorStats.value[2].value = formatDuration(stats.avg_session_duration || 0)
      behaviorStats.value[3].value = `${Math.round((stats.conversion_rate || 0) * 100)}%`
    }
  } catch (error) {
    console.error('加载行为统计失败:', error)
  }
}

// 加载图表数据
const loadChartData = async () => {
  try {
    const response = await axios.get('http://localhost:8000/user_behavior/api/trends/', {
      params: {
        user_id: selectedUserId.value,
        period: selectedPeriod.value
      }
    })
    
    if (response.data.success) {
      const data = response.data.data
      
      // 更新趋势图表数据 (这里只是示例，实际需要使用图表库如ECharts)
      console.log('趋势数据:', data.trend)
      console.log('类别数据:', data.categories)
      
      // TODO: 实际更新ECharts图表
      // updateTrendChart(data.trend)
      // updateCategoryChart(data.categories)
    }
  } catch (error) {
    console.error('加载图表数据失败:', error)
  }
}

// 加载热力图数据
const loadHeatmapData = async () => {
  console.log('Loading heatmap data for range:', heatmapDateRange.value)
}

// 改变时间周期
const changePeriod = (period) => {
  selectedPeriod.value = period
  loadBehaviorStats()
  loadChartData()
}

// 处理排序变化
const handleSortChange = ({ column, prop, order }) => {
  if (prop === 'timestamp') {
    behaviorRecords.value.sort((a, b) => {
      const dateA = new Date(a.timestamp)
      const dateB = new Date(b.timestamp)
      return order === 'ascending' ? dateA - dateB : dateB - dateA
    })
  }
}

// 处理分页变化
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (page) => {
  currentPage.value = page
}

// 查看行为详情
const viewBehaviorDetail = (behavior) => {
  selectedBehavior.value = behavior
  behaviorDetailVisible.value = true
}

// 分析行为
const analyzeBehavior = (behavior) => {
  ElMessage.info('行为分析功能开发中...')
}

// 导出行为数据
const exportBehaviorData = () => {
  if (behaviorRecords.value.length === 0) {
    ElMessage.warning('暂无数据可导出')
    return
  }

  const csvContent = [
    ['时间', '行为类型', '商品名称', '商品价格', '商品类别', '停留时长', '来源'],
    ...behaviorRecords.value.map(record => [
      formatTimestamp(record.timestamp),
      getBehaviorTypeText(record.behavior_type),
      record.product_info?.name || '',
      record.product_info?.price || '',
      record.product_info?.category || '',
      formatDuration(record.duration || 0),
      record.source || ''
    ])
  ].map(row => row.join(',')).join('\n')

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `用户行为数据_${selectedUserId.value}_${new Date().toISOString().slice(0, 10)}.csv`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)

  ElMessage.success('数据导出完成')
}

// 工具函数
const formatTimestamp = (timestamp) => {
  return new Date(timestamp).toLocaleString()
}

const formatPrice = (price) => {
  return parseFloat(price || 0).toFixed(2)
}

const formatDuration = (seconds) => {
  if (!seconds) return '0秒'
  
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  
  if (minutes === 0) {
    return `${remainingSeconds}秒`
  } else {
    return `${minutes}分${remainingSeconds}秒`
  }
}

const getBehaviorTypeText = (type) => {
  const typeMap = {
    'view': '浏览',
    'click': '点击',
    'favorite': '收藏',
    'purchase': '购买',
    'search': '搜索'
  }
  return typeMap[type] || type
}

const getBehaviorTypeColor = (type) => {
  const colorMap = {
    'view': 'info',
    'click': 'primary',
    'favorite': 'warning',
    'purchase': 'success',
    'search': 'purple'
  }
  return colorMap[type] || ''
}

// 组件挂载时加载数据
onMounted(() => {
  loadUserData()
})
</script>

<style scoped>
.user-behavior {
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

/* 行为统计概览 */
.behavior-overview {
  margin-bottom: 30px;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.stat-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  backdrop-filter: blur(20px);
  border-radius: 15px !important;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 15px 35px rgba(31, 38, 135, 0.2);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 30px 20px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  border-radius: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon i {
  font-size: 1.8rem;
  color: white;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: white;
  margin-bottom: 5px;
}

.stat-label {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
  margin-bottom: 8px;
}

.stat-change {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 0.85rem;
  font-weight: 500;
}

.stat-change.positive {
  color: #67c23a;
}

.stat-change.negative {
  color: #f56c6c;
}

/* 图表区域 */
.behavior-charts {
  margin-bottom: 30px;
}

.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.chart-card,
.full-width-chart {
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
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.7);
  font-size: 1rem;
}

.chart-controls {
  display: flex;
  align-items: center;
  gap: 15px;
}

/* 行为详情列表 */
.behavior-details {
  margin-bottom: 30px;
}

.details-card {
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

.behavior-table {
  margin: 20px 0;
}

.timestamp-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.9rem;
}

.timestamp-cell i {
  color: #4facfe;
}

.product-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.product-name {
  color: white;
  font-weight: 500;
  font-size: 0.9rem;
}

.product-category {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.8rem;
}

.price-cell {
  display: flex;
  align-items: baseline;
  gap: 2px;
  color: #4facfe;
  font-weight: 600;
}

.currency {
  font-size: 0.9rem;
}

.amount {
  font-size: 1rem;
}

.no-data {
  color: rgba(255, 255, 255, 0.4);
  font-style: italic;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

/* 行为详情对话框 */
.behavior-detail {
  max-height: 400px;
  overflow-y: auto;
}

.detail-grid,
.product-detail-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 15px;
  margin-bottom: 20px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
}

.detail-item strong {
  color: #495057;
  min-width: 100px;
}

.detail-item .price {
  color: #4facfe;
  font-weight: 600;
}

.product-detail-section,
.behavior-context {
  margin-top: 20px;
}

.product-detail-section h3,
.behavior-context h3 {
  color: #2c3e50;
  margin-bottom: 15px;
  font-size: 1.2rem;
}

.context-data {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  font-size: 0.85rem;
  max-height: 200px;
  overflow-y: auto;
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

/* 响应式设计 */
@media (max-width: 1024px) {
  .charts-grid {
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
  
  .stat-content {
    padding: 20px 15px;
  }
  
  .header-controls {
    flex-direction: column;
    gap: 10px;
  }
  
  .detail-grid,
  .product-detail-grid {
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

:deep(.el-table) {
  background: transparent !important;
  color: white !important;
}

:deep(.el-table th),
:deep(.el-table td) {
  border-bottom-color: rgba(255, 255, 255, 0.1) !important;
  background: transparent !important;
}

:deep(.el-table__header-wrapper) {
  background: rgba(255, 255, 255, 0.05) !important;
}

:deep(.el-table__row:hover > td) {
  background: rgba(255, 255, 255, 0.05) !important;
}

:deep(.el-table__row--striped > td) {
  background: rgba(255, 255, 255, 0.02) !important;
}

:deep(.el-pagination) {
  color: white !important;
}

:deep(.el-pagination .el-pager li) {
  background: rgba(255, 255, 255, 0.1) !important;
  color: white !important;
}

:deep(.el-pagination .el-pager li.active) {
  background: #4facfe !important;
}

:deep(.el-select .el-input__inner),
:deep(.el-date-editor .el-input__inner) {
  background: rgba(255, 255, 255, 0.1) !important;
  border-color: rgba(255, 255, 255, 0.2) !important;
  color: white !important;
}
</style>
