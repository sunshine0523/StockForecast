create database stock;
use stock;

create table stock_news (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    stock_code VARCHAR(10) NOT NULL,
    time_stamp INTEGER NOT NULL,
    news_title VARCHAR(200),
    news_content VARCHAR(5000),
    news_link VARCHAR(200),
    emotion INTEGER NOT NULL DEFAULT -2
);

create index stock_news_stock_code_index
    on stock.stock_news (stock_code);

create table news_emotion (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    stock_code VARCHAR(10) NOT NULL,
    news_time VARCHAR(10) NOT NULL,
    emotion VARCHAR(200) NOT NULL
);

create index news_emotion_stock_code_index
    on stock.news_emotion (stock_code);