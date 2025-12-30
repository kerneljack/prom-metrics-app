# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Flask demonstration application showing Prometheus metrics and OpenTelemetry tracing instrumentation patterns, designed for containerized and Kubernetes deployments.

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
- Initializes OpenTelemetry tracing
- Registers blueprints (`main` for routes, `errors` for error handlers)
- Conditionally wraps WSGI app with Prometheus middleware (only when using Prometheus backend)
- Configures logging (stdout for containers, rotating file otherwise)

**Tracing** (`app/tracing.py`):
- OpenTelemetry with Flask auto-instrumentation
- Supports Console (default) or OTLP exporter via `OTEL_EXPORTER` env var
- All HTTP requests are automatically traced

**Metrics Abstraction** (`app/metrics/`):
- `base.py` - `MetricsBackend` abstract interface
- `prometheus.py` - Prometheus implementation using prometheus-client
- `otel.py` - OpenTelemetry implementation with console/OTLP export
- `__init__.py` - Factory function `get_metrics_backend()` selects backend based on config

**Metrics Interface Methods**:
- `inc_requests()`, `inc_successful()`, `inc_4xx()`, `inc_5xx()` - counters
- `time_request()` - context manager for timing
- `time_request_decorator()` - decorator for timing routes
- `get_metrics_summary()` - returns dict for `/view_metrics` display

**Route Metrics Pattern** (`app/main/routes.py`):
- Use `@metrics.time_request_decorator()` for timing
- Call `metrics.inc_successful()` and `metrics.inc_requests()` on success
- Error handlers in `app/errors/handlers.py` increment error counters

**Key Endpoints**:
- `/` and `/index` - Home page
- `/view_metrics` - Displays current metrics values
- `/do_task` - Simulates 5-second task (demonstrates histogram timing)
- `/metrics` - Prometheus scrape endpoint (only available with Prometheus backend)

## Configuration

Environment variables loaded via `python-dotenv`:
- `LOG_TO_STDOUT` - Set to enable stdout logging (for containers)
- `METRICS_BACKEND` - `prometheus` (default) or `otel`
- `OTEL_EXPORTER` - `console` (default) or `otlp`
- `OTEL_EXPORTER_OTLP_ENDPOINT` - OTLP collector URL (default: `http://localhost:4317`)
- `OTEL_EXPORTER_OTLP_INSECURE` - Skip TLS verification (default: `true`)

**Example configurations**:
```bash
# Prometheus metrics with console tracing (default)
python prom-metrics-app.py

# OTel metrics with console export
METRICS_BACKEND=otel python prom-metrics-app.py

# Full OTel with OTLP export to collector
METRICS_BACKEND=otel OTEL_EXPORTER=otlp OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4317 python prom-metrics-app.py
```
