<template>
  <h1 class="title">大语言模型股票走势预测程序</h1>
  <div>
    <el-carousel height="450px" style="width: 80%; margin: 0 10%">
      <el-carousel-item v-for="image in imageList" :key="image">
        <el-card>
          <el-image style="width: 100%; height: 100%" :src="image" />
        </el-card>
      </el-carousel-item>
    </el-carousel>
  </div>

</template>

<script setup lang="ts">
const imageList = [
    'fx.png',
    'hq.png',
    'yc.png'
]
</script>

<style scoped>
.title {
  text-align: center;
  font-size: x-large;
  margin-bottom: 32px;
}
</style>