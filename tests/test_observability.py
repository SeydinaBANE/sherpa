from __future__ import annotations

from httpx import AsyncClient


async def test_metrics_endpoint_exposes_prometheus(client: AsyncClient) -> None:
    response = await client.get("/metrics")
    assert response.status_code == 200
    assert "sherpa_http_requests_total" in response.text


async def test_request_id_is_returned_and_echoed(client: AsyncClient) -> None:
    generated = await client.get("/healthz")
    assert generated.headers.get("x-request-id")

    echoed = await client.get("/healthz", headers={"X-Request-ID": "trace-123"})
    assert echoed.headers["x-request-id"] == "trace-123"


async def test_request_is_counted(client: AsyncClient) -> None:
    await client.get("/healthz")
    metrics = await client.get("/metrics")
    assert 'sherpa_http_requests_total{method="GET",path="/healthz",status="200"}' in metrics.text
