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
      >
        分析
      </el-button>
    </ul>

  </div>
</template>

<script setup lang="ts">
import {onMounted, ref} from "vue";
import {validLogin} from "@/utils/valid_utils"
import {useRouter} from "vue-router";
import axios from "axios";
import baseUrls from "@/config/baseUrlConfig";
import {ElMessage} from "element-plus";
import {Ask} from "@/utils/Ask";

const router = useRouter()

const stockList = ref<string[]>([])
const selectStock = ref('')
const getStockLoading = ref(false)

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

  const ask = new Ask(selectStock.value)

  axios.post(`${baseUrls.semantic_kernel_service}/SemanticKernel/skills/StockSkill/invoke/AnalysisStockNews`,
  {
    'value': selectStock.value,
    'inputs': []
  },{
        headers: {'Authorization': `Bearer ${token}`},
  }).then((response) => {

  }).catch((e) => {
    ElMessage('分析失败 ' + e)
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
  width: 60%;
}
.analysis-button {
  margin-top: 16px;
  margin-left: 12px;
}
</style>