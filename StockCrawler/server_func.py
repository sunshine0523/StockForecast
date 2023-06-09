import datetime
import re
import time

import pymongo
import yaml

import stock_info_crawler
import stock_news_crawler
from db_utils import MongoConnector, MySQLConnector
from chinese_calendar import is_holiday


def init_config():
    with open('config.yaml', encoding='utf-8') as f:
        _config = yaml.load(f.read(), Loader=yaml.FullLoader)
    return _config


config = init_config()


def get_stock_list(query: str):
    """
    获取股票列表
    :param query:
    :return:
    """
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
        })
    mongo_connector.client.close()
    return res


def get_stock_info(stock_code: str):
    """
    获取指定股票的信息
    :param stock_code:
    :return:
    """
    mongo_connector = MongoConnector(
        config['stock_info_crawler']['db_name'],
        config['stock_info_crawler']['collection_name']
    )
    res = [info for info in mongo_connector.find_by_filter(m_filter={'ts_code': stock_code}).limit(1)]
    mongo_connector.client.close()
    if len(res) == 0:
        return {}
    return {
        'ts_code': res[0]['ts_code'],
        'name': res[0]['name'],
        'industry': res[0]['industry'],
        'fullname': res[0]['fullname'],
        'enname': res[0]['enname'],
        'list_date': res[0]['list_date']
    }


def refresh_stock_news(stock_code: str, page_count: int = 10, news_type: int = 1):
    """
    刷新新闻列表
    :param news_type: 爬取的源，1新浪财经 2股吧
    :param stock_code:
    :param page_count:
    :return:
    """
    if 1 == news_type:
        stock_news_crawler.crawl_sina(
            stock_code=stock_code,
            db_name=config['stock_news_crawler']['db_name'],
            table_name=config['stock_news_crawler']['table_name'],
            page_count=page_count
        )
    elif 2 == news_type:
        stock_news_crawler.crawl_guba(
            stock_code=stock_code,
            db_name=config['stock_news_crawler']['db_name'],
            table_name=config['stock_news_crawler']['table_name'],
            page_count=page_count
        )


def get_stock_news_list(query: str, news_type: int = 1):
    """
    获取股票新闻列表
    :param news_type:
    :param query:
    :return:
    """
    mysql_connector = MySQLConnector(config['stock_news_crawler']['db_name'])
    mysql_connector.execute_sql(f'''
        select * from stock_news
        where stock_code='{query}' and type = {news_type}
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


def get_stock_news_list_by_page(stock_code: str, page: int, page_count: int, news_type: int = 1):
    """
    分页获取股票新闻列表
    :param page_count: 每页容量
    :param page: 第几页，从1开始
    :param news_type:
    :param stock_code:
    :return:
    """
    page = page - 1
    mysql_connector = MySQLConnector(config['stock_news_crawler']['db_name'])
    mysql_connector.execute_sql(f'''
        select * from stock_news
        where stock_code='{stock_code}' and type = {news_type}
        order by time_stamp desc
        limit {page * page_count},{page_count}
    ''')
    mysql_connector.commit()
    res = []
    news_list = mysql_connector.cursor.fetchall()
    for news in news_list:
        res.append({
            'id': news['id'],
            'news_title': news['news_title'],
            'news_link': news['news_link'],
            'time': time.strftime('%Y-%m-%d %H:%M', time.localtime(news['time_stamp']))
        })
    mysql_connector.close()
    return res


def get_news_count(stock_code: str, news_type: int = -1):
    """
    获取新闻条数，供分页器使用
    :param stock_code:
    :param news_type:
    :return:
    """
    mysql_connector = MySQLConnector(config['stock_news_crawler']['db_name'])
    if -1 == news_type:
        mysql_connector.execute_sql(f'''
            select count(*) as sum from stock_news
            where stock_code='{stock_code}'
        ''')
    else:
        mysql_connector.execute_sql(f'''
            select count(*) as sum from stock_news
            where stock_code='{stock_code}' and type = {news_type}
        ''')
    mysql_connector.commit()
    res = [i for i in mysql_connector.cursor.fetchall()]
    mysql_connector.close()
    return res[0]['sum']


def get_has_emotion_news_count(stock_code: str, news_type: int = -1):
    """
    获取含有情绪的新闻条数，供分页器使用
    :param stock_code:
    :param news_type:
    :return:
    """
    mysql_connector = MySQLConnector(config['stock_news_crawler']['db_name'])
    if -1 == news_type:
        mysql_connector.execute_sql(f'''
            select count(*) as sum from stock_news
            where stock_code='{stock_code}' and emotion != -2 and emotion != 0
        ''')
    else:
        mysql_connector.execute_sql(f'''
            select count(*) as sum from stock_news
            where stock_code='{stock_code}' and type = {news_type} and emotion != -2 and emotion != 0
        ''')
    mysql_connector.commit()
    res = [i for i in mysql_connector.cursor.fetchall()]
    mysql_connector.close()
    return res[0]['sum']


def get_has_emotion_score_news_count(stock_code: str, news_type: int = -1):
    """
    获取含有情绪分数的新闻条数，供分页器使用
    :param stock_code:
    :param news_type:
    :return:
    """
    mysql_connector = MySQLConnector(config['stock_news_crawler']['db_name'])
    if -1 == news_type:
        mysql_connector.execute_sql(f'''
            select count(*) as sum from stock_news
            where stock_code='{stock_code}' and emotion_score != -999 and emotion_score != 0
        ''')
    else:
        mysql_connector.execute_sql(f'''
            select count(*) as sum from stock_news
            where stock_code='{stock_code}' and type = {news_type} and emotion_score != -999 and emotion_score != 0
        ''')
    mysql_connector.commit()
    res = [i for i in mysql_connector.cursor.fetchall()]
    mysql_connector.close()
    return res[0]['sum']


def delete_stock_news(stock_code: str, from_date: str, to_date: str, news_type: int = -1):
    """
    删除日期范围内的新闻
    :param stock_code:
    :param from_date:
    :param to_date:
    :param news_type:
    :return:
    """
    mysql_connector = MySQLConnector(config['stock_news_crawler']['db_name'])
    if -1 == news_type:
        mysql_connector.execute_sql(f'''
            delete from stock_news
            where stock_code='{stock_code}' and time_stamp >= {from_date} and time_stamp <= {to_date}
        ''')
    else:
        mysql_connector.execute_sql(f'''
            delete from stock_news
            where stock_code='{stock_code}' and time_stamp >= {from_date} and time_stamp <= {to_date} and type={news_type}
        ''')
    mysql_connector.commit()
    mysql_connector.close()


def get_stock_has_news_list():
    """
    获取已经有新闻的股票名称，来作为推荐列表
    :return:
    """
    mysql_connector = MySQLConnector(config['stock_news_crawler']['db_name'])
    mysql_connector.execute_sql(f'''
        select stock_code from stock_news
        group by stock_code
    ''')
    mysql_connector.commit()
    stock_list = mysql_connector.cursor.fetchall()
    res = []
    mongo_connector = MongoConnector(
        config['stock_info_crawler']['db_name'],
        config['stock_info_crawler']['collection_name']
    )
    for stock_code in stock_list:
        stock_code = stock_code['stock_code']
        stock_info = [i for i in mongo_connector.find_by_filter(m_filter={'ts_code': stock_code}).limit(1)]
        if len(stock_info) != 0:
            res.append({
                'stock_code': stock_code,
                'name': stock_info[0]['name']
            })
    mysql_connector.close()
    mongo_connector.client.close()
    return res


def get_daily_news_emotion_score(stock_code: str, cur_date, last_date, news_type: int = -1):
    """
    获取指定日期的新闻整体情绪分数
    :param last_date: 上一个交易日，取这一天的股价
    :param news_type:
    :param stock_code:
    :param cur_date: 本股票交易日，取这一天的新闻和前一天的新闻
    :return:
    """
    mysql_connector = MySQLConnector(config['stock_news_crawler']['db_name'])
    timestamp = int(time.mktime(time.strptime(cur_date, '%Y%m%d')))
    start_time = timestamp - (24 + 9) * 60 * 60
    end_time = timestamp + 15 * 60 * 60

    if -1 == news_type:
        mysql_connector.execute_sql(f'''
            select emotion from stock_news
            where stock_code='{stock_code}' and time_stamp >= {start_time} and time_stamp <= {end_time} and emotion != 0 and emotion != -2
        ''')
    else:
        mysql_connector.execute_sql(f'''
            select emotion from stock_news
            where stock_code='{stock_code}' and 
                time_stamp >= {start_time} and 
                time_stamp <= {end_time} and 
                emotion != 0 and 
                emotion != -2 and 
                type = {news_type}
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

    # 返回的结果应该加权。首先，我们需要分数/新闻条数来得到平均分。然后，获取前一天的收盘价，规定每25价格对应单位1.
    mongo_connector = MongoConnector(
        config['stock_daily_crawler']['db_name'],
        config['stock_daily_crawler']['collection_name']
    )
    # 获取要预测的上一个交易日的股价
    daily_info = [i for i in mongo_connector.find_by_filter(m_filter={'ts_code': stock_code, 'trade_date': last_date}).limit(1)]
    if len(daily_info) == 0:
        # 如果数据库中没有股票，则不进行预测
        return 0
    else:
        price = daily_info[0]['close']
    mongo_connector.client.close()
    return daily_emotion_score / len(news_list) * price / 25


def get_daily_news_emotion_score_v2(stock_code: str, cur_date, last_date, news_type: int = -1):
    """
    获取指定日期的新闻整体情绪分数
    使用LLM给新闻的打分来评估分数
    :param last_date: 上一个交易日，取这一天的股价
    :param news_type:
    :param stock_code:
    :param cur_date: 本股票交易日，取这一天的新闻和前一天的新闻
    :return:
    """
    mysql_connector = MySQLConnector(config['stock_news_crawler']['db_name'])
    timestamp = int(time.mktime(time.strptime(cur_date, '%Y%m%d')))
    start_time = timestamp - (24 + 9) * 60 * 60
    end_time = timestamp + 15 * 60 * 60

    if -1 == news_type:
        mysql_connector.execute_sql(f'''
            select emotion_score from stock_news
            where stock_code='{stock_code}' and 
            time_stamp >= {start_time} and 
            time_stamp <= {end_time} and 
            emotion_score != 0 and 
            emotion_score > -998
        ''')
    else:
        mysql_connector.execute_sql(f'''
            select emotion_score from stock_news
            where stock_code='{stock_code}' and 
                time_stamp >= {start_time} and 
                time_stamp <= {end_time} and 
                emotion_score != 0 and 
                emotion_score > -998
                type = {news_type}
        ''')
    mysql_connector.commit()
    daily_emotion_score = 0
    news_list = mysql_connector.cursor.fetchall()
    # 如果当天没有新闻，则不进行预测
    if len(news_list) == 0:
        return 0
    for news in news_list:
        daily_emotion_score += news['emotion_score']
    mysql_connector.close()

    # 返回的结果应该加权。首先，我们需要分数/新闻条数来得到平均分。然后，获取前一天的收盘价，规定每100价格对应单位1.
    mongo_connector = MongoConnector(
        config['stock_daily_crawler']['db_name'],
        config['stock_daily_crawler']['collection_name']
    )
    # 获取要预测的上一个交易日的股价
    daily_info = [i for i in mongo_connector.find_by_filter(m_filter={'ts_code': stock_code, 'trade_date': last_date}).limit(1)]
    if len(daily_info) == 0:
        # 如果数据库中没有股票，则不进行预测
        return 0
    else:
        price = daily_info[0]['close']
    mongo_connector.client.close()
    return daily_emotion_score / len(news_list) * price / 100


def get_news_emotion_list_by_page(stock_code: str, page: int, page_count: int, news_type: int = -1):
    """
    根据股票代码获取已经分析出情绪的新闻，如果新闻已经过了当天的交易时间，则属于下一个交易时间
    :param page_count: 每页数量
    :param page: 当前页
    :param news_type: 如果类型为-1，表示查询所有来源的新闻
    :param stock_code:
    :return:
    """
    page = page - 1
    mysql_connector = MySQLConnector(config['stock_news_crawler']['db_name'])
    if -1 == news_type:
        mysql_connector.execute_sql(f'''
            select * from stock_news
            where stock_code='{stock_code}' and emotion != -2 and emotion != 0
            order by time_stamp desc
            limit {page * page_count},{page_count}
        ''')
    else:
        mysql_connector.execute_sql(f'''
            select * from stock_news
            where stock_code='{stock_code}' and 
                emotion != -2 and emotion != 0
                and type = {news_type}
            order by time_stamp desc
            limit {page * page_count},{page_count}
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
            'id': news['id'],
            'news_title': news['news_title'],
            'news_link': news['news_link'],
            'news_time': time.strftime('%Y-%m-%d %H:%M', time.localtime(news['time_stamp'])),
            'emotion': news['emotion']
        })
    mysql_connector.close()
    return res


def get_news_emotion_list_by_page_v2(stock_code: str, page: int, page_count: int, news_type: int = -1):
    """
    获取股票新闻情感分数信息，按日分组
    这个分数不是预测分数，是情感分数分析(Beta)通过语言模型分析出来的分数
    :param page_count:
    :param page:
    :param news_type: -1表示查询所有来源
    :param stock_code:
    :return:
    """
    page = page - 1
    mysql_connector = MySQLConnector(config['stock_news_crawler']['db_name'])
    if -1 == news_type:
        mysql_connector.execute_sql(f'''
            select * from stock_news
            where stock_code='{stock_code}' and emotion_score != -999 and emotion_score != 0
            order by time_stamp desc
            limit {page * page_count},{page_count}
        ''')
    else:
        mysql_connector.execute_sql(f'''
            select * from stock_news
            where stock_code='{stock_code}' and 
                emotion_score != -999 and emotion_score != 0
                and type = {news_type}
            order by time_stamp desc
            limit {page * page_count},{page_count}
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
            'id': news['id'],
            'news_title': news['news_title'],
            'news_link': news['news_link'],
            'news_time': time.strftime('%Y-%m-%d %H:%M', time.localtime(news['time_stamp'])),
            'emotion_score': news['emotion_score']
        })
    mysql_connector.close()
    return res


def get_last_days_daily_news_emotion_score(stock_code: str, days_count: int, news_type: int = -1, use_llm_score: bool = False):
    """
    经过考虑，预测使用的新闻应该为本天产生的新闻
    获取end_date前days_count天数的股票预测情况
    :param use_llm_score: 是否使用LLM给新闻的打分（-5 ~ +5）来预测
    :param news_type: -1为获取全部新闻类型
    :param stock_code:
    :param days_count: 预测的天数
    :return:
    """
    # 如何判断预测结束的日期？获取数据库中最新的日K数据，end_date为它的下一天
    mongo_connector = MongoConnector(
        config['stock_daily_crawler']['db_name'],
        config['stock_daily_crawler']['collection_name']
    )
    # 获取最新一日的股价
    daily_info = [i for i in
                  mongo_connector.find_by_filter(m_filter={'ts_code': stock_code}, m_sort=[("trade_date", pymongo.DESCENDING)]).limit(1)]
    # 如果数据库中一条数据都没有，那么无法预测
    if len(daily_info) == 0:
        return
    end_date = daily_info[0]['trade_date']
    timestamp = int(time.mktime(time.strptime(end_date, '%Y%m%d')))
    res = []
    i = 0
    j = 0
    forcast_date_list = [time.strftime('%Y%m%d', time.localtime(timestamp + 24 * 60 * 60))]
    # forcast_date_list中的第一个应该是未来，所以就应该end_date的后一天
    while i < days_count + 1:
        if is_holiday(datetime.datetime.fromtimestamp(timestamp - j * 24 * 60 * 60)):
            j += 1
            continue
        forcast_date_list.append(time.strftime('%Y%m%d', time.localtime(timestamp - j * 24 * 60 * 60)))
        i += 1
        j += 1
    i = 0
    print(forcast_date_list)
    while i < days_count:
        if use_llm_score:
            score = get_daily_news_emotion_score_v2(stock_code, forcast_date_list[i], forcast_date_list[i + 1], news_type)
        else:
            score = get_daily_news_emotion_score(stock_code, forcast_date_list[i], forcast_date_list[i + 1], news_type)
        res.append({
            'date': forcast_date_list[i],
            'score': score
        })
        i += 1
    # 倒置，从前往后排
    res.reverse()
    mongo_connector.client.close()
    return res


def get_daily_news_emotion_map(stock_code):
    """
    获取按天的新闻情绪总结列表
    这里面可能有重复天数的总结，但是新的会把旧的覆盖掉
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
    mysql_connector.close()
    return res


def update_news_emotion(news_id: int, emotion: int):
    """
    更新新闻情绪
    :param news_id:
    :param emotion:
    :return:
    """
    if emotion not in [-1, 0, 1]:
        return False, 'emotion invalid'
    else:
        mysql_connector = MySQLConnector(config['stock_news_crawler']['db_name'])
        mysql_connector.execute_sql(f'''
            update stock_news
            set emotion={emotion}
            where id={news_id}
        ''')
        mysql_connector.commit()
        mysql_connector.close()
        return True, ''


def get_stock_daily_list(stock_code: str):
    """
    获取股票日K
    :param stock_code:
    :return:
    """
    return stock_info_crawler.crawl_stock_daily(stock_code)


def get_stock_current_info(stock_code: str):
    """
    获取股票的实时信息
    :param stock_code:
    :return:
    """
    return stock_info_crawler.crawl_stock_current(stock_code)


def get_stock_minute(stock_code: str):
    """
    获取股票的分时信息
    :param stock_code:
    :return:
    """
    return stock_info_crawler.crawl_stock_minute(stock_code)