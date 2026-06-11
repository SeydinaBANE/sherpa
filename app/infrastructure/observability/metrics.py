from __future__ import annotations

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

REQUEST_COUNT = Counter(
    "sherpa_http_requests_total",
    "Nombre total de requêtes HTTP",
    ["method", "path", "status"],
)

REQUEST_LATENCY = Histogram(
    "sherpa_http_request_duration_seconds",
    "Durée des requêtes HTTP en secondes",
    ["method", "path"],
)


def observe_request(method: str, path: str, status: int, duration_seconds: float) -> None:
    REQUEST_COUNT.labels(method=method, path=path, status=str(status)).inc()
    REQUEST_LATENCY.labels(method=method, path=path).observe(duration_seconds)


def render_metrics() -> tuple[bytes, str]:
    return generate_latest(), CONTENT_TYPE_LATEST
