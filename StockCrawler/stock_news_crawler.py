import time

from db_utils import MySQLConnector
import requests
from bs4 import BeautifulSoup


def crawler_sina(
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
    mysql_connector.execute_sql('''
        select time_scamp from stock_news
        order by time_scamp desc
        limit 1
    ''')
    mysql_connector.db.commit()
    last_time_scamp = mysql_connector.cursor.fetchone()[0]
    if last_time_scamp is None:
        last_time_scamp = -1
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
                    if last_time_scamp >= time_stamp:
                        mysql_connector.close()
                        return
                    mysql_connector.execute_sql(f'''
                        insert into stock_news(
                            stock_code, time_scamp, news_title, news_content, news_link
                        ) values 
                        ('{stock_code}', {time_stamp}, '{news_title}', '', '{link}')
                    ''')
                    mysql_connector.db.commit()
            time.sleep(1)
    except Exception as e:
        print(e)

    mysql_connector.close()