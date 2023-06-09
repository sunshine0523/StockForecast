<template>
  <div class="news-type-div">
    <div/>
    <el-radio-group v-model="newsTypeRadio" class="ml-4" @change="getStockNewsCount(selectStock)">
      <el-radio label="-1" size="large">全部</el-radio>
      <el-radio label="1" size="large">新浪财经</el-radio>
      <el-radio label="2" size="large">股吧</el-radio>
    </el-radio-group>
    <el-tooltip
        class="box-item"
        effect="dark"
        content="通过语言模型分析新闻情感"
        placement="top"
    >
      <el-button
          type="primary"
          :disabled="selectStock.length === 0"
          class="analysis-button"
          @click="toAnalysis"
          :loading="getStockNewsEmotionLoading"
      >
        刷新
      </el-button>
    </el-tooltip>
  </div>
  <div class="time-line-div">
    <el-skeleton :rows="10" animated :loading="getStockNewsEmotionLoading">
      <template #default>
        <el-empty v-if="hasEmotionNews()" description="还没有相关新闻哦" />
        <div v-else>
          <el-row>
            <el-col :span="4">
              <h3 style="text-align: center"><i-ep-guide class="text-icon"/>&nbsp;快捷索引</h3>
              <el-divider/>
              <el-scrollbar height="200">
                <p v-for="(_, date) in stockNewsEmotionList" :key="date" style="text-align: center;">
                  <el-link
                      :href="'#'+date"
                      type="default"
                      style="color: black">
                    <span style="font-weight: bold">{{date}}</span>
                  </el-link>
                </p>
              </el-scrollbar>
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
                  <el-card :id="date" class="news-card">
                    <template #header>
                      <div class="card-header">
                        <h2 style="text-align: center"><i-ep-paperclip class="text-icon"/>{{date}} 新闻情绪事迹</h2>
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
                              @click="refreshNewsDailyEmotion(selectStock, date)"
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
                        🙁&nbsp;{{news.news_title}}<el-text size="small">&nbsp; {{news.news_time}}</el-text>
                      </el-link>
                      <el-link
                          v-else-if="news.emotion === 1"
                          :href="news.news_link"
                          type="default"
                          target="_blank"
                          style="color: #C62828"
                      >
                        😊&nbsp;{{news.news_title}}<el-text size="small">&nbsp; {{news.news_time}}</el-text>
                      </el-link>
                      <el-link
                          v-else-if="news.emotion === 0"
                          :href="news.news_link"
                          type="default"
                          target="_blank"
                          style="color: #282828"
                      >
                        😐&nbsp;{{news.news_title}}<el-text size="small">&nbsp; {{news.news_time}}</el-text>
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
                    @size-change="currentPage = 1; getStockNewsEmotionList(selectStock)"
                    @current-change="getStockNewsEmotionList(selectStock)"
                />
              </el-timeline>
            </el-col>
            <el-col :span="4">
              <el-card class="tip-card cloudy-knoxville-bg">
                <template #header>
                  <h3 style="text-align: center"><i-ep-info-filled class="text-icon"/>&nbsp;小贴士</h3>
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
</template>

<script setup lang="ts">
import {defineEmits, ref} from "vue";
import {
  refreshNewsDailyEmotion,
  getDailyNewsEmotionLoading,
  getStockNewsEmotionLoading,
  newsTypeRadio,
  stockNewsEmotionList,
  changeNewsEmotion,
  currentPage,
  pageCount,
  totalNewsCount, hasEmotionNews,
} from "@/views/analysis/analysis";
import axios from "axios";
import baseUrls from "@/config/baseUrlConfig";
import {ElMessage} from "element-plus";

const props = defineProps(
    {
      selectStock: { type: String, required: true },
      selectStockName: {type: String, required: true}
    }
)

watch(
    () => props.selectStock,
    () => {
      onSelectStock()
    }
);

const emit = defineEmits(['update:selectStockName'])

const selectStockInfo = ref({})

const onSelectStock = () =>{
  sessionStorage.setItem('stockCode', <string>props.selectStock)
  getStockInfo()
  getStockNewsCount(props.selectStock)
}

const toAnalysis = () => {
  const token = localStorage.getItem('token')
  getStockNewsEmotionLoading.value = true

  axios.post(`${baseUrls.semantic_kernel_service}/SemanticKernel/skills/StockSkill/invoke/AnalysisStockNews`,
      {
        'value': props.selectStock,
        'inputs': []
      },{
        headers: {'Authorization': `Bearer ${token}`},
      })
  .then(() => {
    getStockNewsEmotionList(props.selectStock)
  }).catch((e) => {
    ElMessage('分析失败 ' + e)
    getStockNewsEmotionLoading.value = false
  })
}

const getStockInfo = () => {
  axios.get(`${baseUrls.crawler}/getStockInfo?stock_code=${props.selectStock}`)
      .then((res)=>{
        selectStockInfo.value = res.data.data
        sessionStorage.setItem('stockName', selectStockInfo.value['name'])
        emit('update:selectStockName', selectStockInfo.value['name'])
      })
}

const getStockNewsCount = (selectStock) => {
  axios.get(`${baseUrls.crawler}/getHasEmotionNewsCount?stock_code=${selectStock}&news_type=${newsTypeRadio.value}`)
      .then((res)=>{
        totalNewsCount.value = res.data.data
        getStockNewsEmotionList(selectStock)
      })
}

//获取新闻情绪列表
const getStockNewsEmotionList = (selectStock) => {
  if (selectStock === '') return
  axios.get(`${baseUrls.crawler}/getStockNewsEmotionListByPage?stock_code=${selectStock}&page=${currentPage.value}&page_count=${pageCount.value}&news_type=${newsTypeRadio.value}`)
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

defineExpose({toAnalysis, getStockNewsCount})

</script>

<style scoped lang="sass">
@import "@/assets/analysis.sass"
</style>