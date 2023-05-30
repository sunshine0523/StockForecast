import yaml
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import server_func
import stock_info_crawler
import uvicorn

import stock_news_crawler


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


@app.get('/getStockNewsList')
def get_stock_news_list(query: str):
    """
    获取股票新闻列表
    :param query:
    :return:
    """
    return {'data': server_func.get_stock_news_list(query)}


@app.get('/refreshStockNews')
def refresh_stock_news(stock_code: str, page_count: int = 10):
    """
    刷新股票新闻
    :param stock_code:
    :param page_count:
    :return:
    """
    stock_news_crawler.crawler_sina(
        stock_code=stock_code,
        db_name=config['stock_news_crawler']['db_name'],
        table_name=config['stock_news_crawler']['table_name'],
        page_count=page_count
    )
    return get_stock_news_list(query=stock_code)


@app.get('/getStockDailyList')
def get_stock_daily_list(stock_code: str):
    """
    获取股票日K
    :param stock_code:
    :return:
    """
    return {'data': stock_info_crawler.crawl_stock_daily(stock_code)}


@app.get('/getStockNewsEmotionList')
def get_stock_news_emotion_list(stock_code: str):
    """
    获取近10日的股票新闻情感信息，按日分组
    :param stock_code:
    :return:
    """
    return {'data': server_func.get_news_emotion_list(stock_code)}


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
def get_stock_news_emotion_list(stock_code: str, end_date: str, days_count: int):
    """
    获取end_date前days_count天数的股票预测情况
    :param stock_code:
    :param end_date: 预测的结束日期
    :param days_count: 预测的天数
    :return:
    """
    return {'data': server_func.get_last_days_daily_news_emotion_score(stock_code, end_date, days_count)}


if __name__ == '__main__':
    uvicorn.run(app)
