#!/bin/bash
source venv/bin/activate
exec gunicorn -b :5000 --timeout 90 --worker-class=gevent --access-logfile - --error-logfile - prom-metrics-app:app
