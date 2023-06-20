<template>
  <div class="image-div">
    <el-carousel :height="imageHeight" @change="onCarouselChange" interval="4000">
      <el-carousel-item v-for="image in imageList" :key="image">
        <el-image style="width: 100%" :style="{height: imageHeight}" :src="image" fit="cover" />
      </el-carousel-item>
    </el-carousel>
  </div>
  <div class="introduction-div">
    <p id="introduction-text">{{introductionTextList[index]}}</p>
  </div>
  <div class="introduction-sub-div">
    <p id="introduction-sub-text">{{introductionSubTextList[index]}}</p>
  </div>
</template>

<script setup lang="ts">
import {onMounted, ref} from 'vue'
import img1 from '@/assets/img/01.png'
import img2 from '@/assets/img/02.png'
import img3 from '@/assets/img/03.png'

const imageList = [
    img1,
    img2,
    img3
]

const index = ref(0)

const imageHeight = ref('800px')

const introductionTextList = [
    'GPT, 您的金融顾问',
    '新闻情绪, 传递价值',
    '语言模型, 让预测更简单'
]
const introductionSubTextList = [
    'GPT在背后大量且丰富的语料支持下，已经可以做您可靠的金融顾问。大语言模型股票预测程序使用GPT作为背后支持，可以总结每日新闻情绪、提供金融意见',
    '各大金融平台每天都会产生大量的新闻，我们被信息包围，但可能只是包围。大语言模型股票预测程序将新闻信息分类，让信息拥有更多价值',
    '通过语言模型的支持，大语言模型股票预测程序可以轻松解决从前无法想象的问题。语言模型发挥无限可能'
]

onMounted(()=>{
  imageHeight.value = document.body.clientHeight + 'px'
})

function onCarouselChange(i) {
  index.value = i
  //让文字有从右向左变化的过程
  let introductionText = document.getElementById('introduction-text')
  let introductionSubText = document.getElementById('introduction-sub-text')
}
</script>

<style scoped>
.image-div {
  position: absolute;
  left: 0;
  top: 0;
  width: 100%;
  height: auto;
  z-index: -1;
}
.introduction-div {
  height: 150px;
  display: flex;
  justify-content: center;
  align-items: end;
}
.introduction-sub-div {
  height: 350px;
  display: flex;
  justify-content: center;
  align-items: start;
  margin-top: 10px;
}
#introduction-text {
  font-size: 50px;
  color: white;
}
#introduction-sub-text {
  font-size: 18px;
  color: white;
  max-width: 500px;
  text-align: center;
}
</style>