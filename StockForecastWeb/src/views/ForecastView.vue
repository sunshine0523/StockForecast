<template>
  <h1 class="title">走势预测</h1>
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
    <div class="current-div">
      <el-card>
        <template #header>
          <div class="card-header">
            <h3>实时信息</h3>
            <el-button
                text
                type="primary"
                :loading="getStockCurInfoLoading"
                @click="getStockCurInfo"
            >刷新
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
    <div class="chart-div">
      <el-card>
        <template #header>
          <div class="card-header">
            <h3>行情和预测</h3>
          </div>
        </template>
        <div style="margin-bottom: 8px">
          从
          <el-select v-model="forecastDaysCount" class="m-2" placeholder="预测天数" @change="getStockDaily">
            <el-option
                v-for="item in forecastDaysList"
                :key="item"
                :label="item"
                :value="item"
            />
          </el-select>
          天前开始预测
        </div>
        <div id="stockDailyEcharts" :style="{ width: '100%', height: '500px'}"/>
      </el-card>
    </div>
    <div class="chart-div">
      <el-card>
        <template #header>
          <div class="card-header">
            <h3>分时</h3>
            <el-button
                text
                type="primary"
                :loading="getStockMinuteLoading"
                @click="getStockMinute"
            >刷新
            </el-button>
          </div>
        </template>
        <div id="stockMinuteEcharts" :style="{ width: '100%', height: '500px' }"/>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import {onMounted, ref} from "vue";
import {validLogin} from "@/utils/valid_utils"
import {useRouter} from "vue-router";
import axios from "axios";
import baseUrls from "@/config/baseUrlConfig";
import {ElMessage} from "element-plus";
import * as echarts from "echarts";

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
const getStockCurInfoLoading = ref(false)
const getStockMinuteLoading = ref(false)
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
//预测股票的天数，是从过去n天开始，不是未来n天
const forecastDaysList = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
const forecastDaysCount = ref(5)
//预测的收盘价格，通过getForecast计算
let forecastClosePrice = 0

let minuteChart, dailyChart

onMounted(()=>{
  if (!validLogin()) router.push('/login')

  minuteChart = echart.init(document.getElementById("stockMinuteEcharts"));
  dailyChart = echart.init(document.getElementById("stockDailyEcharts"));
  window.addEventListener('resize',function(){
    dailyChart.resize()
    minuteChart.resize()
  })
})

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
  getStockCurInfo()
  getStockDaily()
}

const getStockDaily = () => {
  axios.get(`${baseUrls.crawler}/getStockDailyList?stock_code=${selectStock.value}`)
      .then((response) => {
        stockDailyList.value = response.data.data
        getLastDaysScore(forecastDaysCount.value)
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
        updateStockMinuteEcharts()
      })
}

//获取过去day_count-1天+未来一天的股票情绪分数
const getLastDaysScore = (day_count: number) => {
  //在计算均线前，先获取最新一日的新闻情绪分数
  axios.get(`${baseUrls.crawler}/getLastDaysDailyNewsEmotionScoreList?stock_code=${selectStock.value}&days_count=${day_count}`)
      .then((response) => {
        lastDaysScoreList.value = response.data.data
      })
      .catch((e)=>{
        ElMessage('获取情绪分数时出现问题 ' + e)
      })
      .finally(()=>{
        updateStockDailyEcharts()
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

const splitDailyData = () => {
  const rawData = stockDailyList.value
  let categoryData = [];
  let values = [];
  let volumes = [];
  for (let i = 0; i < rawData.length; i++) {
    categoryData.push(rawData[i].trade_date);
    let value = []
    value.push(rawData[i].open)
    value.push(rawData[i].close)
    value.push(rawData[i].low)
    value.push(rawData[i].high)
    value.push(rawData[i].vol)
    values.push(value);
    volumes.push(rawData[i].vol)
  }
  volumes.push('-')
  return {
    categoryData: categoryData,
    values: values,
    volumes: volumes
  };
}

const splitMinuteData = () => {
  const rawData = stockMinuteList.value.data
  let times = []
  let values = []
  let volumes = []
  for (let i = 0; i < rawData.length; i++) {
    let splitData = rawData[i].split(' ')
    times.push(splitData[0])
    values.push(splitData[1])
    volumes.push(splitData[2])
  }
  return {
    times: times,
    values: values,
    volumes: volumes
  }
}

// 用于计算均线的函数
function calculateMA(dayCount, data) {
  const result = [];
  for (let i = 0, len = data.values.length; i < len; i++) {
    if (i < dayCount) {
      result.push('-');
      continue;
    }
    let sum = 0;
    for (let j = 0; j < dayCount; j++) {
      sum += data.values[i - j][1];
    }
    result.push(+(sum / dayCount).toFixed(3));
  }
  return result;
}

function getForecast(data, day_count) {
  let curTime = new Date()
  let today = curTime.getFullYear() + '' + (curTime.getMonth() + 1).toString().padStart(2, '0') + '' + (curTime.getDate()).toString().padStart(2, '0')
  let ma1 = calculateMA(1, data)
  const result = [];
  for (let i = 0, len = data.values.length; i < len - day_count; ++i) {
    result.push('-');
  }
  result.push(ma1[ma1.length - day_count])
  for (let i = day_count; i > 0; --i) {
    result.push(result[result.length - 1] + lastDaysScoreList.value[day_count - i].score)
    if (lastDaysScoreList.value[day_count - i].date === today) {
      forecastClosePrice = result[result.length - 1]
    }
  }
  return result
}

//给分时数据表返回预测数据
function getForecastForMinute() {
  let result = []
  let begin = parseFloat(stockMinuteList.value['qt'][5])
  let end = forecastClosePrice
  let length = stockMinuteList.value['data'].length
  //240是4h 240min
  let diff = (end - begin) / 240
  for (let i = 0; i <= length - 1; ++i) {
    let value = begin + i * diff
    result.push(value)
  }
  return result
}

const updateStockDailyEcharts = () => {
  const data = splitDailyData()

  // 把配置和数据放这里
  dailyChart.setOption({
    title: [
      {
        left: 'left',
        text: '股票K线图'
      },
      {
        top: '65%',
        left: 'left',
        text: '成交量'
      }
    ],
    animation: false,
    legend: {
      left: 'center',
      data: ['日K', '收盘价', '预测']
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      },
      borderWidth: 1,
      borderColor: '#ccc',
      padding: 10,
      textStyle: {
        color: '#000'
      },
      position: function (pos, params, el, elRect, size) {
        const obj = {
          top: 10
        };
        obj[['left', 'right'][+(pos[0] < size.viewSize[0] / 2)]] = 30;
        return obj;
      }
      // extraCssText: 'width: 170px'
    },
    axisPointer: {
      link: [
        {
          xAxisIndex: 'all'
        }
      ],
      label: {
        backgroundColor: '#777'
      }
    },
    visualMap: {
      show: false,
      seriesIndex: 5,
      dimension: 2,
      pieces: [
        {
          value: 1,
          color: '#009f31'
        },
        {
          value: -1,
          color: '#ff0000'
        }
      ]
    },
    grid: [
      {
        left: '10%',
        right: '8%',
        height: '50%'
      },
      {
        left: '10%',
        right: '8%',
        top: '63%',
        height: '16%'
      }
    ],
    xAxis: [
      {
        type: 'category',
        data: data.categoryData,
        boundaryGap: false,
        axisLine: { onZero: true },
        axisTick: { show: true },
        splitLine: { show: false },
        axisLabel: { show: false },
        min: 'dataMin',
        max: 'dataMax',
        axisPointer: {
          z: 100
        }
      },
      {
        type: 'category',
        gridIndex: 1,
        data: data.categoryData,
        boundaryGap: false,
        axisLine: { onZero: true },
        axisTick: { show: true },
        splitLine: { show: false },
        axisLabel: { show: true },
        min: 'dataMin',
        max: 'dataMax'
      }
    ],
    yAxis: [
      {
        scale: true,
        splitArea: {
          show: true
        }
      },
      {
        scale: true,
        gridIndex: 1,
        splitNumber: 2,
        axisLabel: { show: false },
        axisLine: { show: false },
        axisTick: { show: false },
        splitLine: { show: false }
      }
    ],
    dataZoom: [
      {
        type: 'inside',
        xAxisIndex: [0, 1],
        start: 90,
        end: 100
      },
      {
        show: true,
        xAxisIndex: [0, 1],
        type: 'slider',
        top: '85%',
        start: 0,
        end: 100
      }
    ],
    series: [
      {
        name: '日K',
        type: 'candlestick',
        data: data.values,
        itemStyle: {
          color: '#ff0000',
          color0: '#009f31',
          borderColor: undefined,
          borderColor0: undefined
        },
      },
      {
        name: '收盘价',
        type: 'line',
        data: calculateMA(1, data),
        smooth: true,
        lineStyle: {
          opacity: 1
        }
      },
      {
        name: '预测',
        type: 'line',
        data: getForecast(data, forecastDaysCount.value),
        smooth: true,
        lineStyle: {
          opacity: 1,
          type: 'dotted'
        },
      },
      {
        name: '成交量',
        type: 'bar',
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: data.volumes
      },
    ]
  });
}

const updateStockMinuteEcharts = () => {
  const data = splitMinuteData()

  // 把配置和数据放这里
  minuteChart.setOption({
    title: [
      {
        left: 'left',
        text: '分时图'
      },
      {
        top: '65%',
        left: 'left',
        text: '成交量'
      }
    ],
    animation: false,
    legend: {
      left: 'center',
      data: ['分时', '预测']
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      },
      borderWidth: 1,
      borderColor: '#ccc',
      padding: 10,
      textStyle: {
        color: '#000'
      },
      position: function (pos, params, el, elRect, size) {
        const obj = {
          top: 10
        };
        obj[['left', 'right'][+(pos[0] < size.viewSize[0] / 2)]] = 30;
        return obj;
      }
      // extraCssText: 'width: 170px'
    },
    axisPointer: {
      link: [
        {
          xAxisIndex: 'all'
        }
      ],
      label: {
        backgroundColor: '#777'
      }
    },
    grid: [
      {
        left: '10%',
        right: '8%',
        height: '50%'
      },
      {
        left: '10%',
        right: '8%',
        top: '63%',
        height: '16%'
      }
    ],
    xAxis: [
      {
        type: 'category',
        data: data.times,
        boundaryGap: false,
        axisLine: { onZero: true },
        axisTick: { show: true },
        splitLine: { show: false },
        axisLabel: { show: false },
        min: 'dataMin',
        max: 'dataMax',
        axisPointer: {
          z: 100
        }
      },
      {
        type: 'category',
        gridIndex: 1,
        data: data.times,
        boundaryGap: false,
        axisLine: { onZero: true },
        axisTick: { show: true },
        splitLine: { show: false },
        axisLabel: { show: true },
        min: 'dataMin',
        max: 'dataMax'
      }
    ],
    yAxis: [
      {
        scale: true,
        splitArea: {
          show: true
        },
      },
      {
        scale: true,
        gridIndex: 1,
        splitNumber: 2,
        axisLabel: { show: false },
        axisLine: { show: false },
        axisTick: { show: false },
        splitLine: { show: false }
      },
    ],
    dataZoom: [
      {
        type: 'inside',
        xAxisIndex: [0, 1],
        start: 0,
        end: 100
      },
      {
        show: true,
        xAxisIndex: [0, 1],
        type: 'slider',
        top: '85%',
        start: 0,
        end: 100
      }
    ],
    series: [
      {
        name: '分时',
        type: 'line',
        data: data.values,
        //基准线
        markLine: {
          symbol: 'none',
          data: [
            {
              yAxis: stockMinuteList.value['qt'][5],
              name: "今日开盘价",
              lineStyle: {
                // type: "solid",
                color: "#FA6400",
                // width: 2,
              },
              label: {
                position: "end",
                fontSize: 14,
                formatter: "今日开盘价",
              },
            }
          ]
        }
      },
      {
        name: '预测',
        type: 'line',
        data: getForecastForMinute(),
        lineStyle: {
          opacity: 1,
          type: 'dotted'
        },
      },
      {
        name: '成交量',
        type: 'bar',
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: data.volumes
      },
    ]
  });
}

</script>

<style scoped>
.title {
  text-align: center;
  font-size: x-large;
}
.content {
  text-align: center;
  min-height: 400px;
}
.stock-select {
  margin-top: 16px;
  width: 80%;
}
.current-div,
.chart-div {
  margin-left: 10%;
  margin-right: 10%;
  margin-top: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>