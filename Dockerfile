FROM python:3.6-alpine

WORKDIR /app

RUN pip install https://github.com/ryanvin/SpiderKeeper/archive/master.zip

EXPOSE 5000