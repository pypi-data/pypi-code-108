
from dataclasses import dataclass
from typing import Optional

import pytest

from daacla import Daacla, table


@dataclass
@table(key='url')
class WebPage:
    url: str
    visits: int = 0
    rate: float = 0.0
    closed: bool = False
    title: Optional[str] = None


@pytest.fixture()
def db() -> Daacla:
    db = Daacla.in_memory()
    db.truncate(WebPage)
    return db


def test_column_typing(db: Daacla) -> None:
    assert db.meta(WebPage).columns['url'] == 'TEXT PRIMARY KEY'
    assert db.meta(WebPage).columns['visits'] == 'INTEGER'
    assert db.meta(WebPage).columns['rate'] == 'REAL'
    assert db.meta(WebPage).columns['closed'] == 'BOOL'


def test_table_name(db: Daacla) -> None:
    assert db.meta(WebPage).table == 'web_page'
    instance = WebPage(url='http://example.com/')
    assert db.meta(instance).table == 'web_page'


def test_insert(db: Daacla) -> None:
    google_url = 'http://google.com/'
    google_page = WebPage(url=google_url)

    db.insert(google_page)

    assert db.get(WebPage, key=google_url) == google_page


def test_update(db: Daacla) -> None:
    apple_url = 'http://apple.com/'
    apple = WebPage(url=apple_url)

    db.insert(apple)

    apple.visits = 11
    assert db.update(apple)

    got = db.get(WebPage, key=apple_url)
    assert got is not None
    assert got == apple
    assert got.visits == apple.visits
    assert got.visits == 11


def test_update_is_not_insert(db: Daacla) -> None:
    apple_url = 'http://apple.com/'
    apple = WebPage(url=apple_url)

    assert not db.update(apple)

    got = db.get(WebPage, key=apple_url)
    assert got is None


def test_upsert_is_also_insert(db: Daacla) -> None:
    apple_url = 'http://apple.com/'
    apple = WebPage(url=apple_url)

    assert db.upsert(apple)

    got = db.get(WebPage, key=apple_url)
    assert got is not None
    assert got == apple

    apple.visits = 22

    assert db.upsert(apple)

    got = db.get(WebPage, key=apple_url)
    assert got is not None
    assert got == apple
    assert got.visits == apple.visits
    assert got.visits == 22


def test_exists(db: Daacla) -> None:
    apple_url = 'http://apple.com/'

    assert not db.exists(WebPage, key=apple_url)

    apple = WebPage(url=apple_url)
    db.insert(apple)

    assert db.exists(WebPage, key=apple_url)


def test_delete(db: Daacla) -> None:
    apple_url = 'http://apple.com/'

    assert not db.delete(WebPage, key=apple_url)

    apple = WebPage(url=apple_url)
    db.insert(apple)

    assert db.exists(WebPage, key=apple_url)

    assert db.delete(WebPage, key=apple.url)

    assert not db.exists(WebPage, key=apple_url)


def test_select(db: Daacla) -> None:
    db.insert(WebPage(url='apple'))
    assert len(list(db.select(WebPage, 'true'))) == 1

    db.insert(WebPage(url='pear', visits=1))
    db.insert(WebPage(url='orange', visits=3))
    db.insert(WebPage(url='berry', visits=3))

    assert len(list(db.select(WebPage, 'visits = ?', 3))) == 2
    assert list(db.select(WebPage, 'visits = ?', 1))[0].url == 'pear'
    assert len(list(db.select(WebPage, 'visits = ?', 5))) == 0
