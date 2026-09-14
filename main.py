"""Application entry point: launches the Web UI server or interactive CLI."""

import argparse
import webbrowser
from src.settings import get_settings


def main() -> None:
    """Run Web UI server by default, or interactive CLI if requested."""
    parser = argparse.ArgumentParser(description="Futures Trading Assistant")
    parser.add_argument(
        "--cli", action="store_true", help="Launch interactive CLI instead of Web UI"
    )
    parser.add_argument("--host", default=None, help="Host to bind Web server")
    parser.add_argument("--port", type=int, default=None, help="Port to bind Web server")
    args = parser.parse_args()

    if args.cli:
        from src.cli import run

        run()
        return

    import uvicorn

    settings = get_settings()
    host = args.host or settings.api_host
    port = args.port or settings.api_port
    url = f"http://{host}:{port}"
    print(f"[*] Starting Futures Trading Assistant Web UI at {url}")
    try:
        webbrowser.open(url)
    except Exception as exc:
        print(f"[*] Could not open browser automatically: {exc}")
    uvicorn.run("src.api:app", host=host, port=port)


if __name__ == "__main__":
    main()