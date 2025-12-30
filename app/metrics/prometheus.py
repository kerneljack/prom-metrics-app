from contextlib import contextmanager
from typing import Iterator
from prometheus_client import Counter, Histogram

from app.metrics.base import MetricsBackend


class PrometheusMetrics(MetricsBackend):
    """Prometheus-based metrics implementation using prometheus-client."""

    def __init__(self):
        self._http_successful_request = Counter(
            "http_successful_request", "Successful HTTP counts"
        )
        self._http_requests = Counter("http_requests", "Total HTTP counts")
        self._http_4xx_errors = Counter("http_error_4xx", "4xx error count")
        self._http_5xx_errors = Counter("http_error_5xx", "5xx error count")
        self._http_request_time_histogram = Histogram(
            "request_processing_seconds", "Time spent processing request (Histogram)"
        )

    def inc_requests(self) -> None:
        self._http_requests.inc()

    def inc_successful(self) -> None:
        self._http_successful_request.inc()

    def inc_4xx(self) -> None:
        self._http_4xx_errors.inc()

    def inc_5xx(self) -> None:
        self._http_5xx_errors.inc()

    @contextmanager
    def time_request(self) -> Iterator[None]:
        with self._http_request_time_histogram.time():
            yield

    def get_metrics_summary(self) -> dict:
        """Return current metric values for display."""
        histogram_buckets = []
        for sample in self._http_request_time_histogram._child_samples():
            histogram_buckets.append({
                "name": f"{self._http_request_time_histogram._name}{sample.name}",
                "le": sample.labels.get("le", ""),
                "value": sample.value,
            })

        return {
            "http_successful_request": {
                "name": self._http_successful_request._name,
                "value": self._http_successful_request._value.get(),
            },
            "http_requests": {
                "name": self._http_requests._name,
                "value": self._http_requests._value.get(),
            },
            "http_4xx_errors": {
                "name": self._http_4xx_errors._name,
                "value": self._http_4xx_errors._value.get(),
            },
            "http_5xx_errors": {
                "name": self._http_5xx_errors._name,
                "value": self._http_5xx_errors._value.get(),
            },
            "histogram_buckets": histogram_buckets,
        }
