FROM python:3.12-slim
#FROM python:3.12-alpine3.19

WORKDIR /app

COPY . /app

RUN pip3 install -r requirements.txt

ENV TZ="Asia/Baghdad"

CMD ["python3","app.py"]
