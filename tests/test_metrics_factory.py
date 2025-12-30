import pytest


class TestGetMetricsBackend:
    """Test the metrics backend factory function."""

    def test_returns_prometheus_by_default(self, monkeypatch):
        monkeypatch.delenv("METRICS_BACKEND", raising=False)

        from app.metrics import get_metrics_backend
        from app.metrics.prometheus import PrometheusMetrics

        backend = get_metrics_backend()
        assert isinstance(backend, PrometheusMetrics)

    def test_returns_prometheus_when_configured(self, prometheus_env):
        from app.metrics import get_metrics_backend
        from app.metrics.prometheus import PrometheusMetrics

        backend = get_metrics_backend()
        assert isinstance(backend, PrometheusMetrics)

    def test_returns_otel_when_configured(self, otel_env):
        from app.metrics import get_metrics_backend
        from app.metrics.otel import OTelMetrics

        backend = get_metrics_backend()
        assert isinstance(backend, OTelMetrics)

    def test_returns_singleton(self, prometheus_env):
        from app.metrics import get_metrics_backend

        backend1 = get_metrics_backend()
        backend2 = get_metrics_backend()
        assert backend1 is backend2

    def test_case_insensitive_backend_selection(self, monkeypatch):
        monkeypatch.setenv("METRICS_BACKEND", "PROMETHEUS")

        from app.metrics import get_metrics_backend
        from app.metrics.prometheus import PrometheusMetrics

        backend = get_metrics_backend()
        assert isinstance(backend, PrometheusMetrics)

    def test_otel_case_insensitive(self, monkeypatch):
        monkeypatch.setenv("METRICS_BACKEND", "OTEL")
        monkeypatch.setenv("OTEL_EXPORTER", "console")

        from app.metrics import get_metrics_backend
        from app.metrics.otel import OTelMetrics

        backend = get_metrics_backend()
        assert isinstance(backend, OTelMetrics)


class TestGetBackendType:
    """Test the get_backend_type helper function."""

    def test_returns_prometheus_by_default(self, monkeypatch):
        monkeypatch.delenv("METRICS_BACKEND", raising=False)

        from app.metrics import get_backend_type

        assert get_backend_type() == "prometheus"

    def test_returns_configured_value(self, monkeypatch):
        monkeypatch.setenv("METRICS_BACKEND", "otel")

        from app.metrics import get_backend_type

        assert get_backend_type() == "otel"

    def test_returns_lowercase(self, monkeypatch):
        monkeypatch.setenv("METRICS_BACKEND", "OTEL")

        from app.metrics import get_backend_type

        assert get_backend_type() == "otel"


class TestMetricsBackendInterface:
    """Test that both backends implement the same interface."""

    def test_prometheus_has_required_methods(self, prometheus_env):
        from app.metrics import get_metrics_backend

        backend = get_metrics_backend()
        assert hasattr(backend, 'inc_requests')
        assert hasattr(backend, 'inc_successful')
        assert hasattr(backend, 'inc_4xx')
        assert hasattr(backend, 'inc_5xx')
        assert hasattr(backend, 'time_request')
        assert hasattr(backend, 'time_request_decorator')
        assert hasattr(backend, 'get_metrics_summary')

    def test_otel_has_required_methods(self, otel_env):
        from app.metrics import get_metrics_backend

        backend = get_metrics_backend()
        assert hasattr(backend, 'inc_requests')
        assert hasattr(backend, 'inc_successful')
        assert hasattr(backend, 'inc_4xx')
        assert hasattr(backend, 'inc_5xx')
        assert hasattr(backend, 'time_request')
        assert hasattr(backend, 'time_request_decorator')
        assert hasattr(backend, 'get_metrics_summary')

    def test_methods_are_callable(self, prometheus_env):
        from app.metrics import get_metrics_backend

        backend = get_metrics_backend()
        assert callable(backend.inc_requests)
        assert callable(backend.inc_successful)
        assert callable(backend.inc_4xx)
        assert callable(backend.inc_5xx)
        assert callable(backend.time_request)
        assert callable(backend.time_request_decorator)
        assert callable(backend.get_metrics_summary)
