import uvicorn


def start():
    """Launched with `poetry run start` at root level"""
    uvicorn.run(
        "whale_googleanalytics.server.app:app", host="0.0.0.0", port=8000, reload=True
    )


def pytest():
    """Launched with `poetry run start` at root level"""
    from whale_googleanalytics.server.app import pytest

    app = pytest()
    return app
