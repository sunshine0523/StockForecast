<template>
  <div class="header-div"/>
  <h1 class="title">{{selectStockInfo.name}} 走势预测 </h1>
  <div class="content">
    <el-select
        v-model="selectStock"
        filterable
        remote
        reserve-keyword
        placeholder="支持中英文上市公司名称、股票代码或公司名称缩写搜索"
        remote-show-suffix
        :remote-method="getStockList"
        :loading="getStockLoading"
        class="stock-select"
        size="large"
        @change="onSelectStock"
    >
      <el-option
          v-for="item in stockList"
          :key="item.ts_code"
          :label="`${item.ts_code} ${item.name}`"
          :value="item.ts_code"
      />
    </el-select>
    <el-row>
      <el-col :span="4">
        <el-affix :offset="260">
          <el-card class="cloudy-knoxville-bg">
            <template #header>
              <h3 style="text-align: center; color: red">猜你喜欢</h3>
            </template>
            <div v-for="stock in favoriteStockList" style="margin-top: 5px">
              <el-link @click="selectStock=stock.stock_code;onSelectStock()" style="color: #282828">{{stock.stock_code}} {{stock.name}}</el-link>
            </div>
          </el-card>
        </el-affix>
      </el-col>
      <el-col :span="16">
        <div class="forecast-option">
          <div/>
          <div>
            从
            <el-select
                v-model="forecastDaysCount"
                placeholder="预测天数"
                @change="getStockDaily(forecastDaysCount, newsTypeRadio)"
                style="width: 64px;"
            >
              <el-option
                  v-for="item in forecastDaysList"
                  :key="item"
                  :label="item"
                  :value="item"
              />
            </el-select>
            天前开始预测
          </div>
          <div>
            <el-radio-group v-model="newsTypeRadio" @change="getStockDaily(forecastDaysCount, newsTypeRadio)">
              <el-radio label="-1" size="large">全部</el-radio>
              <el-radio label="1" size="large">新浪财经</el-radio>
              <el-radio label="2" size="large">股吧</el-radio>
            </el-radio-group>
          </div>
          <div/>
        </div>
        <CurrentView
            :select-stock-cur-info="selectStockCurInfo"
            :get-stock-cur-info-loading="getStockCurInfoLoading"
            @getStockCurInfo="getStockCurInfo"
        />
        <TrendPredictionView
            :forecast-changed-price="forecastChangedPrice"
            :forecast-close-price="forecastClosePrice"
            :cur-price="selectStockCurInfo.cur_price"
            @getStockDaily="getStockDaily"
        />
        <DailyForecastView @getStockDaily="getStockDaily"/>
        <MinuteView
          :get-stock-minute-loading="getStockMinuteLoading"
          @getStockMinute="getStockMinute"
        />
      </el-col>
      <el-col :span="4">
        <el-card class="tip-card cloudy-knoxville-bg">
          <template #header>
            <h3 style="text-align: center"><i-ep-info-filled/>小贴士</h3>
          </template>
          <p>1.程序根据<i>新闻情绪</i>来预测股票涨跌。预测规则：程序在前一天收盘价的基础上，通过要预测的交易日和其前一日内的新闻情绪加权分数，以给出预测交易日的股票价格</p>
          <p>2.预测有风险，投资需谨慎</p>
        </el-card>
        <el-card class="info-card premium-white-bg">
          <template #header>
            <h3 style="text-align: center"><i-ep-info-filled/>股票信息</h3>
          </template>
          <div style="text-align: start">
            <p><span style="font-weight: bold">名称：</span>{{selectStockInfo.name}}</p>
            <p><span style="font-weight: bold">全称：</span>{{selectStockInfo.fullname}}</p>
            <p><span style="font-weight: bold">英文名称：</span>{{selectStockInfo.enname}}</p>
            <p><span style="font-weight: bold">行业：</span>{{selectStockInfo.industry}}</p>
            <p><span style="font-weight: bold">上市日期：</span>{{selectStockInfo.list_date}}</p>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
  <el-backtop :right="100" :bottom="100" />
</template>

<script setup lang="ts">
import {onMounted, ref} from "vue";
import {validLogin} from "@/utils/valid_utils"
import {useRouter} from "vue-router";
import axios from "axios";
import baseUrls from "@/config/baseUrlConfig";
import {ElMessage} from "element-plus";
import * as echarts from "echarts";
import {
  updateStockDailyEcharts,
  updateStockMinuteEcharts,
  updateTrendPredictionEcharts
} from "@/views/forecast/forecast";
import CurrentView from "@/views/forecast/CurrentView.vue";
import DailyForecastView from "@/views/forecast/DailyForecastView.vue";
import MinuteView from "@/views/forecast/MinuteView.vue";
import TrendPredictionView from "@/views/forecast/TrendPredictionView.vue";

interface StockDaily {
  ts_code
  trade_date
  open
  high
  low
  close
  pre_close
  change
  pct_chg
  vol
  amount
}

const router = useRouter()

let echart = echarts;

const stockList = ref<string[]>([])
const selectStock = ref('')
const getStockLoading = ref(false)
const stockDailyList = ref<StockDaily[]>([])
const getStockMinuteLoading = ref(false)
const getStockCurInfoLoading = ref(false)
const lastDaysScoreList = ref([])
//选定的股票的当前信息
const selectStockCurInfo = ref({
  cur_price: '-',
  last_close: '-',
  max_price: '-',
  min_price: '-',
  request_time: '-',
  rise_or_fall: '-',
  rise_or_fall_ratio: '-',
  stock_code: '-',
  today_open: '-',
  volume: '-'
})
const stockMinuteList = ref({})

//预测的收盘价格，通过getForecast计算
const forecastClosePrice = ref(0)
//预测价格相对上一交易日的变化
const forecastChangedPrice = ref(0)
//猜你喜欢列表
const favoriteStockList = ref([])
const selectStockInfo = ref({})
let trendPredictionChart, minuteChart, dailyChart

const forecastDaysCount = ref(5)
//新闻来源
const newsTypeRadio = ref('-1')
//预测股票的天数，是从过去n天开始，不是未来n天
const forecastDaysList = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

onMounted(()=>{
  if (!validLogin()) router.push('/login')

  trendPredictionChart = echart.init(document.getElementById('trendPredictionEcharts'))
  minuteChart = echart.init(document.getElementById("stockMinuteEcharts"));
  dailyChart = echart.init(document.getElementById("stockDailyEcharts"));
  window.addEventListener('resize',function(){
    trendPredictionChart.resize()
    dailyChart.resize()
    minuteChart.resize()
  })
  getFavoriteStockList()

  //设置默认展示的股票
  let stockCode = sessionStorage.getItem('stockCode')
  if (null != stockCode) {
    selectStock.value = stockCode
    getStockInfo()
    getStockCurInfo()
    getStockDaily(forecastDaysCount.value, newsTypeRadio.value)
  }
})

const getStockInfo = () => {
  axios.get(`${baseUrls.crawler}/getStockInfo?stock_code=${selectStock.value}`)
      .then((res)=>{
        selectStockInfo.value = res.data.data
        sessionStorage.setItem('stockName', selectStockInfo.value['name'])
      })
}

const getFavoriteStockList = () => {
  axios.get(`${baseUrls.crawler}/getFavoriteStockList`)
      .then((response) => {
        favoriteStockList.value = response.data.data
      })
      .catch((e)=>{
        ElMessage('获取猜你喜欢列表时出现问题 ' + e)
      })
}

const getStockList = (query: string) => {
  if (query == '') return
  getStockLoading.value = true
  axios.get(`${baseUrls.crawler}/getStockList?query=${query}`)
      .then((response) => {
        stockList.value = response.data.data
      })
      .catch((e)=>{
        ElMessage('获取信息时出现问题 ' + e)
      })
      .finally(()=>{
        getStockLoading.value = false
      })
}

const onSelectStock = () => {
  sessionStorage.setItem('stockCode', selectStock.value)
  getStockInfo()
  getStockCurInfo()
  getStockDaily(forecastDaysCount.value, newsTypeRadio.value)
}

const getStockDaily = (forecastDaysCount, newsType) => {
  axios.get(`${baseUrls.crawler}/getStockDailyList?stock_code=${selectStock.value}`)
      .then((response) => {
        stockDailyList.value = response.data.data
        getLastDaysScore(forecastDaysCount, newsType)
      })
      .catch((e)=>{
        ElMessage('获取信息时出现问题 ' + e)
      })
}

const getStockMinute = () => {
  getStockMinuteLoading.value = true
  axios.get(`${baseUrls.crawler}/getStockMinuteList?stock_code=${selectStock.value}`)
      .then((response) => {
        stockMinuteList.value = response.data.data
      })
      .catch((e)=>{
        ElMessage('获取分时时出现问题 ' + e)
      })
      .finally(()=>{
        getStockMinuteLoading.value = false
        updateStockMinuteEcharts(minuteChart, stockMinuteList, forecastClosePrice)
      })
}

//获取过去forecastDaysCount-1天+未来一天的股票情绪分数
const getLastDaysScore = (forecastDaysCount: number, newsType: string) => {
  //在计算均线前，先获取最新一日的新闻情绪分数
  axios.get(`${baseUrls.crawler}/getLastDaysDailyNewsEmotionScoreList?stock_code=${selectStock.value}&days_count=${forecastDaysCount}&news_type=${newsType}`)
      .then((response) => {
        lastDaysScoreList.value = response.data.data
      })
      .catch((e)=>{
        ElMessage('获取情绪分数时出现问题 ' + e)
      })
      .finally(()=>{
        forecastChangedPrice.value = lastDaysScoreList.value[lastDaysScoreList.value.length - 1].score.toFixed(2)
        updateStockDailyEcharts(dailyChart, stockDailyList, forecastDaysCount, lastDaysScoreList, forecastClosePrice)
        updateTrendPredictionEcharts(trendPredictionChart, lastDaysScoreList, stockDailyList)
        getStockMinute()
      })
}

const getStockCurInfo = () => {
  getStockCurInfoLoading.value = true
  axios.get(`${baseUrls.crawler}/getStockCurrentInfo?stock_code=${selectStock.value}`)
      .then((response) => {
        selectStockCurInfo.value = response.data.data
      })
      .catch((e)=>{
        ElMessage('获取股票实时信息时出现问题 ' + e)
      })
      .finally(()=>{
        getStockCurInfoLoading.value = false
      })
}
</script>

<style scoped>
.title {
  text-align: center;
  font-size: x-large;
  color: white;
  font-weight: bold;
}
.content {
  text-align: center;
  min-height: 400px;
}
.stock-select {
  margin-top: 16px;
  width: 80%;
}
.tip-card {
  margin-top: 75px;
  text-align: start;
}
.info-card {
  margin-top: 16px;
}
.el-card {
  border-radius: 16px;
}
.forecast-option {
  margin-top: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>