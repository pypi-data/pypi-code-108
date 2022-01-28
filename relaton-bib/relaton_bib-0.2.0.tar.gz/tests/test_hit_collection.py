import pytest

from relaton_bib import Hit, HitCollection


@pytest.fixture(autouse=True)
def mock_pool_map(monkeypatch):
    monkeypatch.setattr("multiprocessing.pool.Pool.map",
                        lambda self, f, it: [f(o) for o in it])


@pytest.fixture
def bibitem(mocker):
    item = mocker.Mock(name="bibitem")
    item.to_xml = mocker.MagicMock(return_value=None)
    return item


@pytest.fixture
def hit(mocker, bibitem):
    hit = Hit()
    hit.fetch = mocker.MagicMock(return_value=bibitem)
    return hit


@pytest.fixture
def subject(mocker, hit):
    hits = HitCollection("ref")
    hits.append(hit)
    return hits


def test_fetches_all_hits(subject, hit):
    subject.fetch()
    hit.fetch.assert_called_once()


def test_collection_to_xml(subject, mocker, hit, bibitem):
    result = subject.to_xml()

    hit.fetch.assert_has_calls([
       [mocker.call(), mocker.call()]
    ])
    bibitem.to_xml.assert_called_once()

    assert result is not None
    assert result.tag == "documents"


@pytest.mark.skip("skippend because there is different appoach for iteration")
def test_select_hits(subject):
    assert isinstance(filter(subject), HitCollection)


@pytest.mark.skip("skippend because there is different appoach for iteration")
def test_reduce_collection():
    import functools
    functools.reduce(lambda sum, hit: sum.append(hit), subject)
    isinstance(subject, HitCollection)
