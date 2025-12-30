# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2025-12-30

### Added

- **Unit test suite** - 51 tests covering both metrics backends and tracing
  - Prometheus metrics tests (counters, histogram, summary structure)
  - OTel metrics tests (counters, histogram, summary structure)
  - Factory function tests (backend selection, singleton, interface compliance)
  - Tracing tests (exporter selection, OTLP configuration)
- **requirements-dev.txt** - Development dependencies (pytest, pytest-cov, pytest-mock)
- **Testing section in README** - Documentation for running tests

## [0.2.0] - 2025-12-30

### Added

- **Configurable metrics backend** - Switch between Prometheus and OpenTelemetry via `METRICS_BACKEND` environment variable
- **OpenTelemetry metrics support** - New OTel metrics implementation alongside existing Prometheus
- **OTLP exporter for metrics** - Export metrics to OpenTelemetry Collector via gRPC
- **OTLP exporter for tracing** - Export traces to OpenTelemetry Collector via gRPC
- **Metrics abstraction layer** (`app/metrics/`) with clean interface for swapping backends
- **Comprehensive README** - Full documentation with usage examples, deployment guides, and architecture overview
- **CLAUDE.md** - AI assistant context file for Claude Code

### Changed

- Refactored metrics from `app/main/metrics.py` to `app/metrics/` module with abstract interface
- Routes now use `metrics.time_request_decorator()` instead of Prometheus-specific decorators
- Error handlers updated to use abstract metrics interface
- `/metrics` endpoint now only available when using Prometheus backend
- Tracing configuration moved to use shared `OTEL_EXPORTER` environment variable

### Removed

- `app/main/metrics.py` - Replaced by `app/metrics/` module

## [0.1.0] - 2025-01-01

### Added

- Initial Flask application with Prometheus metrics instrumentation
- OpenTelemetry tracing with Flask auto-instrumentation
- Prometheus metrics: request counters, error counters, request duration histogram
- `/metrics` endpoint for Prometheus scraping
- `/view_metrics` web UI to display current metric values
- `/do_task` endpoint to simulate long-running tasks
- Docker support with gunicorn and gevent workers
- Kubernetes Helm chart for cluster deployment
- Basic error handlers for 404 and 500 responses

[0.2.1]: https://github.com/kerneljack/prom-metrics-app/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/kerneljack/prom-metrics-app/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/kerneljack/prom-metrics-app/releases/tag/v0.1.0
