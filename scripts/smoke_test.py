from __future__ import annotations

import argparse
import sys

import httpx

_COURSE = "smoke"
_TEXT = "La photosynthèse transforme la lumière en énergie chimique."
_QUESTION = "Que fait la photosynthèse ?"


def run_smoke(base_url: str, api_key: str | None = None, timeout: float = 10.0) -> bool:
    headers = {"X-API-Key": api_key} if api_key else {}
    with httpx.Client(base_url=base_url, headers=headers, timeout=timeout) as client:
        health = client.get("/healthz")
        if health.status_code != 200:
            sys.stderr.write(f"healthz KO: {health.status_code}\n")
            return False

        ingest = client.post(
            "/ingest",
            json={"course_id": _COURSE, "source": "smoke.txt", "text": _TEXT},
        )
        if ingest.status_code != 201:
            sys.stderr.write(f"ingest KO: {ingest.status_code}\n")
            return False

        ask = client.post("/ask", json={"course_id": _COURSE, "question": _QUESTION})
        if ask.status_code != 200 or not ask.json().get("grounded"):
            sys.stderr.write(f"ask KO: {ask.status_code} {ask.text}\n")
            return False

    sys.stdout.write("SMOKE PASSED\n")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test Sherpa")
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--api-key", default=None)
    args = parser.parse_args()
    return 0 if run_smoke(args.base_url, args.api_key) else 1


if __name__ == "__main__":
    raise SystemExit(main())
