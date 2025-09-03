import {createWebHistory, createRouter} from 'vue-router'

import Layout from '../src/components/Layout.vue'
import HomePage from '../src/components/HomePage.vue'
import ProductRecommendation from '../src/components/ProductRecommendation.vue'
import ProductList from '../src/components/ProductList.vue'
import ProductDetail from '../src/components/ProductDetail.vue'
import SmartQA from '../src/components/SmartQA.vue'
import UserBehavior from '../src/components/UserBehavior.vue'
import SystemStats from '../src/components/SystemStats.vue'

const routes = [
    {
        path: '/',
        component: Layout,
        children: [
            {
                path: '',
                component: HomePage,
                name: 'Home',
                meta: { title: '首页' }
            },
            {
                path: '/recommendations',
                component: ProductRecommendation,
                name: 'Recommendations',
                meta: { title: '智能推荐' }
            },
            {
                path: '/products',
                component: ProductList,
                name: 'ProductList',
                meta: { title: '商品展示' }
            },
            {
                path: '/products/:productId',
                component: ProductDetail,
                name: 'ProductDetail',
                meta: { title: '商品详情' }
            },
            {
                path: '/qa',
                component: SmartQA,
                name: 'SmartQA',
                meta: { title: '智能问答' }
            },
            {
                path: '/behavior',
                component: UserBehavior,
                name: 'UserBehavior',
                meta: { title: '用户行为' }
            },
            {
                path: '/stats',
                component: SystemStats,
                name: 'SystemStats',
                meta: { title: '系统统计' }
            }
        ]
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

export default router