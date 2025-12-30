import os
import pytest


@pytest.fixture(autouse=True)
def reset_metrics_singleton():
    """Reset the metrics singleton and Prometheus registry before each test."""
    import app.metrics
    app.metrics._metrics_instance = None

    # Clear Prometheus registry to avoid duplicate metric errors
    from prometheus_client import REGISTRY
    collectors_to_remove = []
    for collector in list(REGISTRY._names_to_collectors.values()):
        if hasattr(collector, '_name') and collector._name in [
            'http_successful_request', 'http_requests',
            'http_error_4xx', 'http_error_5xx', 'request_processing_seconds'
        ]:
            collectors_to_remove.append(collector)

    for collector in collectors_to_remove:
        try:
            REGISTRY.unregister(collector)
        except Exception:
            pass

    yield

    app.metrics._metrics_instance = None


@pytest.fixture
def prometheus_env(monkeypatch):
    """Set environment for Prometheus backend."""
    monkeypatch.setenv("METRICS_BACKEND", "prometheus")
    monkeypatch.setenv("OTEL_EXPORTER", "console")


@pytest.fixture
def otel_env(monkeypatch):
    """Set environment for OTel backend."""
    monkeypatch.setenv("METRICS_BACKEND", "otel")
    monkeypatch.setenv("OTEL_EXPORTER", "console")


@pytest.fixture
def otlp_env(monkeypatch):
    """Set environment for OTLP export."""
    monkeypatch.setenv("OTEL_EXPORTER", "otlp")
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_INSECURE", "true")
