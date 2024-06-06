FROM python:3.12-alpine3.19

WORKDIR /app

COPY . /app

RUN apk update && apk add python3-dev gcc libc-dev libffi-dev \
  && pip3 install -r requirements.txt \
  && apk del python3-dev gcc libc-dev libffi-dev --purge \
  && rm -rf /var/cache/apk/*

ENV TZ="Asia/Baghdad"

CMD ["python3","app.py"]
