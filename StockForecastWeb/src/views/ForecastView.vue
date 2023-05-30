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
    <div class="news_option" v-show="getStockNewsDone">
      <el-button type="primary" :loading="refreshStockNews" @click="refreshStockNewsFunc"><i-ep-refresh/>&nbsp;刷新</el-button>
    </div>
    <div class="chart-container">
      <div id="stockEcharts" :style="{ width: '100%', height: '500px' }"></div>
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
const stockDailyList = ref([])
const getStockDailyLoading = ref(false)
const lastDaysScoreList = ref([])
//预测股票的天数，是从过去n天开始，不是未来n天
let forecastDaysCount = 3

onMounted(()=>{
  if (!validLogin()) router.push('/login')
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
  getStockDaily()
}

const getStockDaily = () => {
  getStockDailyLoading.value = true
  axios.get(`${baseUrls.crawler}/getStockDailyList?stock_code=${selectStock.value}`)
      .then((response) => {
        stockDailyList.value = response.data.data
        getLastDaysScore(stockDailyList.value[stockDailyList.value.length - 1].trade_date, forecastDaysCount)
      })
      .catch((e)=>{
        ElMessage('获取信息时出现问题 ' + e)
      })
      .finally(()=>{
        getStockDailyLoading.value = false
      })
}

const getLastDaysScore = (end_date: string, day_count: number) => {
  //在计算均线前，先获取最新一日的新闻情绪分数
  axios.get(`${baseUrls.crawler}/getLastDaysDailyNewsEmotionScoreList?stock_code=${selectStock.value}&end_date=${end_date}&days_count=${day_count}`)
      .then((response) => {
        lastDaysScoreList.value = response.data.data
      })
      .catch((e)=>{
        ElMessage('获取情绪分数时出现问题 ' + e)
      })
      .finally(()=>{
        updateStockEcharts()
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
  let ma1 = calculateMA(1, data)
  const result = [];
  for (let i = 0, len = data.values.length; i < len - day_count; ++i) {
    result.push('-');
  }
  result.push(ma1[ma1.length - day_count])
  for (let i = day_count; i > 0; --i) {
    result.push(result[result.length - 1] + lastDaysScoreList.value[day_count - i].score)
  }
  return result
}

const updateStockEcharts = () => {
  const data = splitDailyData()
  let chart = echart.init(document.getElementById("stockEcharts"));
  // 把配置和数据放这里
  chart.setOption({
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
        data: getForecast(data, forecastDaysCount),
        smooth: true,
        lineStyle: {
          opacity: 1,
          type: 'dotted'
        }
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
  window.onresize = function() {
    //自适应大小
    chart.resize();
  };
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
.news_option {
  text-align: end;
  margin-right: 10%;
  margin-top: 20px;
}
.chart-container {
  margin-left: 10%;
  margin-right: 10%;
  margin-top: 20px;
}
</style>