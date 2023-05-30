import time

import server_func
import stock_news_crawler


def stock_news_crawler_test():
    # stock_news_crawler.crawler_sina('002594.SZ', page_count=1)
    print(server_func.get_news_emotion_list('002594.SZ'))


if __name__ == '__main__':
    stock_news_crawler_test()
    print(int(time.time()))