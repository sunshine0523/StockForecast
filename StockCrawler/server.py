import yaml
from fastapi import FastAPI, Form, Body
from fastapi.middleware.cors import CORSMiddleware
import server_func
import uvicorn


def init_config():
    with open('config.yaml', encoding='utf-8') as f:
        _config = yaml.load(f.read(), Loader=yaml.FullLoader)
    return _config


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

config = init_config()


@app.get('/getStockList')
def get_stock_list(query: str):
    """
    获取股票列表
    :param query:
    :return:
    """
    return {'data': server_func.get_stock_list(query)}


@app.get('/getStockInfo')
def get_stock_info(stock_code: str):
    """
    获取指定股票的信息
    :param stock_code:
    :return:
    """
    return {'data': server_func.get_stock_info(stock_code)}


@app.get('/getStockNewsList')
def get_stock_news_list(query: str, news_type: int = 1):
    """
    获取股票新闻列表
    :param news_type:
    :param query:
    :return:
    """
    return {'data': server_func.get_stock_news_list(query, news_type)}


@app.get('/getStockNewsListByPage')
def get_stock_news_list_by_page(stock_code: str, page: int, page_count: int, news_type: int = 1):
    """
    分页获取股票新闻列表
    :param page_count: 每页容量
    :param page: 第几页，从1开始
    :param news_type:
    :param stock_code:
    :return:
    """
    return {'data': server_func.get_stock_news_list_by_page(stock_code, page, page_count, news_type)}


@app.get('/getNewsCount')
def get_news_count(stock_code: str, news_type: int = -1):
    """
    获取新闻条数，供分页器使用
    :param stock_code:
    :param news_type:
    :return:
    """
    return {'data': server_func.get_news_count(stock_code, news_type)}


@app.post('/deleteStockNews')
def delete_stock_news(
        stock_code: str = Body(),
        from_date: str = Body(),
        to_date: str = Body(),
        news_type: int = Body()
):
    """
    删除日期范围内的新闻
    :param stock_code:
    :param from_date: 时间戳
    :param to_date: 时间戳
    :param news_type:
    :return:
    """
    server_func.delete_stock_news(stock_code, from_date, to_date, news_type)


@app.get('/getFavoriteStockList')
def get_stock_has_news_list():
    """
    获取已经有新闻的股票名称，来作为推荐列表
    :return:
    """
    return {'data': server_func.get_stock_has_news_list()}


@app.get('/refreshStockNews')
def refresh_stock_news(stock_code: str, page_count: int = 10, news_type: int = 1):
    """
    刷新股票新闻
    :param news_type: 爬取的源，1新浪财经 2股吧
    :param stock_code:
    :param page_count:
    :return:
    """
    server_func.refresh_stock_news(stock_code, page_count, news_type)
    return {'data', ''}


@app.get('/getStockNewsEmotionListByPage')
def get_stock_news_emotion_list_by_page(stock_code: str, page: int, page_count: int, news_type: int = -1):
    """
    获取近10日的股票新闻情感信息，按日分组
    :param page_count:
    :param page:
    :param news_type: -1表示查询所有来源
    :param stock_code:
    :return:
    """
    return {'data': server_func.get_news_emotion_list_by_page(stock_code, page, page_count, news_type)}


@app.get('/getDailyNewsEmotionScore')
def get_stock_news_emotion(stock_code: str, news_date: str):
    """
    获取指定日期的情绪总体分数
    :param news_date: 格式yyyymmdd
    :param stock_code:
    :return:
    """
    return {'data': server_func.get_daily_news_emotion_score(stock_code, news_date)}


@app.get('/getLastDaysDailyNewsEmotionScoreList')
def get_stock_news_emotion_list(stock_code: str, days_count: int, news_type: int = -1):
    """
    获取end_date前days_count天数的股票预测情况
    :param news_type: -1为获取全部类型
    :param stock_code:
    :param days_count: 预测的天数
    :return:
    """
    return {'data': server_func.get_last_days_daily_news_emotion_score(stock_code, days_count, news_type)}


@app.post('/updateNewsEmotion')
def update_news_emotion(news_id: int = Body(), emotion: int = Body()):
    """
    更新新闻情绪
    :param news_id:
    :param emotion:
    :return:
    """
    exec_type, res = server_func.update_news_emotion(news_id, emotion)
    if exec_type:
        return {'type': 200, 'data': res}
    else:
        return {'type': 500, 'data': res}


@app.get('/getStockDailyList')
def get_stock_daily_list(stock_code: str):
    """
    获取股票日K
    :param stock_code:
    :return:
    """
    return {'data': server_func.get_stock_daily_list(stock_code)}


@app.get('/getStockCurrentInfo')
def get_stock_current_info(stock_code: str):
    """
    获取股票实时信息
    :param stock_code:
    :return:
    """
    return {'data': server_func.get_stock_current_info(stock_code)}


@app.get('/getStockMinuteList')
def get_stock_minute_list(stock_code: str):
    """
    获取股票分时信息
    :param stock_code:
    :return:
    """
    return {'data': server_func.get_stock_minute(stock_code)}


if __name__ == '__main__':
    uvicorn.run(app)
