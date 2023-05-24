<template>
  <el-menu
    router
    :default-active=activeIndex
    mode="horizontal"
    @select="handleSelect"
    :ellipsis="false"
  >
    <a href="/" class="title">大模型股票预测</a>
    <el-menu-item index="test1">首页</el-menu-item>
    <el-menu-item index="test">测试</el-menu-item>
    <div class="flex-grow"/>
    <el-menu-item index="login">登录</el-menu-item>
  </el-menu>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const activeIndex = ref('index')

const handleSelect = (key: string, keyPath: string[]) => {
  console.log(key, keyPath)
}
</script>

<style scoped>
.title {
  margin: auto 1em;
  font-size: larger;
}
.flex-grow {
  flex-grow: 1;
}
</style>