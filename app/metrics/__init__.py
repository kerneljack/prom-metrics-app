import os
from typing import Optional

from app.metrics.base import MetricsBackend

_metrics_instance: Optional[MetricsBackend] = None


def get_metrics_backend() -> MetricsBackend:
    """Factory function to get the configured metrics backend.

    Uses METRICS_BACKEND environment variable to determine which backend to use.
    Valid values: 'prometheus' (default), 'otel'
    """
    global _metrics_instance

    if _metrics_instance is not None:
        return _metrics_instance

    backend = os.environ.get("METRICS_BACKEND", "prometheus").lower()

    if backend == "otel":
        from app.metrics.otel import OTelMetrics
        _metrics_instance = OTelMetrics()
    else:
        from app.metrics.prometheus import PrometheusMetrics
        _metrics_instance = PrometheusMetrics()

    return _metrics_instance


def get_backend_type() -> str:
    """Return the configured backend type string."""
    return os.environ.get("METRICS_BACKEND", "prometheus").lower()
