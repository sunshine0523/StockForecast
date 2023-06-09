<template>
  <div class="header-div"/>
  <h1 class="title">{{selectStockName}}  行情分析 </h1>
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
    >
      <el-option
          v-for="item in stockList"
          :key="item.ts_code"
          :label="`${item.ts_code} ${item.name}`"
          :value="item.ts_code"
      />
    </el-select>
    <el-tabs v-model="activeAnalysisType" @tab-change="onTabChanged" style="margin-top: 16px">
      <el-tab-pane label="基础情感分析" name="1">
        <AnalysisEmotionView
            ref="analysisEmotionView"
            :select-stock="selectStock"
            v-model:select-stock-name="selectStockName"
        />
      </el-tab-pane>
      <el-tab-pane label="情感分数分析(Beta)" name="2">
        <AnalysisEmotionScoreView
            ref="analysisEmotionScoreView"
            :select-stock="selectStock"
            v-model:select-stock-name="selectStockName"
        />
      </el-tab-pane>
    </el-tabs>
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
import AnalysisEmotionView from "@/views/analysis/AnalysisEmotionView.vue";
import AnalysisEmotionScoreView from "@/views/analysis/AnalysisEmotionScoreView.vue";

const router = useRouter()

const analysisEmotionView = ref()
const analysisEmotionScoreView = ref()

//分析类型标签
const activeAnalysisType = ref('1')

const stockList = ref<string[]>([])
const selectStock = ref('')
const selectStockName = ref('')
const getStockLoading = ref(false)

onMounted(()=>{
  if (!validLogin()) router.push('/login')

  //设置默认展示的股票
  let stockCode = sessionStorage.getItem('stockCode')

  if (null != stockCode) {
    selectStock.value = stockCode
  }
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

const onTabChanged = () => {
  if ('1' === activeAnalysisType.value) {
    analysisEmotionView.value?.getStockNewsCount(selectStock.value)
  }
  else if ('2' === activeAnalysisType.value) {
    analysisEmotionScoreView.value?.getStockNewsCount(selectStock.value)
  }
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
  width: 75%;
}
.analysis-button {
  margin-top: 16px;
  margin-left: 12px;
}
</style>