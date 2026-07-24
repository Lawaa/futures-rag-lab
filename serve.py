"""Launch the FastAPI server with uvicorn.

Usage:
    uv run serve.py
"""

import uvicorn

from src.settings import get_settings


def main() -> None:
    settings = get_settings()
    uvicorn.run(
        "src.api:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False,
    )


if __name__ == "__main__":
    main()