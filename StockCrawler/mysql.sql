create database stock;
use stock;

create table stock_news (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    stock_code VARCHAR(10) NOT NULL,
    time_scamp INTEGER NOT NULL,
    news_title VARCHAR(200),
    news_content VARCHAR(5000),
    news_link VARCHAR(200)
)