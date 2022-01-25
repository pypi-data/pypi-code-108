import pytest

from .client import InfluenceClient


@pytest.mark.django_db
def test_init(client):
    _ = InfluenceClient()
