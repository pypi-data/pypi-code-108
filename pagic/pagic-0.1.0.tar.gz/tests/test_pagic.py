import pytest
from flask import Flask

from pagic.page import Page, page
from pagic.pagic import Pagic


@page
class HomePage(Page):
    name = "home"
    path = "/"
    label = "Home"

    layout = "tests/base.j2"
    template = "tests/home.j2"


@pytest.fixture
def app():
    app = Flask(__name__)
    pagic = Pagic(app)
    pagic.register_pages("tests")
    return app


def test_home(app, client):
    # rules = list(app.url_map.iter_rules())
    res = client.get("/")
    assert res.status_code == 200


if __name__ == "__main__":
    _app = Flask(__name__)
    pagic = Pagic(_app)
    _app.run()
