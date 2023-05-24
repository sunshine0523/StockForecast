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

<script setup lang="ts">
import {RouterView} from 'vue-router'
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
    //background-color: var(--el-color-primary-light-7);
    color: var(--el-text-color-primary);
    text-align: center;
  }

  .el-main {
    //background-color: var(--el-color-primary-light-9);
    color: var(--el-text-color-primary);
    text-align: center;
  }
}
</style>