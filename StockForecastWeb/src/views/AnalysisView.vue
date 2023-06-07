<template>
  <div class="header-div"/>
  <h1 class="title">{{selectStockInfo.name}}  行情分析 </h1>
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
          @change="onSelectStock"
      >
        <el-option
            v-for="item in stockList"
            :key="item.ts_code"
            :label="`${item.ts_code} ${item.name}`"
            :value="item.ts_code"
        />
      </el-select>
      <el-tooltip
          class="box-item"
          effect="dark"
          content="通过语言模型分析新闻情感"
          placement="top"
      >
        <el-button
            type="primary"
            size="large"
            :disabled="selectStock.length === 0"
            class="analysis-button"
            @click="toAnalysis"
            :loading="getStockNewsEmotionLoading"
        >
          刷新情感分析
        </el-button>
      </el-tooltip>
    </ul>
    <div class="news-type-div">
      <el-radio-group v-model="newsTypeRadio" class="ml-4" @change="getStockNewsCount">
        <el-radio label="-1" size="large">全部</el-radio>
        <el-radio label="1" size="large">新浪财经</el-radio>
        <el-radio label="2" size="large">股吧</el-radio>
      </el-radio-group>
    </div>
    <div class="time-line-div">
      <el-skeleton :rows="10" animated :loading="getStockNewsEmotionLoading">
        <template #default>
          <el-empty v-if="stockNewsEmotionList.length === 0" description="还没有相关新闻哦" />
          <div v-else>
            <el-row>
              <el-col :span="4">
                <el-affix :offset="300">
                  <h3 style="text-align: center">快捷索引</h3>
                  <el-divider/>
                  <el-scrollbar height="200">
                    <p v-for="(_, date) in stockNewsEmotionList" :key="date" style="text-align: center;">
                      <el-link
                          :href="'#'+date"
                          type="default"
                          style="color: black">
                        {{date}}
                      </el-link>
                    </p>
                  </el-scrollbar>
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
                          <el-tooltip
                              class="box-item"
                              effect="dark"
                              content="通过语言模型总结今日新闻，并尝试给出股价走势"
                              placement="top"
                          >
                            <el-button
                                text
                                type="primary"
                                :loading="getDailyNewsEmotionLoading"
                                @click="refreshNewsDailyEmotion(date)"
                            >刷新本日总结
                            </el-button>
                          </el-tooltip>
                        </div>
                        <p style="margin: 6px;">本日总结：{{ daily_news['daily_emotion'] }}</p>
                      </template>
                      <div v-for="(news, index) in daily_news['news']" :key="index" class="daily-news-content">
                        <el-link
                            v-if="news.emotion === -1"
                            :href="news.news_link"
                            type="default"
                            target="_blank"
                            style="color: #2E7D32"
                        >
                          🙁 {{news.news_title}}<el-text size="small">&nbsp; {{news.news_time}}</el-text>
                        </el-link>
                        <el-link
                            v-if="news.emotion === 1"
                            :href="news.news_link"
                            type="default"
                            target="_blank"
                            style="color: #C62828"
                        >
                          😊 {{news.news_title}}<el-text size="small">&nbsp; {{news.news_time}}</el-text>
                        </el-link>
                        <el-link
                            v-if="news.emotion === 0"
                            :href="news.news_link"
                            type="default"
                            target="_blank"
                            style="color: #282828"
                        >
                          😐 {{news.news_title}}<el-text size="small">&nbsp; {{news.news_time}}</el-text>
                        </el-link>
                        &nbsp;
                        <el-tooltip
                            class="box-item"
                            effect="dark"
                            content="标记为正面新闻"
                            placement="top"
                        >
                          <el-button text round @click="changeNewsEmotion(news, 1)">😊</el-button>
                        </el-tooltip>
                        <el-tooltip
                            class="box-item"
                            effect="dark"
                            content="标记为负面新闻"
                            placement="top"
                        >
                          <el-button text round @click="changeNewsEmotion(news, -1)">🙁</el-button>
                        </el-tooltip>
                        <el-tooltip
                            class="box-item"
                            effect="dark"
                            content="标记为中性新闻"
                            placement="top"
                        >
                          <el-button text round @click="changeNewsEmotion(news, 0)">😐</el-button>
                        </el-tooltip>
                      </div>
                    </el-card>
                  </el-timeline-item>
                  <el-pagination
                      v-model:current-page="currentPage"
                      v-model:page-size="pageCount"
                      :total="totalNewsCount"
                      :page-sizes="[5, 10, 20, 30, 40, 50, 100, 150, 200, 250, 300, 350, 400]"
                      background layout="sizes, prev, pager, next"
                      @size-change="currentPage = 1; getStockNewsEmotionList()"
                      @current-change="getStockNewsEmotionList"
                  />
                </el-timeline>
              </el-col>
              <el-col :span="4">
                <el-card class="tip-card cloudy-knoxville-bg">
                  <template #header>
                    <h3 style="text-align: center"><i-ep-info-filled/>小贴士</h3>
                  </template>
                  <p>1.您可以选择全部新闻来源，或者在上方选择指定的新闻来源。目前支持<i>新浪财经</i>和<i>股吧</i>新闻来源</p>
                  <p>2.新闻按照<i>交易时间</i>分段，即每天15点之前视为今天的新闻，过了15点的算所明日的新闻。</p>
                  <p>3.红色标题表示经过语言模型分析，该新闻可能含积极情绪，绿色标题表示该新闻可能含消极情绪。</p>
                  <p>4.点击右上方“刷新本日总结”按钮，可以获取语言模型根据新闻分析的今日新闻内容总结。</p>
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
import {ElMessage, ElNotification} from "element-plus";

const router = useRouter()

const stockList = ref<string[]>([])
const selectStock = ref('')
const getStockLoading = ref(false)
const getStockNewsEmotionLoading = ref(false)
const stockNewsEmotionList = ref([])
const getDailyNewsEmotionLoading = ref(false)
const newsTypeRadio = ref('-1')

const selectStockInfo = ref({})

//分页相关
const currentPage = ref(1)
//每页容量
const pageCount = ref(5)
const totalNewsCount = ref(0)

onMounted(()=>{
  if (!validLogin()) router.push('/login')

  //设置默认展示的股票
  let stockCode = sessionStorage.getItem('stockCode')

  if (null != stockCode) {
    selectStock.value = stockCode
    getStockInfo()
    getStockNewsCount()
  }
})

const onSelectStock = () => {
  sessionStorage.setItem('stockCode', selectStock.value)
  getStockInfo()
  getStockNewsCount()
}

const getStockNewsCount = () => {
  axios.get(`${baseUrls.crawler}/getNewsCount?stock_code=${selectStock.value}&news_type=${newsTypeRadio.value}`)
      .then((res)=>{
        totalNewsCount.value = res.data.data
        getStockNewsEmotionList()
      })
}

const getStockInfo = () => {
  axios.get(`${baseUrls.crawler}/getStockInfo?stock_code=${selectStock.value}`)
      .then((res)=>{
        selectStockInfo.value = res.data.data
        sessionStorage.setItem('stockName', selectStockInfo.value['name'])
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
  if (selectStock.value === '') return
  axios.get(`${baseUrls.crawler}/getStockNewsEmotionListByPage?stock_code=${selectStock.value}&page=${currentPage.value}&page_count=${pageCount.value}&news_type=${newsTypeRadio.value}`)
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

/**
 *
 * @param news 新闻实体
 * @param emotion 新闻的情绪 积极1 消极-1 中性0
 */
const changeNewsEmotion = (news, emotion) => {
  axios.post(`${baseUrls.crawler}/updateNewsEmotion`, {
    news_id: news.id,
    emotion: emotion,
  })
      .then((res)=>{
        if (res.data.type == 200) {
          ElNotification({
            title: '提示',
            message: '情绪标记成功',
          })
          console.log(news)
          news.emotion = emotion
        } else {
          ElNotification({
            title: '提示',
            message: '情绪标记失败 ' + res.data.data,
          })
        }
      })
      .catch((e)=>{
        ElMessage('标记新闻情绪时出现问题 ' + e)
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
  width: 75%;
}
.analysis-button {
  margin-top: 16px;
  margin-left: 12px;
}
.news-type-div {
  text-align: center;
  margin: 20px auto 0 auto;
}
.time-line-div {
  text-align: start;
  margin-top: 20px;
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
.tip-card {
  margin-top: 22px;
  text-align: start;
  background-color: snow;
}
.el-card {
  border-radius: 16px;
}
</style>