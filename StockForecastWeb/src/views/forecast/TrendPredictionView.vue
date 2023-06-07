<template>
  <div class="chart-div">
    <el-card>
      <template #header>
        <div class="card-header">
          <h3>变化趋势</h3>
        </div>
      </template>
      <div style="margin: 12px">
        <p style="font-weight: bold">预计下个交易日收盘价为<span style="font-size: x-large">{{forecastClosePrice}}</span>元，相对本交易日收盘价变化了<span style="font-size: x-large">{{forecastChangedPrice}}</span>元。</p>
        <p style="font-weight: bold">当前价格为<span style="font-size: x-large">{{curPrice}}</span>元，与预测收盘价格相差<span style="font-size: x-large">{{Math.abs(forecastClosePrice-curPrice).toFixed(2)}}</span>元。</p>
      </div>
      <div id="trendPredictionEcharts" :style="{ width: '100%', height: '300px'}"/>
      <div style="text-align: right; margin-top: 12px">
        <p style="font-size: small; color: gray">* 图表中数字仅反应趋势，不代表实际价格</p>
      </div>
    </el-card>
  </div>
</template>

<script lang="ts">
import {defineComponent} from "vue"
export default defineComponent({
  props: {
    forecastClosePrice: {},
    forecastChangedPrice: {},
    newsTypeRadio: {},
    curPrice: {}
  },
})
</script>
<script setup lang="ts">
import {useRouter} from "vue-router";
import {defineEmits, ref} from 'vue'

const emit = defineEmits(['getStockDaily'])

const router = useRouter()
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