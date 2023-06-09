<template>
  <div class="header-div"/>
  <h1 class="title">{{selectStockInfo.name}} 股票行情 </h1>
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
    <el-row style="margin-top: 20px">
      <el-col :span="4">
        <el-affix :offset="240">
          <el-card class="recent-card">
            <template #header>
              <h3 style="text-align: center"><i-ep-clock class="text-icon"/>&nbsp;最近访问</h3>
            </template>
            <div v-for="stock in favoriteStockList" style="margin-top: 5px">
              <el-link @click="selectStock=stock.stock_code;onSelectStock()" style="color: #282828">{{stock.stock_code}} {{stock.name}}</el-link>
            </div>
          </el-card>
        </el-affix>
      </el-col>
      <el-col :span="1"/>
      <el-col :span="14">
        <el-tabs v-model="activeTabName" @tab-change="currentPage = 1; getStockNewsCount()">
          <el-tab-pane label="新浪财经" name="1">

          </el-tab-pane>
          <el-tab-pane label="股吧" name="2">

          </el-tab-pane>
        </el-tabs>
        <div class="crawler-option" v-show="getStockNewsDone">
          <div>
            爬取页数
            <el-select
                v-model="crawlPageCount"
                style="width: 120px;"
            >
              <el-option
                  v-for="item in crawlPageCountList"
                  :key="item"
                  :label="item"
                  :value="item"
              />
            </el-select>
          </div>
          <div>
            <el-button type="primary" :loading="refreshStockNews" @click="refreshStockNewsFunc"><i-ep-refresh/>&nbsp;刷新</el-button>
            <el-button @click="deleteDialogVisible = true"><i-ep-delete/>&nbsp;删除</el-button>
          </div>
        </div>

        <div class="time-line">
          <el-skeleton :rows="10" animated :loading="getStockNewsLoading">
            <template #default>
              <el-empty v-if="stockNewsList.length === 0" description="还没有相关新闻哦" />
              <div v-else>
                <el-timeline>
                  <el-timeline-item
                      v-for="(news, index) in stockNewsList"
                      :key="index"
                      :size="'large'"
                      :timestamp="news.time"
                      :hollow="true"
                      :type="'primary'"
                      placement="top"
                  >
                    <el-link :href="news.news_link" type="default" target="_blank">{{news.news_title}}</el-link>
                    &nbsp;
                    <el-tooltip
                        class="box-item"
                        effect="dark"
                        content="标记为正面新闻"
                        placement="top"
                    >
                      <el-button text round @click="changeNewsEmotion(news.id, 1)">😊</el-button>
                    </el-tooltip>
                    <el-tooltip
                        class="box-item"
                        effect="dark"
                        content="标记为负面新闻"
                        placement="top"
                    >
                      <el-button text round @click="changeNewsEmotion(news.id, -1)">🙁</el-button>
                    </el-tooltip>
                    <el-tooltip
                        class="box-item"
                        effect="dark"
                        content="标记为中性新闻"
                        placement="top"
                    >
                      <el-button text round @click="changeNewsEmotion(news.id, 0)">😐</el-button>
                    </el-tooltip>
                  </el-timeline-item>
                </el-timeline>
                <el-pagination
                    v-model:current-page="currentPage"
                    v-model:page-size="pageCount"
                    :total="totalNewsCount"
                    :page-sizes="[5, 10, 20, 30, 40, 50, 100, 150, 200, 250, 300, 350, 400]"
                    background layout="sizes, prev, pager, next"
                    @size-change="currentPage = 1; getStockNews()"
                    @current-change="getStockNews"
                />
              </div>
            </template>
          </el-skeleton>
        </div>
      </el-col>
      <el-col :span="1"/>
      <el-col :span="4">
        <el-card class="premium-white-bg" style="margin-top: 32px">
          <template #header>
            <h3 style="text-align: center"><i-ep-info-filled class="text-icon"/>&nbsp;股票信息</h3>
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
  <el-dialog v-model="deleteDialogVisible" title="删除新闻">
    <el-form :model="deleteForm">
      <el-form-item label="起始日期">
        <el-date-picker
            v-model="deleteForm.from"
            type="datetime"
            placeholder="选择删除的起始日期"
        />
      </el-form-item>
      <el-form-item label="结束日期">
        <el-date-picker
            v-model="deleteForm.to"
            type="datetime"
            placeholder="选择删除的结束日期"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="deleteDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="toDeleteNews" :disabled="deleteForm.from === '' || deleteForm.to === ''">
          删除
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import {onMounted, ref} from "vue";
import {validLogin} from "@/utils/valid_utils"
import {useRouter} from "vue-router";
import axios, {get} from "axios";
import baseUrls from "@/config/baseUrlConfig";
import {ElMessage, ElNotification} from "element-plus";

const router = useRouter()

const activeTabName = ref('1')

const stockList = ref<string[]>([])
const selectStock = ref('')
const getStockLoading = ref(false)
const stockNewsList = ref([])
const getStockNewsLoading = ref(false)
const getStockNewsDone = ref(false)
const refreshStockNews = ref(false)
const crawlPageCount = ref('10')
const crawlPageCountList = [5, 10, 15, 20]
const deleteDialogVisible = ref(false)
//猜你喜欢列表
const favoriteStockList = ref([])
const deleteForm = reactive({
  from: '',
  to: ''
})
const selectStockInfo = ref({})
//分页相关
const currentPage = ref(1)
//每页容量
const pageCount = ref(5)
const totalNewsCount = ref(0)

onMounted(()=>{
  if (!validLogin()) router.push('/login')
  getFavoriteStockList()

  //设置默认展示的股票
  let stockCode = sessionStorage.getItem('stockCode')

  if (null != stockCode) {
    selectStock.value = stockCode
    getStockInfo()
    getStockNewsCount()
  }
})

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
  getStockNewsCount()
}

/**
 *
 * @param id 新闻的id
 * @param emotion 新闻的情绪 积极1 消极-1 中性0
 */
const changeNewsEmotion = (id, emotion) => {
  axios.post(`${baseUrls.crawler}/updateNewsEmotion`, {
    news_id: id,
    emotion: emotion,
  })
  .then((res)=>{
    if (res.data.type == 200) {
      ElNotification({
        title: '提示',
        message: '情绪标记成功',
      })
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

const getStockInfo = () => {
  axios.get(`${baseUrls.crawler}/getStockInfo?stock_code=${selectStock.value}`)
      .then((res)=>{
        selectStockInfo.value = res.data.data
        sessionStorage.setItem('stockName', selectStockInfo.value['name'])
      })
}

const getStockNewsCount = () => {
  axios.get(`${baseUrls.crawler}/getNewsCount?stock_code=${selectStock.value}&news_type=${activeTabName.value}`)
      .then((res)=>{
        totalNewsCount.value = res.data.data
        getStockNews()
      })
}

const getStockNews = () => {
  if (selectStock.value === '') return
  getStockNewsLoading.value = true
  getStockNewsDone.value = false
  axios.get(`${baseUrls.crawler}/getStockNewsListByPage?stock_code=${selectStock.value}&page=${currentPage.value}&page_count=${pageCount.value}&news_type=${activeTabName.value}`)
      .then((response)=>{
        stockNewsList.value = response.data.data
        getStockNewsDone.value = true
      })
      .catch((e)=>{
        ElMessage('获取新闻时出现问题 ' + e)
      })
      .finally(()=>{
        getStockNewsLoading.value = false
      })
}

const refreshStockNewsFunc = () => {
  getStockNewsLoading.value = true
  refreshStockNews.value = true
  axios.get(`${baseUrls.crawler}/refreshStockNews?stock_code=${selectStock.value}&page_count=${crawlPageCount.value}&news_type=${activeTabName.value}`)
      .then((response)=>{
        currentPage.value = 1
        getStockNewsCount()
      })
      .catch((e)=>{
        ElMessage('刷新新闻时出现问题 ' + e)
      })
      .finally(()=>{
        getStockNewsLoading.value = false
        refreshStockNews.value = false
      })
}

const toDeleteNews = () => {
  axios.post(`${baseUrls.crawler}/deleteStockNews`, {
    stock_code: selectStock.value,
    from_date: deleteForm.from.getTime()/1000,
    to_date: deleteForm.to.getTime()/1000,
    news_type: activeTabName.value
  })
      .then(()=>{
        deleteDialogVisible.value = false
        getStockNews()
        ElNotification({
          title: '提示',
          message: '新闻已经成功删除',
        })
      })
      .catch((e)=>{
        ElMessage('删除新闻时出现问题 ' + e)
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
.time-line {
  text-align: start;
}
.crawler-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.el-card {
  border-radius: 16px;
}
.recent-card /deep/ .el-card__header {
  background-image: linear-gradient(to top, #ffffff, #fbf8fd, #fbeff8, #fde7f0, #ffdee4);
}
</style>