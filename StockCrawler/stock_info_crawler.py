import time

import pymongo
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


def crawl_stock_daily(ts_code: str):
    """
    获取股票日K。如果历史已经获取过，那么只会接续那天获取
    :param ts_code:
    :return:
    """
    pro = ts.pro_api(config['stock_info_crawler']['ts_token'])
    mongo_connector = MongoConnector(
        config['stock_daily_crawler']['db_name'],
        config['stock_daily_crawler']['collection_name']
    )
    r = [i for i in mongo_connector.find_by_filter(m_filter={'ts_code': ts_code}, m_sort=[("trade_date", pymongo.DESCENDING)]).limit(1)]
    end_date = time.strftime('%Y%m%d', time.localtime())
    if len(r) == 0:
        df = pro.daily(ts_code=ts_code, start_date='20230101', end_date=end_date)
        mongo_connector.collection.insert_many(df.to_dict('records'))
    elif end_date == r[0]['trade_date']:
        pass
    else:
        time_array = time.strptime(r[0]['trade_date'], '%Y%m%d')
        time_stamp = int(time.mktime(time_array)) + 24 * 60 * 60
        start_date = time.strftime('%Y%m%d', time.localtime(time_stamp))
        df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        try:
            mongo_connector.collection.insert_many(df.to_dict('records'))
        except Exception:
            pass

    # 爬取完后，返回最近一百个交易日的信息
    stock_daily_list = mongo_connector.find_by_filter(m_filter={'ts_code': ts_code}, m_sort=[("trade_date", pymongo.DESCENDING)]).limit(100)
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
