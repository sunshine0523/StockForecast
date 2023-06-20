"""
将新闻数据导出为json
"""
import json
import time

import yaml

from db_utils import MySQLConnector


def init_config():
    with open('config.yaml', encoding='utf-8') as f:
        _config = yaml.load(f.read(), Loader=yaml.FullLoader)
    return _config


config = init_config()


def get_emotion(emotion):
    if emotion == 1:
        return 'Positive'
    elif emotion == -1:
        return 'Negative'
    return 'None'


def get_news_emotion_list(news_type: int = -1):
    """
    根据股票代码获取已经分析出情绪的新闻，如果新闻已经过了当天的交易时间，则属于下一个交易时间
    :param news_type: 如果类型为-1，表示查询所有来源的新闻
    :param stock_code:
    :return:
    """
    mysql_connector = MySQLConnector(config['stock_news_crawler']['db_name'])
    if -1 == news_type:
        mysql_connector.execute_sql(f'''
            select * from stock_news
            where emotion != -2
            order by time_stamp desc
        ''')
    else:
        mysql_connector.execute_sql(f'''
            select * from stock_news
            where emotion != -2 and type = {news_type}
            order by time_stamp desc
        ''')
    mysql_connector.commit()
    res = []
    news_list = mysql_connector.cursor.fetchall()
    # 获取按天的新闻总结
    for news in news_list:
        real_news_time = time.localtime(news['time_stamp'])
        # 过了当前的交易时间就算作下一天
        if real_news_time.tm_hour >= 15:
            real_news_time = time.localtime(news['time_stamp'] + 24 * 60 * 60)
        news_time = time.strftime('%Y-%m-%d', real_news_time)
        res.append({
            'news_title': news['news_title'],
            'news_link': news['news_link'],
            'news_time': news_time,
            'emotion': get_emotion(news['emotion'])
        })
        # if len(res) >= 100:
        #     break
    mysql_connector.close()
    return res


if __name__ == '__main__':
    data = get_news_emotion_list(-1)
    print(f'total size: {len(data)}')
    with open("news_emotion_10k.json", 'w', encoding='utf-8') as write_f:
        json.dump(data, write_f, indent=4, ensure_ascii=False)

