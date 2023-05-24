FROM continuumio/anaconda3

COPY ./requirements.txt /tmp/conda/requirements.txt
COPY . /tmp/StockCrawler

EXPOSE 5000

RUN conda config --add channels https://mirrors.bfsu.edu.cn/anaconda/pkgs/free/
RUN conda config --add channels https://mirrors.bfsu.edu.cn/anaconda/pkgs/main
RUN conda config --add channels https://mirrors.bfsu.edu.cn/anaconda/cloud/conda-forge/
    #设置搜索时显示通道地址
RUN conda config --set show_channel_urls yes

RUN pip install -r /tmp/StockCrawler/requirements.txt