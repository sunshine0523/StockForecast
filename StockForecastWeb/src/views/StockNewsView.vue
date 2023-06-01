<template>
  <h1 class="title">股票行情</h1>
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

      </el-col>
      <el-col :span="16">
        <el-tabs v-model="activeTabName" @tab-change="getStockNews">
          <el-tab-pane label="新浪财经" name="1">

          </el-tab-pane>
          <el-tab-pane label="股吧" name="2">

          </el-tab-pane>
        </el-tabs>
        <div class="news_option" v-show="getStockNewsDone">
          <el-button type="primary" :loading="refreshStockNews" @click="refreshStockNewsFunc"><i-ep-refresh/>&nbsp;刷新</el-button>
        </div>
        <div class="time-line">
          <el-skeleton :rows="10" animated :loading="getStockNewsLoading">
            <template #default>
              <el-empty v-if="stockNewsList.length === 0" description="还没有相关新闻哦" />
              <el-timeline v-else>
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
                </el-timeline-item>
              </el-timeline>
            </template>
          </el-skeleton>
        </div>
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

const router = useRouter()

const activeTabName = ref('1')

const stockList = ref<string[]>([])
const selectStock = ref('')
const getStockLoading = ref(false)
const stockNewsList = ref([])
const getStockNewsLoading = ref(false)
const getStockNewsDone = ref(false)
const refreshStockNews = ref(false)

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
  getStockNews()
}

const getStockNews = () => {
  getStockNewsLoading.value = true
  getStockNewsDone.value = false
  axios.get(`${baseUrls.crawler}/getStockNewsList?query=${selectStock.value}&news_type=${activeTabName.value}`)
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
  axios.get(`${baseUrls.crawler}/refreshStockNews?stock_code=${selectStock.value}&page_count=5&news_type=${activeTabName.value}`)
      .then((response)=>{
        stockNewsList.value = response.data.data
      })
      .catch((e)=>{
        ElMessage('刷新新闻时出现问题 ' + e)
      })
      .finally(()=>{
        getStockNewsLoading.value = false
        refreshStockNews.value = false
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
.news_option {
  text-align: end;
}
.time-line {
  text-align: start;
}
</style>