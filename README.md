# Prometheus Metrics App

A Flask demonstration application showcasing observability instrumentation patterns with **Prometheus** and **OpenTelemetry**. Designed for learning, testing, and demonstrating metrics and tracing in containerized and Kubernetes environments.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Limitations](#limitations)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Prometheus Metrics Backend](#prometheus-metrics-backend)
  - [OpenTelemetry Metrics Backend](#opentelemetry-metrics-backend)
  - [OTLP Export to Collectors](#otlp-export-to-collectors)
- [Endpoints](#endpoints)
- [Deployment](#deployment)
  - [Docker](#docker)
  - [Kubernetes with Helm](#kubernetes-with-helm)
- [Testing](#testing)
- [Architecture](#architecture)
- [License](#license)

## Overview

This application demonstrates how to instrument a Python web application with industry-standard observability tools. It provides a practical example of:

- **Metrics collection** using either Prometheus client library or OpenTelemetry SDK
- **Distributed tracing** with OpenTelemetry and automatic Flask instrumentation
- **Flexible export options** including console output and OTLP protocol for production collectors

The app includes sample endpoints, making it ideal for testing and learning instrumentation best practices.

## Features

- **Dual metrics backends**: Switch between Prometheus and OpenTelemetry metrics via configuration
- **OpenTelemetry tracing**: Automatic instrumentation of all HTTP requests
- **Flexible exporters**: Console output for development, OTLP for production collectors
- **Prometheus `/metrics` endpoint**: Standard scrape endpoint when using Prometheus backend
- **Request timing histograms**: Track request duration distributions
- **Error rate tracking**: Separate counters for 4xx and 5xx errors
- **Web UI for metrics**: View current metric values at `/view_metrics`
- **Container-ready**: Includes Dockerfile with gunicorn for production deployments
- **Kubernetes-ready**: Helm chart included for easy cluster deployment
- **Clean abstraction layer**: Easy to extend with additional metrics backends

## Limitations

- **Demo application**: Not intended for production workloads; designed for learning and testing
- **Single service**: Does not demonstrate distributed tracing across multiple services
- **No persistent storage**: Metrics reset when the application restarts
- **Basic authentication**: No authentication or authorization implemented
- **Limited metrics**: Only includes basic HTTP metrics (requests, errors, latency)
- **No alerting**: Does not include alerting rules or configurations
- **OTel metrics view**: When using OTel backend, `/view_metrics` shows locally-tracked values (not exported aggregations)

## Quick Start

```bash
# Clone and install
git clone https://github.com/kerneljack/prom-metrics-app.git
cd prom-metrics-app
pip install -r requirements.txt

# Run with defaults (Prometheus metrics, console tracing)
python prom-metrics-app.py

# Visit http://localhost:5000
```

## Installation

### Prerequisites

- Python 3.9+
- pip

### Setup

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Dependencies

| Package | Purpose |
|---------|---------|
| Flask | Web framework |
| prometheus-client | Prometheus metrics instrumentation |
| opentelemetry-api | OpenTelemetry API |
| opentelemetry-sdk | OpenTelemetry SDK for traces and metrics |
| opentelemetry-instrumentation-flask | Automatic Flask instrumentation |
| opentelemetry-exporter-otlp-proto-grpc | OTLP exporter for collectors |
| python-dotenv | Environment variable management |

## Configuration

All configuration is done via environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `METRICS_BACKEND` | Metrics implementation: `prometheus` or `otel` | `prometheus` |
| `OTEL_EXPORTER` | Export destination: `console` or `otlp` | `console` |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP collector endpoint | `http://localhost:4317` |
| `OTEL_EXPORTER_OTLP_INSECURE` | Disable TLS for OTLP | `true` |
| `LOG_TO_STDOUT` | Enable stdout logging | Not set |

## Usage

### Prometheus Metrics Backend

The default configuration uses Prometheus client library for metrics. This exposes a standard `/metrics` endpoint for Prometheus to scrape.

```bash
# Start with Prometheus metrics (default)
python prom-metrics-app.py

# Or explicitly set
METRICS_BACKEND=prometheus python prom-metrics-app.py
```

**Scrape configuration for Prometheus:**

```yaml
scrape_configs:
  - job_name: 'prom-metrics-app'
    static_configs:
      - targets: ['localhost:5000']
    metrics_path: '/metrics'
```

**Available Prometheus metrics:**

| Metric | Type | Description |
|--------|------|-------------|
| `http_successful_request_total` | Counter | Successful HTTP requests |
| `http_requests_total` | Counter | Total HTTP requests |
| `http_error_4xx_total` | Counter | Client error responses |
| `http_error_5xx_total` | Counter | Server error responses |
| `request_processing_seconds` | Histogram | Request duration distribution |

### OpenTelemetry Metrics Backend

Use the OTel SDK for metrics when you want unified telemetry with tracing or when exporting to an OpenTelemetry Collector.

```bash
# OTel metrics with console output (for development/debugging)
METRICS_BACKEND=otel python prom-metrics-app.py
```

**Note:** When using the OTel backend, the `/metrics` endpoint is not available. Metrics are pushed to the configured exporter instead of being scraped.

### OTLP Export to Collectors

For production environments, export both traces and metrics to an OpenTelemetry Collector using OTLP:

```bash
# Export to local collector
METRICS_BACKEND=otel \
OTEL_EXPORTER=otlp \
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317 \
python prom-metrics-app.py

# Export to remote collector with TLS
METRICS_BACKEND=otel \
OTEL_EXPORTER=otlp \
OTEL_EXPORTER_OTLP_ENDPOINT=https://collector.example.com:4317 \
OTEL_EXPORTER_OTLP_INSECURE=false \
python prom-metrics-app.py
```

**Example OpenTelemetry Collector configuration:**

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317

exporters:
  prometheus:
    endpoint: "0.0.0.0:8889"
  jaeger:
    endpoint: "jaeger:14250"

service:
  pipelines:
    metrics:
      receivers: [otlp]
      exporters: [prometheus]
    traces:
      receivers: [otlp]
      exporters: [jaeger]
```

### Tracing Only (Prometheus Metrics + OTel Traces)

You can use Prometheus for metrics while still getting OTel tracing with OTLP export:

```bash
# Prometheus metrics + OTLP traces
METRICS_BACKEND=prometheus \
OTEL_EXPORTER=otlp \
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317 \
python prom-metrics-app.py
```

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Home page |
| `/index` | GET | Home page (alias) |
| `/view_metrics` | GET | Web UI showing current metric values |
| `/do_task` | GET | Simulates a 5-second task (for testing histograms) |
| `/metrics` | GET | Prometheus scrape endpoint (Prometheus backend only) |

## Deployment

### Docker

```bash
# Build the image
docker build -t prom-metrics-app .

# Run with default configuration
docker run -p 5000:5000 prom-metrics-app

# Run with OTel metrics and OTLP export
docker run -p 5000:5000 \
  -e METRICS_BACKEND=otel \
  -e OTEL_EXPORTER=otlp \
  -e OTEL_EXPORTER_OTLP_ENDPOINT=http://host.docker.internal:4317 \
  prom-metrics-app
```

The Docker image uses gunicorn with gevent workers for production-grade performance.

### Kubernetes with Helm

```bash
# Build and push image to your registry
docker build -t your-registry/prom-metrics-app:0.1.0 .
docker push your-registry/prom-metrics-app:0.1.0

# Update values.yaml with your image repository
# helm/prom-metrics-app/values.yaml:
#   image:
#     repository: your-registry/prom-metrics-app
#     tag: "0.1.0"

# Install the chart
helm install prom-metrics-app ./helm/prom-metrics-app/

# Install with custom values
helm install prom-metrics-app ./helm/prom-metrics-app/ \
  --set image.repository=your-registry/prom-metrics-app \
  --set image.tag=0.1.0

# Upgrade an existing release
helm upgrade prom-metrics-app ./helm/prom-metrics-app/
```

**Configure environment variables in Kubernetes:**

Add to your `values.yaml` or create a ConfigMap:

```yaml
# In deployment.yaml, add env vars:
env:
  - name: METRICS_BACKEND
    value: "otel"
  - name: OTEL_EXPORTER
    value: "otlp"
  - name: OTEL_EXPORTER_OTLP_ENDPOINT
    value: "http://otel-collector.monitoring:4317"
```

**Prometheus ServiceMonitor (if using Prometheus Operator):**

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: prom-metrics-app
spec:
  selector:
    matchLabels:
      app: prom-metrics-app
  endpoints:
    - port: http
      path: /metrics
      interval: 30s
```

## Testing

The project includes a comprehensive test suite covering both metrics backends and tracing.

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=app --cov-report=term-missing

# Run specific test file
pytest tests/test_metrics_prometheus.py -v
```

**Test Coverage:**

| Module | Tests | Description |
|--------|-------|-------------|
| `test_metrics_prometheus.py` | 13 | Prometheus counters, histogram, summary |
| `test_metrics_otel.py` | 15 | OTel counters, histogram, summary |
| `test_metrics_factory.py` | 12 | Backend factory, singleton, interface |
| `test_tracing.py` | 10 | Exporter selection, OTLP config |

## Architecture

```
prom-metrics-app/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── tracing.py           # OpenTelemetry tracing setup
│   ├── metrics/             # Metrics abstraction layer
│   │   ├── __init__.py      # Backend factory
│   │   ├── base.py          # Abstract interface
│   │   ├── prometheus.py    # Prometheus implementation
│   │   └── otel.py          # OpenTelemetry implementation
│   ├── main/                # Main blueprint
│   │   ├── __init__.py
│   │   └── routes.py        # Application routes
│   ├── errors/              # Error handlers
│   │   ├── __init__.py
│   │   └── handlers.py
│   └── templates/           # Jinja2 templates
├── tests/                   # Unit tests
│   ├── conftest.py          # Pytest fixtures
│   ├── test_metrics_prometheus.py
│   ├── test_metrics_otel.py
│   ├── test_metrics_factory.py
│   └── test_tracing.py
├── helm/                    # Kubernetes Helm chart
├── config.py                # Flask configuration
├── prom-metrics-app.py      # Application entry point
├── boot.sh                  # Container startup script
├── Dockerfile
├── requirements.txt
└── requirements-dev.txt     # Dev/test dependencies
```

**Key design decisions:**

- **Metrics abstraction**: The `MetricsBackend` interface allows swapping implementations without changing application code
- **Factory pattern**: `get_metrics_backend()` instantiates the correct backend based on configuration
- **Lazy imports**: OTLP exporters are imported only when needed to avoid unnecessary dependencies
- **Shared configuration**: Both tracing and metrics use the same `OTEL_EXPORTER` setting for consistency

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.