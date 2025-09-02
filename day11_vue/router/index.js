import {createWebHistory, createRouter} from 'vue-router'

import StockAdvisor from '../src/components/StockAdvisor.vue'

const routes = [
    {
        path: '/',
        component: StockAdvisor,
        name: 'Home',
        meta: { title: '智能股票顾问' }
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

export default router