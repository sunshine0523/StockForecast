import datetime
import time

from db_utils import MySQLConnector
import requests
from bs4 import BeautifulSoup


def crawl_sina(
    stock_code: str,
    db_name: str = 'stock',
    table_name: str = 'stock_news',
    page_count: int = 10
):
    """
    爬取新浪财经的指定股票新闻信息并存储到数据库中
    在执行爬虫前应该确保数据库和表已经存在，脚本不负责判断该部分内容
    来源：新浪财经-行情中心
    :param stock_code: 股票代码，格式如：000001.SZ
    :param db_name: 数据库名
    :param table_name: 表名
    :param page_count: 爬取的页数，默认为10页
    :return:
    """
    mysql_connector = MySQLConnector(db_name)

    # 对于新浪财经，接受的股票代码格式如：sz000001，需要预处理
    sina_stock_code = ''.join(stock_code.split('.').__reversed__()).casefold()
    base_url = 'https://vip.stock.finance.sina.com.cn/corp/view/vCB_AllNewsStock.php'

    # 获取数据库中新闻时间最新一条数据，用以比对时间
    mysql_connector.execute_sql(f'''
        select time_stamp from {table_name}
        where stock_code='{stock_code}' and type = 1
        order by time_stamp desc
        limit 1
    ''')
    mysql_connector.commit()
    last_time_stamp = mysql_connector.cursor.fetchone()
    if last_time_stamp is None:
        last_time_stamp = -1
    else:
        last_time_stamp = last_time_stamp['time_stamp']
    try:
        for page in range(page_count):
            res = requests.get(f'{base_url}?symbol={sina_stock_code}&Page={page + 1}')
            soup = BeautifulSoup(res.text, 'html.parser')
            date_list = soup.find('div', attrs={'class': 'datelist'}).find('ul').__str__().split('<br/>')
            for news in date_list:
                soup = BeautifulSoup(news, 'html.parser')
                a_tag = soup.find('a')
                if a_tag is not None:
                    link = a_tag['href']
                    news_title = a_tag.text
                    soup.a.clear()
                    news_time = soup.get_text(separator=' ', strip=True)
                    time_array = time.strptime(news_time, '%Y-%m-%d %H:%M')
                    time_stamp = int(time.mktime(time_array))
                    # 如发现数据库的时间已经大于当前时间，则停止爬取
                    if last_time_stamp >= time_stamp:
                        mysql_connector.close()
                        return
                    mysql_connector.execute_sql(f'''
                        insert into {table_name}(
                            stock_code, time_stamp, news_title, news_content, news_link, type
                        ) values
                        ('{stock_code}', {time_stamp}, '{news_title}', '', '{link}', 1)
                    ''')
                    mysql_connector.db.commit()
            time.sleep(1)
    except Exception as e:
        print(e)

    mysql_connector.close()


def crawl_guba(
    stock_code: str,
    db_name: str = 'stock',
    table_name: str = 'stock_news',
    page_count: int = 10
):
    """
    爬取股吧网友评论，因为某些新闻并不能代表实际走势，看股吧评论也许能够了解真实情况...
    :param stock_code:
    :param db_name:
    :param table_name:
    :param page_count:
    :return:
    """
    mysql_connector = MySQLConnector(db_name)

    # 对于股吧，接受的股票代码格式如：000001，需要预处理
    guba_stock_code = ''.join(stock_code.split('.')[0])
    base_url = f'http://guba.eastmoney.com/o/list,{guba_stock_code}'

    # 获取数据库中新闻时间最新一条数据，用以比对时间
    mysql_connector.execute_sql(f'''
            select time_stamp from {table_name}
            where stock_code='{stock_code}' and type = 2
            order by time_stamp desc
            limit 1
        ''')
    mysql_connector.commit()
    last_time_stamp = mysql_connector.cursor.fetchone()
    if last_time_stamp is None:
        last_time_stamp = -1
    else:
        last_time_stamp = last_time_stamp['time_stamp']

    for page in range(page_count):
        print(f'爬取第{page}页')
        try:
            res = requests.get(f'{base_url},f_{page + 1}.html')
            soup = BeautifulSoup(res.text, 'html.parser')
            for news in soup.find_all('div', attrs={'class': 'articleh'}):
                try:
                    news_title = news.find('a').text
                    news_link = news.find('a')['href']
                    if news_link.startswith('//'):
                        news_link = 'https:' + news_link
                    else:
                        news_link = 'http://guba.eastmoney.com/o' + news_link
                    time_str = news.find('span', attrs={'class': 'l5 a5'}).text
                    time_array = time.strptime(datetime.datetime.now().year.__str__() + '-' + time_str, '%Y-%m-%d %H:%M')
                    time_stamp = int(time.mktime(time_array))
                    # 如发现数据库的时间已经大于当前时间，则停止爬取，
                    # 但是股吧第一页总有奇奇怪怪的置顶不按时间排列，所以第一页不判断
                    if page != 0 and last_time_stamp >= time_stamp:
                        print(f'到达上次时间 {last_time_stamp}，当前爬取到的时间 {time_stamp} {time_str}')
                        mysql_connector.close()
                        return
                    mysql_connector.execute_sql(f'''
                                                insert into {table_name}(
                                                    stock_code, time_stamp, news_title, news_content, news_link, type
                                                ) values
                                                ('{stock_code}', {time_stamp}, '{news_title}', '', '{news_link}', 2)
                                            ''')
                    mysql_connector.db.commit()
                except Exception as e:
                    print(e)
                    continue
            time.sleep(1)
        except Exception as e:
            print(e)
            continue
    mysql_connector.close()


if __name__ == '__main__':
    crawl_guba('002594.SZ')