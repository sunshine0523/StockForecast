<template>
  <div class="chart-div">
    <el-card>
      <template #header>
        <div class="card-header">
          <h3><i-ep-histogram class="text-icon"/>&nbsp;变化趋势</h3>
          <el-button text></el-button>
          <el-button text @click="detailInfoDrawer = true"><i-ep-more/>&nbsp;详细信息</el-button>
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
  <el-drawer
      v-model="detailInfoDrawer"
      title="详细预测信息"
      direction="rtl"
      size="33%"
  >
    <div style="text-align: left">
      <el-table :data="lastDaysScoreList">
        <el-table-column property="date" label="日期" width="150" />
        <el-table-column property="score" label="分数" width="200" />
      </el-table>
    </div>
  </el-drawer>
</template>

<script lang="ts">
import {defineComponent} from "vue"
export default defineComponent({
  props: {
    forecastClosePrice: {},
    forecastChangedPrice: {},
    newsTypeRadio: {},
    curPrice: {},
    lastDaysScoreList: {}
  },
})
</script>
<script setup lang="ts">
import {useRouter} from "vue-router";
import {defineEmits, ref} from 'vue'

const emit = defineEmits(['getStockDaily'])

const router = useRouter()

const detailInfoDrawer = ref(false)
</script>
<style scoped lang="sass">
@import "@/assets/forecast.sass"
</style>