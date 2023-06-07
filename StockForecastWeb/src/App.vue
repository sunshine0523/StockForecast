<template>
  <el-container>
    <el-header>
      <Header/>
    </el-header>
    <el-container>
      <el-main>
        <RouterView/>
      </el-main>
    </el-container>
    <el-footer>
      <Footer/>
    </el-footer>
  </el-container>
</template>

<script setup>
import { onMounted } from 'vue'

onMounted(() => {
  //更换主题色
  document.body.style.setProperty('--el-color-primary', '#0A67A3');
  document.body.style.setProperty('--el-color-primary-light-9', '#a5c3e1');
  document.body.style.setProperty('--el-color-primary-light-3', '#65A6D1');
})
</script>

<style scoped lang="scss">
.common-layout {
  .el-header,
  .el-footer,
  .el-main {
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .el-header,
  .el-footer {
    text-align: center;
  }

  .el-main {
    height: 500px;
  }
}
</style>