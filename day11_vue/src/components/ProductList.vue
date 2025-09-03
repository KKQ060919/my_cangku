<template>
  <div class="product-list">
    <!-- 页面标题 -->
    <div class="page-header">
      <el-card class="glass-card header-card" shadow="never">
        <div class="header-content">
          <div class="header-left">
            <i class="el-icon-goods"></i>
            <div>
              <h1>商品展示</h1>
              <p>浏览我们的精选商品</p>
            </div>
          </div>
          <div class="header-right">
            <el-tag type="primary" size="large">共{{ totalCount }}件商品</el-tag>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 筛选和搜索面板 -->
    <div class="filter-panel">
      <el-card class="glass-card" shadow="never">
        <template #header>
          <div class="card-header">
            <i class="el-icon-search"></i>
            <span>搜索与筛选</span>
          </div>
        </template>

        <el-form :model="filters" label-width="80px" class="filter-form">
          <el-row :gutter="20">
            <el-col :span="6">
              <el-form-item label="搜索:">
                <el-input
                  v-model="filters.search"
                  placeholder="搜索商品名称、品牌、描述"
                  clearable
                  @keyup.enter="loadProducts(true)"
                  @clear="loadProducts(true)"
                >
                  <template #prefix>
                    <i class="el-icon-search"></i>
                  </template>
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="4">
              <el-form-item label="类别:">
                <el-select v-model="filters.category" placeholder="选择类别" clearable @change="loadProducts(true)">
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
            <el-col :span="4">
              <el-form-item label="品牌:">
                <el-select v-model="filters.brand" placeholder="选择品牌" clearable @change="loadProducts(true)">
                  <el-option label="全部品牌" value="" />
                  <el-option 
                    v-for="brand in brands" 
                    :key="brand" 
                    :label="brand" 
                    :value="brand" 
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="4">
              <el-form-item label="排序:">
                <el-select v-model="filters.sortBy" @change="loadProducts(true)">
                  <el-option label="名称" value="name" />
                  <el-option label="价格低到高" value="price" />
                  <el-option label="价格高到低" value="price_desc" />
                  <el-option label="最新更新" value="updated_at" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item>
                <el-button 
                  type="primary" 
                  @click="loadProducts(true)" 
                  :loading="loading"
                  size="large"
                >
                  <i class="el-icon-search"></i>
                  搜索
                </el-button>
                <el-button @click="clearFilters" size="large">
                  <i class="el-icon-refresh"></i>
                  重置
                </el-button>
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </el-card>
    </div>

    <!-- 商品列表 -->
    <div class="products-section" v-if="products.length > 0">
      <el-card class="glass-card" shadow="never">
        <template #header>
          <div class="card-header">
            <div class="header-left">
              <i class="el-icon-goods"></i>
              <span>商品列表 ({{ products.length }})</span>
            </div>
            <div class="view-controls">
              <el-radio-group v-model="viewMode" size="small">
                <el-radio-button value="grid">
                  <i class="el-icon-grid"></i>
                  网格视图
                </el-radio-button>
                <el-radio-button value="list">
                  <i class="el-icon-menu"></i>
                  列表视图
                </el-radio-button>
              </el-radio-group>
            </div>
          </div>
        </template>

        <!-- 网格视图 -->
        <div class="products-grid" v-if="viewMode === 'grid'">
          <div 
            v-for="product in products" 
            :key="product.product_id"
            class="product-card"
            @click="viewProductDetail(product)"
          >
            <div class="product-image">
              <div class="placeholder-image">
                <i class="el-icon-picture-outline"></i>
              </div>
              <div class="product-tags">
                <el-tag v-if="product.is_hot" size="small" type="warning" class="hot-tag">热门</el-tag>
                <el-tag v-if="product.stock < 10" size="small" type="danger" class="stock-tag">库存不足</el-tag>
              </div>
            </div>
            <div class="product-content">
              <h3 class="product-name">{{ product.name }}</h3>
              <div class="product-brand">{{ product.brand }}</div>
              <div class="product-price">
                <span class="currency">¥</span>
                <span class="amount">{{ formatPrice(product.price) }}</span>
              </div>
              <div class="product-category">{{ product.category }}</div>
              <div class="product-stock" :class="{ 'low-stock': product.stock < 10 }">
                库存: {{ product.stock }}
              </div>
              <p class="product-description" v-if="product.description">
                {{ product.description.substring(0, 80) }}...
              </p>
            </div>
            <div class="product-actions">
              <el-button size="small" type="primary" @click.stop="viewProductDetail(product)">
                <i class="el-icon-view"></i>
                查看详情
              </el-button>
              <el-button size="small" @click.stop="addToCart(product)">
                <i class="el-icon-shopping-cart-2"></i>
                加入收藏
              </el-button>
            </div>
          </div>
        </div>

        <!-- 列表视图 -->
        <div class="products-list" v-if="viewMode === 'list'">
          <div 
            v-for="product in products" 
            :key="product.product_id"
            class="product-list-item"
            @click="viewProductDetail(product)"
          >
            <div class="list-item-left">
              <div class="product-image-small">
                <i class="el-icon-picture-outline"></i>
              </div>
              <div class="product-info">
                <h4 class="product-name">{{ product.name }}</h4>
                <div class="product-meta">
                  <span class="brand">{{ product.brand }}</span>
                  <span class="category">{{ product.category }}</span>
                </div>
                <p class="product-description" v-if="product.description">
                  {{ product.description.substring(0, 120) }}...
                </p>
              </div>
            </div>
            <div class="list-item-right">
              <div class="product-price">
                <span class="currency">¥</span>
                <span class="amount">{{ formatPrice(product.price) }}</span>
              </div>
              <div class="product-stock" :class="{ 'low-stock': product.stock < 10 }">
                库存: {{ product.stock }}
              </div>
              <div class="product-tags">
                <el-tag v-if="product.is_hot" size="small" type="warning">热门</el-tag>
              </div>
              <div class="product-actions">
                <el-button size="small" type="primary" @click.stop="viewProductDetail(product)">
                  查看详情
                </el-button>
                <el-button size="small" @click.stop="addToCart(product)">
                  加入收藏
                </el-button>
              </div>
            </div>
          </div>
        </div>

        <!-- 分页 -->
        <div class="pagination-wrapper" v-if="totalPages > 1">
          <el-pagination
            v-model:current-page="currentPage"
            :page-size="pageSize"
            :total="totalCount"
            :page-sizes="[12, 24, 36, 48]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
            background
          />
        </div>
      </el-card>
    </div>

    <!-- 无商品时的占位符 -->
    <div class="no-products" v-else-if="!loading">
      <el-card class="glass-card" shadow="never">
        <div class="empty-state">
          <i class="el-icon-goods"></i>
          <h3>没有找到商品</h3>
          <p>尝试调整搜索条件或筛选器</p>
          <el-button type="primary" @click="clearFilters">清空筛选条件</el-button>
        </div>
      </el-card>
    </div>

    <!-- 加载状态 -->
    <div class="loading-state" v-if="loading">
      <el-card class="glass-card" shadow="never">
        <div class="loading-content">
          <el-icon class="is-loading">
            <Loading />
          </el-icon>
          <p>正在加载商品...</p>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

// 响应式数据
const loading = ref(false)
const products = ref([])
const categories = ref([])
const brands = ref([])
const viewMode = ref('grid')

// 分页数据
const currentPage = ref(1)
const pageSize = ref(12)
const totalCount = ref(0)
const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value))

// 筛选条件
const filters = reactive({
  search: '',
  category: '',
  brand: '',
  sortBy: 'name'
})

// 加载商品数据
const loadProducts = async (resetPage = false) => {
  if (resetPage) {
    currentPage.value = 1
  }
  
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      search: filters.search,
      category: filters.category,
      brand: filters.brand,
      sort_by: filters.sortBy
    }

    // 移除空参数
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null) {
        delete params[key]
      }
    })

    const response = await axios.get('http://localhost:8000/api/products/list/', { params })

    if (response.data.success) {
      products.value = response.data.products
      totalCount.value = response.data.pagination.total_count
      ElMessage.success(`加载了 ${products.value.length} 件商品`)
    } else {
      ElMessage.error(response.data.error || '加载商品失败')
    }
  } catch (error) {
    console.error('加载商品错误:', error)
    ElMessage.error('网络错误，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 加载类别列表
const loadCategories = async () => {
  try {
    const response = await axios.get('http://localhost:8000/api/products/categories/')
    if (response.data.success) {
      categories.value = response.data.categories
    }
  } catch (error) {
    console.error('加载类别失败:', error)
  }
}

// 加载品牌列表
const loadBrands = async () => {
  try {
    const response = await axios.get('http://localhost:8000/api/products/brands/')
    if (response.data.success) {
      brands.value = response.data.brands
    }
  } catch (error) {
    console.error('加载品牌失败:', error)
  }
}

// 查看商品详情
const viewProductDetail = async (product) => {
  // 记录点击行为
  await recordClickBehavior(product.product_id)
  
  router.push({
    name: 'ProductDetail',
    params: { productId: product.product_id }
  })
}

// 记录用户点击行为
const recordClickBehavior = async (productId) => {
  try {
    const currentUserId = localStorage.getItem('currentUserId') || 'user_001'
    
    const response = await axios.post('http://localhost:8000/user_behavior/api/record/', {
      user_id: currentUserId,
      product_id: productId
    })

    if (response.data.code === 1) {
      console.log('用户点击行为记录成功:', response.data.message)
    } else {
      console.warn('用户点击行为记录失败:', response.data.message)
    }
  } catch (error) {
    console.error('记录用户点击行为失败:', error)
    // 不影响主要功能，只记录日志
  }
}

// 添加到收藏
const addToCart = (product) => {
  ElMessage.success(`已将"${product.name}"添加到收藏`)
  // 这里可以添加实际的收藏逻辑
}

// 清空筛选条件
const clearFilters = () => {
  filters.search = ''
  filters.category = ''
  filters.brand = ''
  filters.sortBy = 'name'
  loadProducts(true)
}

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val
  loadProducts(true)
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  loadProducts()
}

// 格式化价格
const formatPrice = (price) => {
  return parseFloat(price || 0).toFixed(2)
}

// 组件挂载时加载数据
onMounted(() => {
  loadProducts()
  loadCategories()
  loadBrands()
})
</script>

<style scoped>
.product-list {
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

/* 筛选面板 */
.filter-panel {
  margin-bottom: 30px;
}

.filter-form {
  padding: 20px 0;
}

.filter-form :deep(.el-form-item__label) {
  color: white !important;
  font-weight: 500 !important;
}

.filter-form :deep(.el-select),
.filter-form :deep(.el-input) {
  width: 100%;
}

/* 商品网格视图 */
.view-controls {
  display: flex;
  align-items: center;
  gap: 15px;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  padding: 20px 0;
}

.product-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
}

.product-card:hover {
  transform: translateY(-3px);
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

.product-image {
  height: 200px;
  background: rgba(255, 255, 255, 0.02);
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.placeholder-image {
  font-size: 3rem;
  color: rgba(255, 255, 255, 0.3);
}

.product-tags {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.product-content {
  padding: 20px;
}

.product-name {
  color: white;
  font-size: 1.2rem;
  margin: 0 0 10px 0;
  font-weight: 600;
  line-height: 1.3;
}

.product-brand {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
  margin-bottom: 10px;
}

.product-price {
  display: flex;
  align-items: baseline;
  gap: 2px;
  margin-bottom: 10px;
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
  display: inline-block;
  margin-bottom: 10px;
}

.product-stock {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.85rem;
  margin-bottom: 10px;
}

.product-stock.low-stock {
  color: #f56c6c;
  font-weight: 600;
}

.product-description {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.85rem;
  line-height: 1.4;
  margin: 10px 0;
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

/* 商品列表视图 */
.products-list {
  padding: 20px 0;
}

.product-list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.product-list-item:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

.list-item-left {
  display: flex;
  align-items: center;
  gap: 20px;
  flex: 1;
}

.product-image-small {
  width: 80px;
  height: 80px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: rgba(255, 255, 255, 0.3);
}

.product-info {
  flex: 1;
}

.product-info .product-name {
  font-size: 1.2rem;
  margin-bottom: 8px;
}

.product-meta {
  display: flex;
  gap: 15px;
  margin-bottom: 8px;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
}

.list-item-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 10px;
  min-width: 200px;
}

/* 分页 */
.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding: 30px 0;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  margin-top: 20px;
}

/* 空状态 */
.no-products, .loading-state {
  margin-bottom: 30px;
}

.empty-state, .loading-content {
  text-align: center;
  padding: 80px 20px;
  color: rgba(255, 255, 255, 0.7);
}

.empty-state i, .loading-content i {
  font-size: 4rem;
  color: #4facfe;
  margin-bottom: 20px;
}

.empty-state h3 {
  color: white;
  font-size: 1.5rem;
  margin: 20px 0;
}

.empty-state p, .loading-content p {
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

.header-left {
  display: flex;
  align-items: center;
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
  
  .product-list-item {
    flex-direction: column;
    gap: 20px;
  }
  
  .list-item-left, .list-item-right {
    width: 100%;
  }
  
  .list-item-right {
    align-items: flex-start;
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
:deep(.el-input .el-input__inner) {
  background: rgba(255, 255, 255, 0.1) !important;
  border-color: rgba(255, 255, 255, 0.2) !important;
  color: white !important;
}

:deep(.el-select .el-input__inner::placeholder),
:deep(.el-input .el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.6) !important;
}

:deep(.el-pagination) {
  color: white !important;
}

:deep(.el-pagination .el-pager li) {
  background: rgba(255, 255, 255, 0.1) !important;
  border-color: rgba(255, 255, 255, 0.2) !important;
  color: white !important;
}

:deep(.el-pagination .el-pager li.active) {
  background: #4facfe !important;
  color: white !important;
}
</style>
