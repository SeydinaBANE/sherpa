from __future__ import annotations

import uvicorn

from app.config import get_settings
from app.presentation.api import create_app

app = create_app()


def main() -> None:
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=not settings.is_production,
    )


if __name__ == "__main__":
    main()
