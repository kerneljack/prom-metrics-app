# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Flask demonstration application showing Prometheus metrics instrumentation patterns, designed for containerized and Kubernetes deployments.

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally (development)
python prom-metrics-app.py
# App runs on http://localhost:5000

# Run with gunicorn (production)
gunicorn -b :5000 --timeout 90 --worker-class=gevent --access-logfile - --error-logfile - prom-metrics-app:app

# Docker
docker build -t prom-metrics-app .
docker run -p 5000:5000 prom-metrics-app

# Kubernetes (Helm)
helm install prom-metrics-app ./helm/prom-metrics-app/
```

## Architecture

**Flask App Factory Pattern**: The application uses `create_app()` in `app/__init__.py` which:
- Registers blueprints (`main` for routes, `errors` for error handlers)
- Wraps the WSGI app with Prometheus middleware to expose `/metrics` endpoint
- Configures logging (stdout for containers, rotating file otherwise)

**Metrics Instrumentation** (`app/main/metrics.py`):
- `Metrics` class centralizes all Prometheus instruments
- Counters: `http_successful_request`, `http_requests`, `http_4xx_errors`, `http_5xx_errors`
- Histogram: `http_request_time_histogram` for request duration tracking

**Route Metrics Pattern** (`app/main/routes.py`):
- Use `@metrics.http_request_time_histogram.time()` decorator for timing
- Call `metrics.http_successful_request.inc()` and `metrics.http_requests.inc()` on success
- Error handlers in `app/errors/handlers.py` increment error counters

**Key Endpoints**:
- `/` and `/index` - Home page
- `/view_metrics` - Displays current metrics values
- `/do_task` - Simulates 5-second task (demonstrates histogram timing)
- `/metrics` - Prometheus scrape endpoint (handled by middleware)

## Configuration

Environment variables loaded via `python-dotenv`:
- `LOG_TO_STDOUT` - Set to enable stdout logging (for containers)
- Configuration class in `config.py`
