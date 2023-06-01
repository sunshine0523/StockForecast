import json
import time

import pymongo
import requests
import tushare as ts
import yaml

from db_utils import MongoConnector


def init_config():
    # py的相对路径的根是main函数的执行位置，可以通过os.getcwd()来查看
    # with open('/tmp/config/mongo_config.yaml', encoding='utf-8') as f:
    #     config = yaml.load(f.read(), Loader=yaml.FullLoader)
    with open('config.yaml', encoding='utf-8') as f:
        _config = yaml.load(f.read(), Loader=yaml.FullLoader)
    return _config


config = init_config()


def crawl_stock_info():
    """
    从tushare获取股票基本信息
    :return:
    """
    pro = ts.pro_api(config['stock_info_crawler']['ts_token'])

    df = pro.stock_basic(**{

    }, fields=[
        "ts_code",
        "symbol",
        "name",
        "area",
        "industry",
        "market",
        "list_date",
        "fullname",
        "enname",
        "cnspell",
        "exchange",
        "curr_type",
        "list_status",
        "delist_date",
        "is_hs"
    ])

    mongo_connector = MongoConnector(
        config['stock_info_crawler']['db_name'],
        config['stock_info_crawler']['collection_name']
    )
    mongo_connector.collection.insert_many(df.to_dict('records'))
    mongo_connector.client.close()


def crawl_stock_daily(stock_code: str):
    """
    从tushare获取股票日K。如果历史已经获取过，那么只会接续那天获取
    :param stock_code:
    :return:
    """
    if stock_code == '':
        return
    pro = ts.pro_api(config['stock_info_crawler']['ts_token'])
    mongo_connector = MongoConnector(
        config['stock_daily_crawler']['db_name'],
        config['stock_daily_crawler']['collection_name']
    )
    r = [i for i in mongo_connector.find_by_filter(m_filter={'ts_code': stock_code}, m_sort=[("trade_date", pymongo.DESCENDING)]).limit(1)]
    end_date = time.strftime('%Y%m%d', time.localtime())
    if len(r) == 0:
        df = pro.daily(ts_code=stock_code, start_date='20230101', end_date=end_date)
        mongo_connector.collection.insert_many(df.to_dict('records'))
    elif end_date == r[0]['trade_date']:
        pass
    else:
        time_array = time.strptime(r[0]['trade_date'], '%Y%m%d')
        time_stamp = int(time.mktime(time_array)) + 24 * 60 * 60
        start_date = time.strftime('%Y%m%d', time.localtime(time_stamp))
        df = pro.daily(ts_code=stock_code, start_date=start_date, end_date=end_date)
        try:
            mongo_connector.collection.insert_many(df.to_dict('records'))
        except Exception:
            pass

    # 爬取完后，返回最近一百个交易日的信息
    stock_daily_list = mongo_connector.find_by_filter(m_filter={'ts_code': stock_code}, m_sort=[("trade_date", pymongo.DESCENDING)]).limit(100)
    result = []
    for daily in stock_daily_list:
        result.append({
            'ts_code': daily['ts_code'],
            'trade_date': daily['trade_date'],
            'open': daily['open'],
            'high': daily['high'],
            'low': daily['low'],
            'close': daily['close'],
            'pre_close': daily['pre_close'],
            'change': daily['change'],
            'pct_chg': daily['pct_chg'],
            'vol': daily['vol'],
            'amount': daily['amount']
        })
    mongo_connector.client.close()
    result.reverse()
    return result


def crawl_stock_current(stock_code: str):
    """
    从gtimg.cn爬取实时股票数据。实时数据就不缓存了吧
    :param stock_code: 股票代码，格式如：000001.SZ
    :return:
    """
    # 股票的基本数据，包括昨日收盘、今日开盘、当前价格、涨幅等信息
    stock_info_base_url = 'http://qt.gtimg.cn/q='
    # 对于腾讯的api接口，接受的股票代码格式如：sz000001，需要预处理
    tencent_stock_code = ''.join(stock_code.split('.').__reversed__()).casefold()
    try:
        res = requests.get(f'{stock_info_base_url}{tencent_stock_code}')
    except Exception as e:
        print(e)
        return {'cur_price': '获取失败'}
    stock_info = res.text.split('~')
    try:
        return {
            # 股票代码
            'stock_code': stock_code,
            # 当前价格
            'cur_price': stock_info[3],
            # 昨日收盘价
            'last_close': stock_info[4],
            # 今日开盘价
            'today_open': stock_info[5],
            # 成交量
            'volume': stock_info[6],
            # 请求时间
            'request_time': time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(int(time.mktime(time.strptime(stock_info[30], '%Y%m%d%H%M%S'))))),
            # 涨跌
            'rise_or_fall': stock_info[31],
            # 涨跌幅
            'rise_or_fall_ratio': stock_info[32],
            # 最高价
            'max_price': stock_info[33],
            # 最低价
            'min_price': stock_info[34]
        }
    except Exception as e:
        print(e)
        return {'cur_price': '获取失败'}


def crawl_stock_minute(stock_code: str):
    """
    获取股票分时信息，不进行缓存
    :param stock_code:
    :return:
    """
    # 股票的分时信息
    stock_minute_base_url = 'https://web.ifzq.gtimg.cn/appstock/app/minute/query?code='
    # 对于腾讯的api接口，接受的股票代码格式如：sz000001，需要预处理
    tencent_stock_code = ''.join(stock_code.split('.').__reversed__()).casefold()
    try:
        res = requests.get(f'{stock_minute_base_url}{tencent_stock_code}')
    except Exception as e:
        print(e)
        return {}
    try:
        return {
            'data': json.loads(res.text)['data'][tencent_stock_code]['data']['data'],
            'qt': json.loads(res.text)['data'][tencent_stock_code]['qt'][tencent_stock_code]
        }
    except Exception as e:
        print(e)
        return {}


if __name__ == '__main__':
    print(crawl_stock_minute('000001.SZ'))