FROM python:3.12-alpine3.19

WORKDIR /app

COPY crontab /etc/cron.d/crontab

COPY app.py /app/app.py

COPY requirements.txt /app/requirements.txt

RUN pip3 install -r requirements.txt

ENV TZ="Asia/Baghdad"

RUN /usr/bin/crontab /etc/cron.d/crontab

RUN crontab /etc/cron.d/crontab

RUN chmod 0644 /etc/cron.d/crontab

CMD ["crond", "-f"]

#CMD ["python3","app.py"]
