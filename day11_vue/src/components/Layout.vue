<template>
  <div class="layout">
    <!-- 导航栏 -->
    <nav class="navbar">
      <div class="nav-brand">
        <i class="el-icon-shopping-bag-2"></i>
        <span>智能商品推荐系统</span>
      </div>
      <div class="nav-menu">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: $route.path === item.path }"
        >
          <i :class="item.icon"></i>
          <span>{{ item.label }}</span>
        </router-link>
      </div>
      <div class="nav-user">
        <el-dropdown @command="handleUserCommand">
          <span class="user-info">
            <i class="el-icon-user"></i>
            <span>{{ currentUser }}</span>
            <i class="el-icon-arrow-down"></i>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="switch">切换用户</el-dropdown-item>
              <el-dropdown-item command="clear">清空数据</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </nav>

    <!-- 主要内容区域 -->
    <main class="main-content">
      <router-view />
    </main>

    <!-- 用户切换对话框 -->
    <el-dialog v-model="userDialogVisible" title="切换用户" width="400px">
      <el-form>
        <el-form-item label="用户ID:">
          <el-input v-model="newUserId" placeholder="输入用户ID，如：user_001" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="userDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="switchUser">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()

// 响应式数据
const currentUser = ref(localStorage.getItem('currentUserId') || 'user_001')
const userDialogVisible = ref(false)
const newUserId = ref('')

// 菜单项配置
const menuItems = [
  { path: '/', label: '首页', icon: 'el-icon-house' },
  { path: '/products', label: '商品展示', icon: 'el-icon-goods' },
  { path: '/recommendations', label: '智能推荐', icon: 'el-icon-magic-stick' },
  { path: '/qa', label: '智能问答', icon: 'el-icon-chat-dot-round' },
  { path: '/behavior', label: '用户行为', icon: 'el-icon-user-solid' },
  { path: '/stats', label: '系统统计', icon: 'el-icon-data-analysis' }
]

// 处理用户命令
const handleUserCommand = (command) => {
  if (command === 'switch') {
    newUserId.value = currentUser.value
    userDialogVisible.value = true
  } else if (command === 'clear') {
    // 清空用户相关数据
    ElMessage.success('数据已清空')
  }
}

// 切换用户
const switchUser = () => {
  if (!newUserId.value) {
    ElMessage.warning('请输入用户ID')
    return
  }
  
  currentUser.value = newUserId.value
  localStorage.setItem('currentUserId', newUserId.value)
  userDialogVisible.value = false
  ElMessage.success(`已切换到用户：${newUserId.value}`)
}

// 组件挂载时设置当前用户
onMounted(() => {
  if (!localStorage.getItem('currentUserId')) {
    localStorage.setItem('currentUserId', 'user_001')
  }
})

// 导出当前用户ID供子组件使用
window.getCurrentUserId = () => currentUser.value
</script>

<style scoped>
.layout {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* 导航栏样式 */
.navbar {
  backdrop-filter: blur(20px);
  background: rgba(255, 255, 255, 0.1);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding: 0 30px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 70px;
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
}

.nav-brand {
  display: flex;
  align-items: center;
  color: white;
  font-size: 1.2rem;
  font-weight: 600;
  gap: 10px;
}

.nav-brand i {
  font-size: 1.5rem;
  color: #4facfe;
}

.nav-menu {
  display: flex;
  gap: 30px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  padding: 8px 16px;
  border-radius: 8px;
  transition: all 0.3s ease;
  font-weight: 500;
}

.nav-item:hover {
  color: white;
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
}

.nav-item.active {
  color: white;
  background: rgba(79, 172, 254, 0.2);
  border: 1px solid rgba(79, 172, 254, 0.3);
}

.nav-item i {
  font-size: 1.1rem;
}

.nav-user {
  color: white;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.user-info:hover {
  background: rgba(255, 255, 255, 0.1);
}

/* 主要内容区域 */
.main-content {
  min-height: calc(100vh - 70px);
  padding: 30px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .navbar {
    padding: 0 15px;
    height: 60px;
  }
  
  .nav-menu {
    gap: 15px;
  }
  
  .nav-item span {
    display: none;
  }
  
  .nav-brand span {
    display: none;
  }
  
  .main-content {
    padding: 15px;
  }
}

/* Element Plus 样式覆盖 */
:deep(.el-dropdown) {
  color: white;
}

:deep(.el-dropdown-menu) {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}
</style>
