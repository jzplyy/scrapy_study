FROM python:3.9.7

RUN mkdir /cpm_spider && \
    mkdir /scrapyg
WORKDIR /cpm_spider
ADD . /cpm_spider

RUN pip install -i https://pypi.douban.com/simple --upgrade pip && \
    pip3 install -i https://pypi.douban.com/simple -r requirements.txt && \
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple uwsgi

RUN apt-get update