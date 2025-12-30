import os
import time
from contextlib import contextmanager
from typing import Iterator

from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import Resource, SERVICE_NAME

from app.metrics.base import MetricsBackend


def _create_metric_reader():
    """Create the appropriate metric reader based on configuration.

    Environment variables:
        OTEL_EXPORTER: 'console' (default) or 'otlp'
        OTEL_EXPORTER_OTLP_ENDPOINT: OTLP endpoint URL (default: http://localhost:4317)
        OTEL_EXPORTER_OTLP_INSECURE: Set to 'true' for insecure connection
    """
    exporter_type = os.environ.get("OTEL_EXPORTER", "console").lower()

    if exporter_type == "otlp":
        from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

        endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
        insecure = os.environ.get("OTEL_EXPORTER_OTLP_INSECURE", "true").lower() == "true"

        exporter = OTLPMetricExporter(endpoint=endpoint, insecure=insecure)
    else:
        exporter = ConsoleMetricExporter()

    return PeriodicExportingMetricReader(exporter, export_interval_millis=10000)


class OTelMetrics(MetricsBackend):
    """OpenTelemetry-based metrics implementation."""

    def __init__(self, service_name: str = "prom-metrics-app"):
        resource = Resource(attributes={SERVICE_NAME: service_name})

        reader = _create_metric_reader()
        provider = MeterProvider(resource=resource, metric_readers=[reader])
        metrics.set_meter_provider(provider)

        self._meter = metrics.get_meter(__name__)

        self._http_successful_request = self._meter.create_counter(
            name="http_successful_request",
            description="Successful HTTP counts",
            unit="1",
        )
        self._http_requests = self._meter.create_counter(
            name="http_requests",
            description="Total HTTP counts",
            unit="1",
        )
        self._http_4xx_errors = self._meter.create_counter(
            name="http_error_4xx",
            description="4xx error count",
            unit="1",
        )
        self._http_5xx_errors = self._meter.create_counter(
            name="http_error_5xx",
            description="5xx error count",
            unit="1",
        )
        self._http_request_time_histogram = self._meter.create_histogram(
            name="request_processing_seconds",
            description="Time spent processing request",
            unit="s",
        )

        # Track values locally for get_metrics_summary since OTel doesn't expose values directly
        self._counters = {
            "http_successful_request": 0,
            "http_requests": 0,
            "http_4xx_errors": 0,
            "http_5xx_errors": 0,
        }
        self._histogram_values = []

    def inc_requests(self) -> None:
        self._http_requests.add(1)
        self._counters["http_requests"] += 1

    def inc_successful(self) -> None:
        self._http_successful_request.add(1)
        self._counters["http_successful_request"] += 1

    def inc_4xx(self) -> None:
        self._http_4xx_errors.add(1)
        self._counters["http_4xx_errors"] += 1

    def inc_5xx(self) -> None:
        self._http_5xx_errors.add(1)
        self._counters["http_5xx_errors"] += 1

    @contextmanager
    def time_request(self) -> Iterator[None]:
        start_time = time.perf_counter()
        try:
            yield
        finally:
            duration = time.perf_counter() - start_time
            self._http_request_time_histogram.record(duration)
            self._histogram_values.append(duration)

    def get_metrics_summary(self) -> dict:
        """Return current metric values for display."""
        # Calculate histogram buckets similar to Prometheus
        buckets = [0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0]
        histogram_buckets = []

        for le in buckets:
            count = sum(1 for v in self._histogram_values if v <= le)
            histogram_buckets.append({
                "name": "request_processing_seconds_bucket",
                "le": str(le),
                "value": float(count),
            })

        # +Inf bucket
        histogram_buckets.append({
            "name": "request_processing_seconds_bucket",
            "le": "+Inf",
            "value": float(len(self._histogram_values)),
        })

        # Count and sum
        histogram_buckets.append({
            "name": "request_processing_seconds_count",
            "le": "",
            "value": float(len(self._histogram_values)),
        })
        histogram_buckets.append({
            "name": "request_processing_seconds_sum",
            "le": "",
            "value": sum(self._histogram_values) if self._histogram_values else 0.0,
        })

        return {
            "http_successful_request": {
                "name": "http_successful_request",
                "value": float(self._counters["http_successful_request"]),
            },
            "http_requests": {
                "name": "http_requests",
                "value": float(self._counters["http_requests"]),
            },
            "http_4xx_errors": {
                "name": "http_error_4xx",
                "value": float(self._counters["http_4xx_errors"]),
            },
            "http_5xx_errors": {
                "name": "http_error_5xx",
                "value": float(self._counters["http_5xx_errors"]),
            },
            "histogram_buckets": histogram_buckets,
        }
