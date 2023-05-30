<template>
  <h1 class="title">行情分析</h1>
  <div class="content">
    <ul>
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
      <el-button
          type="primary"
          size="large"
          :disabled="selectStock.length === 0"
          class="analysis-button"
          @click="toAnalysis"
          :loading="getStockNewsEmotionLoading"
      >
        分析
      </el-button>
    </ul>
    <div class="time-line">
      <el-skeleton :rows="10" animated :loading="getStockNewsEmotionLoading">
        <template #default>
          <el-empty v-if="stockNewsEmotionList.length === 0" description="还没有相关新闻哦" />
          <el-timeline v-else>
            <el-timeline-item
                v-for="(daily_news, date) in stockNewsEmotionList"
                :key="date"
                :size="'large'"
                :timestamp="date"
                :hollow="true"
                :type="'primary'"
                placement="top"
            >
              <el-card>
                <template #header>
                  <div class="card-header">
                    <h2 style="text-align: center"><i-ep-paperclip/>{{date}} 新闻情绪事迹</h2>
                    <el-button
                        text
                        type="primary"
                        :loading="getDailyNewsEmotionLoading"
                        @click="refreshNewsDailyEmotion(date)"
                    >刷新本日总结
                    </el-button>
                  </div>
                  <p style="margin: 6px;">本日总结：{{ daily_news['daily_emotion'] }}</p>
                </template>
                <div v-for="(news, index) in daily_news['news']" :key="index" class="daily-news-content">
                  <el-link
                    v-if="news.emotion === -1"
                    :href="news.news_link"
                    type="default"
                    target="_blank"
                    style="color: forestgreen"
                  >
                    🙁 {{news.news_title}}<el-text size="small">&nbsp; {{news.news_time}}</el-text>
                  </el-link>
                  <el-link
                    v-if="news.emotion === 1"
                    :href="news.news_link"
                    type="default"
                    target="_blank"
                    style="color: red"
                  >
                    😊 {{news.news_title}}<el-text size="small">&nbsp; {{news.news_time}}</el-text>
                  </el-link>
                </div>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </template>
      </el-skeleton>
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

const router = useRouter()

const stockList = ref<string[]>([])
const selectStock = ref('')
const getStockLoading = ref(false)
const getStockNewsEmotionLoading = ref(false)
const stockNewsEmotionList = ref([])
const getDailyNewsEmotionLoading = ref(false)

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

const toAnalysis = () => {
  const token = localStorage.getItem('token')
  getStockNewsEmotionLoading.value = true

  axios.post(`${baseUrls.semantic_kernel_service}/SemanticKernel/skills/StockSkill/invoke/AnalysisStockNews`,
  {
    'value': selectStock.value,
    'inputs': []
  },{
        headers: {'Authorization': `Bearer ${token}`},
  }).then((response) => {
    getStockNewsEmotionList()
  }).catch((e) => {
    ElMessage('分析失败 ' + e)
    getStockNewsEmotionLoading.value = false
  })
}

//获取新闻情绪列表
const getStockNewsEmotionList = () => {
  axios.get(`${baseUrls.crawler}/getStockNewsEmotionList?stock_code=${selectStock.value}`)
      .then((response) => {
        stockNewsEmotionList.value = response.data.data
      })
      .catch((e)=>{
        ElMessage('获取新闻情绪信息时出现问题 ' + e)
      })
      .finally(()=>{
        getStockNewsEmotionLoading.value = false
      })
}

const refreshNewsDailyEmotion = (day: number) => {
  const token = localStorage.getItem('token')
  getDailyNewsEmotionLoading.value = true

  axios.post(`${baseUrls.semantic_kernel_service}/SemanticKernel/skills/StockSkill/invoke/SummarizeNewsEmotion`,
  {
    'value': selectStock.value,
    'inputs': [
      {'key': 'day', 'value': day}
    ]
  },{
    headers: {'Authorization': `Bearer ${token}`},
  }).then((response) => {
    let res = response.data
    stockNewsEmotionList.value[day]['daily_emotion'] = res.value;
  }).catch((e) => {
    ElMessage('总结本日新闻情绪失败 ' + e)
  }).finally(()=>{
    getDailyNewsEmotionLoading.value = false
  })
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
  width: 75%;
}
.analysis-button {
  margin-top: 16px;
  margin-left: 12px;
}
.time-line {
  text-align: start;
  margin-top: 20px;
  margin-left: 10%;
  margin-right: 10%;
}
.daily-news-content {
  margin: 16px 8px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>