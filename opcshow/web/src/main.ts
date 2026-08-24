import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './styles/main.css'
import { api } from './api'

// 访问统计（PRD：后台数据统计）
api.post('/visit', {}).catch(() => {})

createApp(App).use(router).mount('#app')
