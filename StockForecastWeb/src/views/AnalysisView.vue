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
    <div class="time-line-div">
      <el-skeleton :rows="10" animated :loading="getStockNewsEmotionLoading">
        <template #default>
          <el-empty v-if="stockNewsEmotionList.length === 0" description="还没有相关新闻哦" />
          <div v-else>
            <el-row>
              <el-col :span="4">
                <el-affix :offset="270">
                  <h3 style="text-align: center">快捷索引</h3>
                  <el-divider/>
                  <p v-for="(_, date) in stockNewsEmotionList" :key="date" style="text-align: center;">
                    <el-link
                        :href="'#'+date"
                        type="default"
                        style="color: black">
                      {{date}}
                    </el-link>
                  </p>
                  <el-divider/>
                </el-affix>
              </el-col>
              <el-col :span="16">
                <el-timeline class="time-line">
                  <el-timeline-item
                      v-for="(daily_news, date) in stockNewsEmotionList"
                      :key="date"
                      :size="'large'"
                      :timestamp="date"
                      :hollow="true"
                      :type="'primary'"
                      placement="top"
                  >
                    <el-card :id="date">
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
              </el-col>
              <el-col :span="4">
                <el-card style="margin-top: 22px">
                  <template #header>
                    <h3 style="text-align: center"><i-ep-info-filled/>小贴士</h3>
                  </template>
                  <p>1.新闻按照<i>交易时间</i>分段，即每天15点之前视为今天的新闻，过了15点的算所明日的新闻。</p>
                  <p>2.红色标题表示经过语言模型分析，该新闻可能含积极情绪，绿色标题表示该新闻可能含消极情绪。</p>
                  <p>3.点击右上方“刷新本日总结”按钮，可以获取语言模型根据新闻分析的今日新闻内容总结。</p>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </template>
      </el-skeleton>
    </div>
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
.time-line-div {
  text-align: start;
  margin-top: 40px;
}
.time-line {
  margin-left: 32px;
  margin-right: 32px;
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