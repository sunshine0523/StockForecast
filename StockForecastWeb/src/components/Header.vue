<template>
  <el-menu
      router
      active-text-color="white"
      default-active="/"
      mode="horizontal"
      :ellipsis="false"
      background-color="#00000000"
      text-color="white"
  >
    <el-link href="/" class="title" type="primary" :underline="false">大模型股票预测</el-link>
    <el-menu-item index="stockNews">行情</el-menu-item>
    <el-menu-item index="analysis">分析</el-menu-item>
    <el-menu-item index="forecast">预测</el-menu-item>
    <div class="flex-grow"/>
    <el-menu-item @click="toLogin()">{{loginUser}}</el-menu-item>
  </el-menu>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from "axios";
import baseUrls from "@/config/baseUrlConfig";
import {ElMessage, ElMessageBox} from "element-plus";
import {useRouter} from "vue-router";

onMounted(()=>{
  validLogin()
})

const router = useRouter()

const loginUser = ref('登录')

const validLogin = () => {
  const token = localStorage.getItem('token')
  axios.get(`${baseUrls.semantic_kernel_service}/Authentication/valid`, {
    headers: {'Authorization': `Bearer ${token}`}
  }).then((response) => {
    loginUser.value = response.data
    sessionStorage.setItem('isLogin', '1')
  }).catch((e) => {
    ElMessage('请先登录 ' + e)
    sessionStorage.setItem('isLogin', '0')
  })
}

const toLogin = () => {
  const isLogin = sessionStorage.getItem('isLogin') == '1'
  if(isLogin) {
    ElMessageBox.confirm('要退出登录吗？', '提示')
      .then(()=>{
        loginUser.value = '登录'
        sessionStorage.setItem('isLogin', '0')
        localStorage.removeItem('token')
      })
  } else {
    router.push('/login')
  }
}
</script>

<style scoped>
.el-menu {
  border-bottom: 0;
}
.title {
  margin: auto 1em;
  font-size: larger;
  color: white;
}
.flex-grow {
  flex-grow: 1;
}
</style>