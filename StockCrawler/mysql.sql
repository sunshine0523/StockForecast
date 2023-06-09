create database stock;
use stock;

# type 类型， 1表示新浪财经 2表示股吧
create table stock_news (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    stock_code VARCHAR(10) NOT NULL,
    time_stamp INTEGER NOT NULL,
    news_title VARCHAR(200),
    news_content VARCHAR(5000),
    news_link VARCHAR(200),
    emotion INTEGER NOT NULL DEFAULT -2,
    # 情绪分数用于情感分数分析(Beta)功能，-999表示该新闻还未分析，-998表示该新闻分析失败 -5~+5表示情绪打分，-5情绪最负面，+5情绪最正面
    emotion_score INTEGER NOT NULL DEFAULT -999,
    type INTEGER NOT NULL DEFAULT 0
);

create index stock_news_stock_code_index
    on stock.stock_news (stock_code);

create table news_emotion (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    stock_code VARCHAR(10) NOT NULL,
    news_time VARCHAR(10) NOT NULL,
    emotion VARCHAR(1000) NOT NULL
);

create index news_emotion_stock_code_index
    on stock.news_emotion (stock_code);