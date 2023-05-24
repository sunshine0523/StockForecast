import stock_news_crawler


def stock_nes_crawler_test():
    stock_news_crawler.crawler_sina('002594.SZ', page_count=1)


if __name__ == '__main__':
    stock_nes_crawler_test()