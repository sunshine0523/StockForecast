<template>
  <div class="chart-div">
    <el-card>
      <template #header>
        <div class="card-header">
          <h3>分时信息</h3>
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

<style scoped>
.chart-div {
  margin-left: 5%;
  margin-right: 5%;
  margin-top: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #0A67A3;
}
.el-card {
  border-radius: 16px;
}
</style>