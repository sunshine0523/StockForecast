import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

import './assets/main.css'
//引入element样式
import 'element-plus/theme-chalk/src/index.scss'

const app = createApp(App)

app.use(router)

app.mount('#app')