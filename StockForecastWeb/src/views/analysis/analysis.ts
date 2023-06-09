import axios from "axios";
import baseUrls from "@/config/baseUrlConfig";
import {ref} from "vue";
import {ElMessage, ElNotification} from "element-plus";

//分页相关
export const currentPage = ref(1)
//每页容量
export const pageCount = ref(5)
export const totalNewsCount = ref(0)
export const newsTypeRadio = ref('-1')
export const stockNewsEmotionList = ref({})
export const getStockNewsEmotionLoading = ref(false)
export const getDailyNewsEmotionLoading = ref(false)

//判断情绪新闻列表里是否有数据
export function hasEmotionNews() {
    return JSON.stringify(stockNewsEmotionList.value) == '{}'
}

export const refreshNewsDailyEmotion = (selectStock: string, day: number) => {
    const token = localStorage.getItem('token')
    getDailyNewsEmotionLoading.value = true

    axios.post(`${baseUrls.semantic_kernel_service}/SemanticKernel/skills/StockSkill/invoke/SummarizeNewsEmotion`,
        {
            'value': selectStock,
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
export const changeNewsEmotion = (news, emotion) => {
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