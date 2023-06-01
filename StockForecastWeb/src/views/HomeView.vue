<template>
  <div class="image-div">
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
.image-div {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 10rem;
  z-index: -1;
}
</style>