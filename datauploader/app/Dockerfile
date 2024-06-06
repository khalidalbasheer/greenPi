FROM python:3.12-slim

WORKDIR /app

COPY . /app

RUN pip3 install --upgrade pip

RUN pip3 install --upgrade setuptools

RUN pip3 install grpcio==1.62.0

#RUN apk update && apk add python3-dev gcc libc-dev libffi-dev \
#  && pip3 install -r requirements.txt \
#  && apk del python3-dev gcc libc-dev libffi-dev --purge \
#  && rm -rf /var/cache/apk/*

RUN pip3 install -r requirements.txt

ENV TZ="Asia/Baghdad"

CMD ["python3","app.py"]
