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
        updateStockEcharts()
      })
      .catch((e)=>{
        ElMessage('获取信息时出现问题 ' + e)
      })
      .finally(()=>{
        getStockDailyLoading.value = false
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

  return {
    categoryData: categoryData,
    values: values,
    volumes: volumes
  };
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
      data: ['日K']
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
        name: '日K',
        type: 'candlestick',
        data: data.values,
        itemStyle: {
          color: '#ff0000',
          color0: '#009f31',
          borderColor: undefined,
          borderColor0: undefined
        },
        tooltip: {
          formatter: function (param) {
            param = param[0];
            return [
              'Date: ' + param.name + '<hr size=1 style="margin: 3px 0">',
              'Open: ' + param.data[0] + '<br/>',
              'Close: ' + param.data[1] + '<br/>',
              'Lowest: ' + param.data[2] + '<br/>',
              'Highest: ' + param.data[3] + '<br/>'
            ].join('');
          }
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