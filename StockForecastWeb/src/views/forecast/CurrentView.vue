<template>
  <div class="current-div">
    <el-card>
      <template #header>
        <div class="card-header">
          <h3><i-ep-list class="text-icon"/>&nbsp;实时信息</h3>
          <el-button
              text
              :loading="getStockCurInfoLoading"
              @click="getStockCurInfo"
          ><i-ep-refresh/>&nbsp;刷新
          </el-button>
        </div>
      </template>
      <el-row>
        <el-col :span="6">
          <div v-if="selectStockCurInfo.rise_or_fall > 0">
            <el-statistic
                title="当前价格"
                :value="selectStockCurInfo.cur_price"
                :value-style="{color: 'red'}"
            />
          </div>
          <div v-else>
            <el-statistic
                title="当前价格"
                :value="selectStockCurInfo.cur_price"
                :value-style="{color: 'green'}"
            />
          </div>
        </el-col>
        <el-col :span="6">
          <el-statistic title="昨日收盘" :value="selectStockCurInfo.last_close"/>
        </el-col>
        <el-col :span="6">
          <el-statistic title="今日开盘" :value="selectStockCurInfo.today_open" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="成交量" :value="selectStockCurInfo.volume" />
        </el-col>
      </el-row>
      <el-row style="margin-top: 12px">
        <el-col :span="6">
          <el-statistic title="涨跌额" :value="selectStockCurInfo.rise_or_fall" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="涨跌幅" :value="selectStockCurInfo.rise_or_fall_ratio" suffix="%"/>
        </el-col>
        <el-col :span="6">
          <el-statistic title="最高价" :value="selectStockCurInfo.max_price" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="最低价" :value="selectStockCurInfo.min_price" />
        </el-col>
      </el-row>
      <div style="text-align: right; margin-top: 12px">
        <p style="font-size: small; color: gray">更新于北京时间 {{selectStockCurInfo.request_time}}</p>
      </div>
    </el-card>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue"
export default defineComponent({
  props: {
    selectStockCurInfo: {},
    getStockCurInfoLoading: {}
  },
})
</script>

<script setup lang="ts">
import {defineEmits} from 'vue'
const emit = defineEmits(['getStockCurInfo'])

const getStockCurInfo = ()=>{
  emit('getStockCurInfo')
}
</script>

<style scoped lang="sass">
@import "@/assets/forecast.sass"
</style>