import { createRouter, createWebHistory } from 'vue-router'
import HomeView from "@/views/HomeView.vue";
import LoginView from "@/views/LoginView.vue"
import StockNewsView from "@/views/StockNewsView.vue"
import AnalysisView from "@/views/analysis/AnalysisView.vue";
import ForecastView from "@/views/forecast/ForecastView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/stockNews',
      name: 'stockNews',
      component: StockNewsView
    },
    {
      path: '/analysis',
      name: 'analysis',
      component: AnalysisView
    },
    {
      path: '/forecast',
      name: 'forecast',
      component: ForecastView
    }
  ]
})

export default router
