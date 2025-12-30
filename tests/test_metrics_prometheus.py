import time
import pytest
from prometheus_client import REGISTRY


@pytest.fixture
def prometheus_metrics():
    """Create a fresh PrometheusMetrics instance.

    Note: Prometheus client doesn't allow re-registering metrics with the same name,
    so we need to be careful about creating multiple instances in tests.
    We use a fresh import to work around singleton behavior.
    """
    # Unregister existing metrics to allow fresh creation
    collectors_to_remove = []
    for collector in REGISTRY._names_to_collectors.values():
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

    from app.metrics.prometheus import PrometheusMetrics
    return PrometheusMetrics()


class TestPrometheusMetricsCounters:
    """Test counter increment methods."""

    def test_inc_requests_increments_counter(self, prometheus_metrics):
        initial = prometheus_metrics.get_metrics_summary()["http_requests"]["value"]
        prometheus_metrics.inc_requests()
        new_value = prometheus_metrics.get_metrics_summary()["http_requests"]["value"]
        assert new_value == initial + 1

    def test_inc_successful_increments_counter(self, prometheus_metrics):
        initial = prometheus_metrics.get_metrics_summary()["http_successful_request"]["value"]
        prometheus_metrics.inc_successful()
        new_value = prometheus_metrics.get_metrics_summary()["http_successful_request"]["value"]
        assert new_value == initial + 1

    def test_inc_4xx_increments_counter(self, prometheus_metrics):
        initial = prometheus_metrics.get_metrics_summary()["http_4xx_errors"]["value"]
        prometheus_metrics.inc_4xx()
        new_value = prometheus_metrics.get_metrics_summary()["http_4xx_errors"]["value"]
        assert new_value == initial + 1

    def test_inc_5xx_increments_counter(self, prometheus_metrics):
        initial = prometheus_metrics.get_metrics_summary()["http_5xx_errors"]["value"]
        prometheus_metrics.inc_5xx()
        new_value = prometheus_metrics.get_metrics_summary()["http_5xx_errors"]["value"]
        assert new_value == initial + 1

    def test_multiple_increments(self, prometheus_metrics):
        initial = prometheus_metrics.get_metrics_summary()["http_requests"]["value"]
        prometheus_metrics.inc_requests()
        prometheus_metrics.inc_requests()
        prometheus_metrics.inc_requests()
        new_value = prometheus_metrics.get_metrics_summary()["http_requests"]["value"]
        assert new_value == initial + 3


class TestPrometheusMetricsHistogram:
    """Test histogram timing methods."""

    def test_time_request_context_manager_records_duration(self, prometheus_metrics):
        with prometheus_metrics.time_request():
            time.sleep(0.01)  # 10ms

        summary = prometheus_metrics.get_metrics_summary()
        # Find the count bucket
        count_bucket = next(
            b for b in summary["histogram_buckets"]
            if b["name"] == "request_processing_seconds_count"
        )
        assert count_bucket["value"] >= 1

    def test_time_request_decorator_records_duration(self, prometheus_metrics):
        @prometheus_metrics.time_request_decorator()
        def slow_function():
            time.sleep(0.01)
            return "done"

        result = slow_function()
        assert result == "done"

        summary = prometheus_metrics.get_metrics_summary()
        count_bucket = next(
            b for b in summary["histogram_buckets"]
            if b["name"] == "request_processing_seconds_count"
        )
        assert count_bucket["value"] >= 1

    def test_time_request_records_in_correct_bucket(self, prometheus_metrics):
        # Record a very fast operation (should fall in small bucket)
        with prometheus_metrics.time_request():
            pass  # instant

        summary = prometheus_metrics.get_metrics_summary()
        # The smallest bucket (0.005s) should have the count
        small_bucket = next(
            b for b in summary["histogram_buckets"]
            if b["le"] == "0.005"
        )
        assert small_bucket["value"] >= 1

    def test_histogram_sum_increases(self, prometheus_metrics):
        initial_sum = next(
            b for b in prometheus_metrics.get_metrics_summary()["histogram_buckets"]
            if b["name"] == "request_processing_seconds_sum"
        )["value"]

        with prometheus_metrics.time_request():
            time.sleep(0.01)

        new_sum = next(
            b for b in prometheus_metrics.get_metrics_summary()["histogram_buckets"]
            if b["name"] == "request_processing_seconds_sum"
        )["value"]

        assert new_sum > initial_sum


class TestPrometheusMetricsSummary:
    """Test get_metrics_summary method."""

    def test_get_metrics_summary_returns_dict(self, prometheus_metrics):
        summary = prometheus_metrics.get_metrics_summary()
        assert isinstance(summary, dict)

    def test_get_metrics_summary_has_required_keys(self, prometheus_metrics):
        summary = prometheus_metrics.get_metrics_summary()
        required_keys = [
            "http_successful_request",
            "http_requests",
            "http_4xx_errors",
            "http_5xx_errors",
            "histogram_buckets"
        ]
        for key in required_keys:
            assert key in summary

    def test_get_metrics_summary_counter_structure(self, prometheus_metrics):
        summary = prometheus_metrics.get_metrics_summary()
        counter = summary["http_requests"]
        assert "name" in counter
        assert "value" in counter
        assert isinstance(counter["value"], float)

    def test_get_metrics_summary_histogram_structure(self, prometheus_metrics):
        summary = prometheus_metrics.get_metrics_summary()
        buckets = summary["histogram_buckets"]
        assert isinstance(buckets, list)
        assert len(buckets) > 0

        # Check bucket structure
        for bucket in buckets:
            assert "name" in bucket
            assert "le" in bucket
            assert "value" in bucket
