from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from app.config import Settings


def setup_tracing(endpoint: str | None = None):
    # Manually create a fresh, uncached Settings instance
    settings = Settings()

    if endpoint is None:
        endpoint = settings.otel_exporter_otlp_endpoint

    # Resource can be required for some backends, e.g. Jaeger
    # If resource wouldn't be set - traces wouldn't appears in Jaeger
    resource = Resource(attributes={"service.name": settings.otel_service_name})

    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)

    otlp_exporter = OTLPSpanExporter(endpoint=endpoint, insecure=True)

    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)

    RequestsInstrumentor().instrument()

    return tracer_provider
