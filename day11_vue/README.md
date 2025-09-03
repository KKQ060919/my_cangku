# 智能商品推荐系统 - 前端应用

基于 Vue 3 + Vite + Element Plus 构建的现代化前端应用，为智能商品推荐系统提供用户界面。

## 🚀 技术栈

- **Vue 3** - 响应式前端框架
- **Vite** - 快速构建工具
- **Vue Router** - 单页面应用路由
- **Element Plus** - Vue 3 UI组件库
- **Axios** - HTTP请求客户端

## 📦 项目结构

```
day11_vue/
├── public/          # 静态资源
├── src/
│   ├── components/  # Vue组件
│   │   ├── HomePage.vue              # 首页
│   │   ├── ProductRecommendation.vue # 商品推荐
│   │   ├── SmartQA.vue              # 智能问答
│   │   ├── UserBehavior.vue         # 用户行为分析
│   │   ├── SystemStats.vue          # 系统统计
│   │   └── Layout.vue               # 布局组件
│   ├── router/      # 路由配置
│   ├── App.vue      # 根组件
│   ├── main.js      # 应用入口
│   └── style.css    # 全局样式
└── package.json     # 项目依赖
```

## 🎨 页面功能

### 1. 首页 (HomePage)
- 系统概览和欢迎页面
- 快速功能入口
- 系统状态展示
- 最近活动记录

### 2. 商品推荐 (ProductRecommendation)
- 个性化推荐设置
- 推荐结果展示
- 商品详情查看
- 用户反馈收集

### 3. 智能问答 (SmartQA)
- 实时聊天界面
- RAG驱动的问答
- 相关商品推荐
- 对话历史记录

### 4. 用户行为分析 (UserBehavior)
- 行为数据可视化
- 统计图表展示
- 行为记录列表
- 数据导出功能

### 5. 系统统计 (SystemStats)
- 系统性能监控
- 服务状态检查
- 数据库统计
- 系统日志查看

## 🛠️ 开发指南

### 环境准备

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

### API集成

应用通过Axios与Django后端通信，主要API端点：

```javascript
// 推荐API
POST /recommendation/api/recommend/

// 问答API
POST /rag/api/ask/

// 用户行为API
POST /user_behavior/api/view/

// 缓存管理API
GET /cache_management/api/stats/
```

### 组件开发

使用Vue 3 Composition API和`<script setup>`语法：

```vue
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const data = ref([])

const loadData = async () => {
  const response = await axios.get('/api/endpoint')
  data.value = response.data
}

onMounted(() => {
  loadData()
})
</script>
```

### 样式设计

- 使用CSS Grid和Flexbox布局
- 响应式设计适配多种设备
- 玻璃拟态(Glassmorphism)视觉效果
- Element Plus主题定制

### 状态管理

通过组件内部状态和Props进行数据传递，大型数据使用Axios请求实时获取。

## 🎯 开发规范

### 代码风格
- 使用ESLint进行代码检查
- 遵循Vue 3官方风格指南
- 组件命名采用PascalCase
- 文件命名采用kebab-case

### 组件结构
```vue
<template>
  <!-- 模板内容 -->
</template>

<script setup>
  // 组合式API逻辑
</script>

<style scoped>
  /* 组件样式 */
</style>
```

### Git提交规范
- feat: 新功能
- fix: 修复bug
- docs: 文档更新
- style: 代码格式调整
- refactor: 代码重构

## 🔧 配置说明

### Vite配置 (vite.config.js)
```javascript
export default {
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
}
```

### 路由配置 (router/index.js)
```javascript
const routes = [
  { path: '/', component: HomePage },
  { path: '/recommendations', component: ProductRecommendation },
  { path: '/qa', component: SmartQA },
  { path: '/behavior', component: UserBehavior },
  { path: '/stats', component: SystemStats }
]
```

## 📱 响应式设计

应用支持多种设备尺寸：
- 桌面端: > 1024px
- 平板端: 768px - 1024px  
- 手机端: < 768px

## 🚀 部署指南

### 开发环境
```bash
npm run dev
```

### 生产构建
```bash
npm run build
```

### 预览构建结果
```bash
npm run preview
```

### 部署到服务器
构建后将`dist`目录内容部署到Web服务器即可。

## 📝 维护说明

- 定期更新依赖包版本
- 监控构建性能和包大小
- 测试多浏览器兼容性
- 优化首屏加载速度

更多信息请参考主项目README文档。
