FROM python:3.9.7

RUN mkdir /cpm_etl_script && \
    mkdir /cpm_etl
WORKDIR /cpm_etl_script
ADD . /cpm_etl_script

RUN pip install -i https://pypi.douban.com/simple --upgrade pip && \
    pip3 install -i https://pypi.douban.com/simple -r requirements.txt

RUN apt-get update