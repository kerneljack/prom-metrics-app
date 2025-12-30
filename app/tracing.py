import os

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.instrumentation.flask import FlaskInstrumentor


def _create_span_exporter():
    """Create the appropriate span exporter based on configuration.

    Environment variables:
        OTEL_EXPORTER: 'console' (default) or 'otlp'
        OTEL_EXPORTER_OTLP_ENDPOINT: OTLP endpoint URL (default: http://localhost:4317)
        OTEL_EXPORTER_OTLP_INSECURE: Set to 'true' for insecure connection
    """
    exporter_type = os.environ.get("OTEL_EXPORTER", "console").lower()

    if exporter_type == "otlp":
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

        endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
        insecure = os.environ.get("OTEL_EXPORTER_OTLP_INSECURE", "true").lower() == "true"

        return OTLPSpanExporter(endpoint=endpoint, insecure=insecure)
    else:
        return ConsoleSpanExporter()


def init_tracing(app):
    """Initialize OpenTelemetry tracing.

    Uses OTEL_EXPORTER env var to select console (default) or otlp exporter.
    """
    resource = Resource(attributes={
        SERVICE_NAME: "prom-metrics-app"
    })
    provider = TracerProvider(resource=resource)
    processor = BatchSpanProcessor(_create_span_exporter())
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)

    FlaskInstrumentor().instrument_app(app)
