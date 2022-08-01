FROM python:slim

RUN useradd prom-metrics-app

WORKDIR /home/prom-metrics-app

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn gevent

COPY app app
COPY prom-metrics-app.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP prom-metrics-app.py

RUN chown -R prom-metrics-app:prom-metrics-app ./
USER prom-metrics-app

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
