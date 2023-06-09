<template>
  <div class="chart-div">
    <el-card>
      <template #header>
        <div class="card-header">
          <h3><i-ep-camera-filled class="text-icon"/>&nbsp;分时信息</h3>
          <el-button
              text
              :loading="getStockMinuteLoading"
              @click="getStockMinute"
          ><i-ep-refresh/>&nbsp;刷新
          </el-button>
        </div>
      </template>
      <div id="stockMinuteEcharts" :style="{ width: '100%', height: '500px' }"/>
    </el-card>
  </div>
</template>

<script lang="ts">
import {defineComponent} from "vue"
export default defineComponent({
  props: {
    getStockMinuteLoading: {}
  },
})
</script>

<script setup lang="ts">
import {defineEmits} from 'vue'

const emit = defineEmits(['getStockMinute'])

const getStockMinute = ()=>{
  emit('getStockMinute')
}
</script>

<style scoped lang="sass">
@import "@/assets/forecast.sass"
</style>