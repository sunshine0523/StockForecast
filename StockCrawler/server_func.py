import datetime
import re
import time
import yaml
from db_utils import MongoConnector, MySQLConnector
from chinese_calendar import is_holiday


def init_config():
    with open('config.yaml', encoding='utf-8') as f:
        _config = yaml.load(f.read(), Loader=yaml.FullLoader)
    return _config


config = init_config()


def get_stock_list(query: str):
    mongo_connector = MongoConnector(
        config['stock_info_crawler']['db_name'],
        config['stock_info_crawler']['collection_name']
    )
    m_filter = {
        "$or": [
            {"ts_code": re.compile(query)},
            {"name": re.compile(query)},
            {"enname": re.compile(query)},
            {"cnspell": re.compile(query)}
        ]
    }
    res = []
    for stock in mongo_connector.find_by_filter(m_filter=m_filter):
        res.append({
            'ts_code': stock['ts_code'],
            'name': stock['name'],
            # 'area': stock['area'],
            # 'industry': stock['industry'],
            # 'fullname': stock['fullname'],
            # 'enname': stock['enname'],
            # 'cnspell': stock['cnspell'],
            # 'market': stock['market'],
            # 'exchange': stock['exchange'],
            # 'curr_type': stock['curr_type'],
            # 'list_status': stock['list_status'],
            # 'list_date': stock['list_date']
        })
    mongo_connector.client.close()
    return res


def get_stock_news_list(query: str):
    mysql_connector = MySQLConnector(config['stock_news_crawler']['db_name'])
    mysql_connector.execute_sql(f'''
        select * from stock_news
        where stock_code='{query}'
        order by time_stamp desc
    ''')
    mysql_connector.commit()
    res = []
    news_list = mysql_connector.cursor.fetchall()
    for news in news_list:
        res.append({
            'news_title': news['news_title'],
            'news_link': news['news_link'],
            'time': time.strftime('%Y-%m-%d %H:%M', time.localtime(news['time_stamp']))
        })
    mysql_connector.close()
    return res


def get_daily_news_emotion_score(stock_code: str, date: str):
    """
    获取指定日期的新闻整体情绪分数
    :param stock_code:
    :param date:
    :return:
    """
    mysql_connector = MySQLConnector(config['stock_news_crawler']['db_name'])
    timestamp = int(time.mktime(time.strptime(date, '%Y%m%d')))
    start_time = timestamp - 9 * 60 * 60
    end_time = timestamp + 15 * 60 * 60

    mysql_connector.execute_sql(f'''
        select emotion from stock_news
        where stock_code='{stock_code}' and time_stamp >= {start_time} and time_stamp <= {end_time} and emotion != 0 and emotion != -2
    ''')
    mysql_connector.commit()
    daily_emotion_score = 0
    news_list = mysql_connector.cursor.fetchall()
    # 如果当天没有新闻，则不进行预测
    if len(news_list) == 0:
        return 0
    for news in news_list:
        daily_emotion_score += news['emotion']
    mysql_connector.close()

    # 返回的结果应该加权。首先，我们需要分数/新闻条数来得到平均分。然后，获取最新一日的股价，规定每25价格对应单位1.
    mongo_connector = MongoConnector(
        config['stock_daily_crawler']['db_name'],
        config['stock_daily_crawler']['collection_name']
    )
    daily_info = [i for i in mongo_connector.find_by_filter(m_filter={'ts_code': stock_code}).limit(1)]
    if len(daily_info) == 0:
        price = 100
    else:
        price = daily_info[0]['close']
    mongo_connector.client.close()
    return daily_emotion_score / len(news_list) * price / 25


def get_last_days_daily_news_emotion_score(stock_code: str, end_date: str, days_count: int):
    """
    获取end_date前days_count天数的股票预测情况
    :param stock_code:
    :param end_date: 预测的结束日期
    :param days_count: 预测的天数
    :return:
    """
    timestamp = int(time.mktime(time.strptime(end_date, '%Y%m%d')))
    res = []
    i = 0
    j = 0
    while i < days_count:
        date = time.strftime('%Y%m%d', time.localtime(timestamp - j * 24 * 60 * 60))
        if is_holiday(datetime.datetime.fromtimestamp(timestamp - j * 24 * 60 * 60)):
            j += 1
            continue
        res.append({
            'date': date,
            'score': get_daily_news_emotion_score(stock_code, date)
        })

        i += 1
        j += 1
    # 倒置，从前往后排
    res.reverse()
    return res


def get_news_emotion_list(stock_code: str):
    """
    根据股票代码获取已经分析出情绪的新闻，如果新闻已经过了当天的交易时间，则属于下一个交易时间
    :param stock_code:
    :return:
    """
    mysql_connector = MySQLConnector(config['stock_news_crawler']['db_name'])
    mysql_connector.execute_sql(f'''
        select * from stock_news
        where stock_code='{stock_code}' and emotion != -2 and emotion != 0 and {int(time.time())} - time_stamp <= 864000
        order by time_stamp desc
    ''')
    mysql_connector.commit()
    res = {}
    news_list = mysql_connector.cursor.fetchall()
    # 获取按天的新闻总结
    daily_news_emotion_map = get_daily_news_emotion_map(stock_code)
    for news in news_list:
        real_news_time = time.localtime(news['time_stamp'])
        # 过了当前的交易时间就算作下一天
        if real_news_time.tm_hour >= 15:
            real_news_time = time.localtime(news['time_stamp'] + 24 * 60 * 60)
        news_time = time.strftime('%Y-%m-%d', real_news_time)
        if res.get(news_time) is None:
            if daily_news_emotion_map.get(news_time) is None:
                daily_emotion = '本日暂无总结'
            else:
                daily_emotion = daily_news_emotion_map[news_time]
            res[news_time] = {'daily_emotion': daily_emotion, 'news': []}
        res[news_time]['news'].append({
            'news_title': news['news_title'],
            'news_link': news['news_link'],
            'news_time': time.strftime('%Y-%m-%d %H:%M', time.localtime(news['time_stamp'])),
            'emotion': news['emotion']
        })
    mysql_connector.close()
    return res


def get_daily_news_emotion_map(stock_code):
    """
    获取按天的新闻情绪总结列表
    :param stock_code:
    :return:
    """
    mysql_connector = MySQLConnector(config['stock_news_crawler']['db_name'])
    mysql_connector.execute_sql(f'''
        select * from news_emotion
        where stock_code='{stock_code}'
    ''')
    mysql_connector.commit()
    res = {}
    news_list = mysql_connector.cursor.fetchall()
    for news_emotion in news_list:
        res[news_emotion['news_time']] = news_emotion['emotion']
    return res
