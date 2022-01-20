import pytest
from module_placeholder.main import create_app


@pytest.fixture(scope='session')
def app():
    app = create_app()
    return app
