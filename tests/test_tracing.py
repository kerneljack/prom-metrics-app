import pytest


class TestCreateSpanExporter:
    """Test the span exporter factory function."""

    def test_returns_console_exporter_by_default(self, monkeypatch):
        monkeypatch.delenv("OTEL_EXPORTER", raising=False)

        from app.tracing import _create_span_exporter
        from opentelemetry.sdk.trace.export import ConsoleSpanExporter

        exporter = _create_span_exporter()
        assert isinstance(exporter, ConsoleSpanExporter)

    def test_returns_console_exporter_when_configured(self, monkeypatch):
        monkeypatch.setenv("OTEL_EXPORTER", "console")

        from app.tracing import _create_span_exporter
        from opentelemetry.sdk.trace.export import ConsoleSpanExporter

        exporter = _create_span_exporter()
        assert isinstance(exporter, ConsoleSpanExporter)

    def test_returns_otlp_exporter_when_configured(self, otlp_env):
        from app.tracing import _create_span_exporter
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

        exporter = _create_span_exporter()
        assert isinstance(exporter, OTLPSpanExporter)

    def test_case_insensitive_exporter_selection(self, monkeypatch):
        monkeypatch.setenv("OTEL_EXPORTER", "CONSOLE")

        from app.tracing import _create_span_exporter
        from opentelemetry.sdk.trace.export import ConsoleSpanExporter

        exporter = _create_span_exporter()
        assert isinstance(exporter, ConsoleSpanExporter)


class TestOTLPConfiguration:
    """Test OTLP exporter configuration."""

    def test_uses_default_endpoint(self, monkeypatch):
        monkeypatch.setenv("OTEL_EXPORTER", "otlp")
        monkeypatch.delenv("OTEL_EXPORTER_OTLP_ENDPOINT", raising=False)
        monkeypatch.setenv("OTEL_EXPORTER_OTLP_INSECURE", "true")

        from app.tracing import _create_span_exporter
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

        exporter = _create_span_exporter()
        assert isinstance(exporter, OTLPSpanExporter)

    def test_uses_configured_endpoint(self, monkeypatch):
        monkeypatch.setenv("OTEL_EXPORTER", "otlp")
        monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://custom:4317")
        monkeypatch.setenv("OTEL_EXPORTER_OTLP_INSECURE", "true")

        from app.tracing import _create_span_exporter
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

        exporter = _create_span_exporter()
        assert isinstance(exporter, OTLPSpanExporter)

    def test_insecure_default_true(self, monkeypatch):
        monkeypatch.setenv("OTEL_EXPORTER", "otlp")
        monkeypatch.delenv("OTEL_EXPORTER_OTLP_INSECURE", raising=False)

        from app.tracing import _create_span_exporter
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

        # Should not raise - insecure defaults to true
        exporter = _create_span_exporter()
        assert isinstance(exporter, OTLPSpanExporter)

    def test_insecure_can_be_disabled(self, monkeypatch):
        monkeypatch.setenv("OTEL_EXPORTER", "otlp")
        monkeypatch.setenv("OTEL_EXPORTER_OTLP_INSECURE", "false")

        from app.tracing import _create_span_exporter
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

        exporter = _create_span_exporter()
        assert isinstance(exporter, OTLPSpanExporter)


class TestInitTracing:
    """Test the init_tracing function."""

    def test_instruments_flask_app(self, monkeypatch):
        monkeypatch.setenv("OTEL_EXPORTER", "console")

        from flask import Flask
        from app.tracing import init_tracing

        app = Flask(__name__)
        # Should not raise
        init_tracing(app)

    def test_sets_tracer_provider(self, monkeypatch):
        monkeypatch.setenv("OTEL_EXPORTER", "console")

        from flask import Flask
        from opentelemetry import trace
        from app.tracing import init_tracing

        app = Flask(__name__)
        init_tracing(app)

        provider = trace.get_tracer_provider()
        assert provider is not None
