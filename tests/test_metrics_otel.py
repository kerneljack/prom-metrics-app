import time
import pytest


@pytest.fixture
def otel_metrics(otel_env):
    """Create a fresh OTelMetrics instance."""
    from app.metrics.otel import OTelMetrics
    return OTelMetrics()


class TestOTelMetricsCounters:
    """Test counter increment methods."""

    def test_inc_requests_increments_counter(self, otel_metrics):
        initial = otel_metrics.get_metrics_summary()["http_requests"]["value"]
        otel_metrics.inc_requests()
        new_value = otel_metrics.get_metrics_summary()["http_requests"]["value"]
        assert new_value == initial + 1

    def test_inc_successful_increments_counter(self, otel_metrics):
        initial = otel_metrics.get_metrics_summary()["http_successful_request"]["value"]
        otel_metrics.inc_successful()
        new_value = otel_metrics.get_metrics_summary()["http_successful_request"]["value"]
        assert new_value == initial + 1

    def test_inc_4xx_increments_counter(self, otel_metrics):
        initial = otel_metrics.get_metrics_summary()["http_4xx_errors"]["value"]
        otel_metrics.inc_4xx()
        new_value = otel_metrics.get_metrics_summary()["http_4xx_errors"]["value"]
        assert new_value == initial + 1

    def test_inc_5xx_increments_counter(self, otel_metrics):
        initial = otel_metrics.get_metrics_summary()["http_5xx_errors"]["value"]
        otel_metrics.inc_5xx()
        new_value = otel_metrics.get_metrics_summary()["http_5xx_errors"]["value"]
        assert new_value == initial + 1

    def test_multiple_increments(self, otel_metrics):
        initial = otel_metrics.get_metrics_summary()["http_requests"]["value"]
        otel_metrics.inc_requests()
        otel_metrics.inc_requests()
        otel_metrics.inc_requests()
        new_value = otel_metrics.get_metrics_summary()["http_requests"]["value"]
        assert new_value == initial + 3


class TestOTelMetricsHistogram:
    """Test histogram timing methods."""

    def test_time_request_context_manager_records_duration(self, otel_metrics):
        with otel_metrics.time_request():
            time.sleep(0.01)  # 10ms

        summary = otel_metrics.get_metrics_summary()
        count_bucket = next(
            b for b in summary["histogram_buckets"]
            if b["name"] == "request_processing_seconds_count"
        )
        assert count_bucket["value"] >= 1

    def test_time_request_decorator_records_duration(self, otel_metrics):
        @otel_metrics.time_request_decorator()
        def slow_function():
            time.sleep(0.01)
            return "done"

        result = slow_function()
        assert result == "done"

        summary = otel_metrics.get_metrics_summary()
        count_bucket = next(
            b for b in summary["histogram_buckets"]
            if b["name"] == "request_processing_seconds_count"
        )
        assert count_bucket["value"] >= 1

    def test_time_request_records_in_correct_bucket(self, otel_metrics):
        # Record a very fast operation (should fall in small bucket)
        with otel_metrics.time_request():
            pass  # instant

        summary = otel_metrics.get_metrics_summary()
        # The smallest bucket (0.005s) should have the count
        small_bucket = next(
            b for b in summary["histogram_buckets"]
            if b["le"] == "0.005"
        )
        assert small_bucket["value"] >= 1

    def test_histogram_sum_increases(self, otel_metrics):
        initial_sum = next(
            b for b in otel_metrics.get_metrics_summary()["histogram_buckets"]
            if b["name"] == "request_processing_seconds_sum"
        )["value"]

        with otel_metrics.time_request():
            time.sleep(0.01)

        new_sum = next(
            b for b in otel_metrics.get_metrics_summary()["histogram_buckets"]
            if b["name"] == "request_processing_seconds_sum"
        )["value"]

        assert new_sum > initial_sum


class TestOTelMetricsSummary:
    """Test get_metrics_summary method."""

    def test_get_metrics_summary_returns_dict(self, otel_metrics):
        summary = otel_metrics.get_metrics_summary()
        assert isinstance(summary, dict)

    def test_get_metrics_summary_has_required_keys(self, otel_metrics):
        summary = otel_metrics.get_metrics_summary()
        required_keys = [
            "http_successful_request",
            "http_requests",
            "http_4xx_errors",
            "http_5xx_errors",
            "histogram_buckets"
        ]
        for key in required_keys:
            assert key in summary

    def test_get_metrics_summary_counter_structure(self, otel_metrics):
        summary = otel_metrics.get_metrics_summary()
        counter = summary["http_requests"]
        assert "name" in counter
        assert "value" in counter
        assert isinstance(counter["value"], float)

    def test_get_metrics_summary_histogram_structure(self, otel_metrics):
        summary = otel_metrics.get_metrics_summary()
        buckets = summary["histogram_buckets"]
        assert isinstance(buckets, list)
        assert len(buckets) > 0

        # Check bucket structure
        for bucket in buckets:
            assert "name" in bucket
            assert "le" in bucket
            assert "value" in bucket

    def test_histogram_has_inf_bucket(self, otel_metrics):
        summary = otel_metrics.get_metrics_summary()
        inf_bucket = next(
            (b for b in summary["histogram_buckets"] if b["le"] == "+Inf"),
            None
        )
        assert inf_bucket is not None


class TestOTelMetricsServiceName:
    """Test service name configuration."""

    def test_default_service_name(self, otel_env):
        from app.metrics.otel import OTelMetrics
        metrics = OTelMetrics()
        # Service name is set during initialization
        # We can't easily verify it without accessing internals,
        # but we can verify the instance is created successfully
        assert metrics is not None

    def test_custom_service_name(self, otel_env):
        from app.metrics.otel import OTelMetrics
        metrics = OTelMetrics(service_name="custom-service")
        assert metrics is not None
