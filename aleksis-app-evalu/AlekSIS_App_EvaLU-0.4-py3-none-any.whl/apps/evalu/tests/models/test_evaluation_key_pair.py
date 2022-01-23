import pytest

from aleksis.apps.evalu.models import EvaluationKeyPair

pytestmark = pytest.mark.django_db


def test_create():
    pair = EvaluationKeyPair.create("test")
    assert pair.pk is not None


def test_encryption():
    pair1 = EvaluationKeyPair.create("test")
    pair2 = EvaluationKeyPair.create("test2")

    assert pair1.encrypt("foo")
    assert pair1.encrypt("foo") != pair1.encrypt("foo")
    assert pair1.encrypt("foo") != pair1.encrypt("baz")
    assert pair1.encrypt("foo") != pair2.encrypt("foo")


def test_decryption():
    pair1 = EvaluationKeyPair.create("test")
    pair2 = EvaluationKeyPair.create("test2")

    assert pair1.decrypt(pair1.encrypt("foo"), "test").decode() == "foo"
    assert pair1.decrypt(pair1.encrypt("baz"), "test").decode() == "baz"

    with pytest.raises(ValueError):
        pair1.decrypt(pair1.encrypt("foo"), "test2")

    with pytest.raises(ValueError):
        pair1.decrypt(pair2.encrypt("foo"), "test")


def test_unlock():
    pair1 = EvaluationKeyPair.create("test")

    assert pair1.test("test")

    with pytest.raises(ValueError):
        pair1.test("test2")


def test_str():
    pair1 = EvaluationKeyPair.create("test")
    assert "Key" in str(pair1)


def test_broken():
    pair1 = EvaluationKeyPair()
    assert pair1.get_public_key() is None
    assert pair1.get_private_key("foo") is None
