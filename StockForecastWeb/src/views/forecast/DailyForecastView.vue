<template>
  <div class="chart-div">
    <el-card>
      <template #header>
        <div class="card-header">
          <h3><i-ep-trend-charts class="text-icon"/>&nbsp;日K信息</h3>
          <el-button text @click="router.push('/stockNews')"><i-ep-arrow-left/>&nbsp;更新新闻</el-button>
        </div>
      </template>
      <div id="stockDailyEcharts" :style="{ width: '100%', height: '500px'}"/>
    </el-card>
  </div>
</template>

<script lang="ts">
import {defineComponent} from "vue"
export default defineComponent({
  props: {

  },
})
</script>
<script setup lang="ts">
import {useRouter} from "vue-router";
import {defineEmits, ref} from 'vue'

const emit = defineEmits(['getStockDaily'])

const router = useRouter()
</script>
<style scoped lang="sass">
@import "@/assets/forecast.sass"
</style>