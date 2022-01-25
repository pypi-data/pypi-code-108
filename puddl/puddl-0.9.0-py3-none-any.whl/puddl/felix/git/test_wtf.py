import logging
from pathlib import Path

from puddl.felix.git.repo2rows import iter_records


def test_empty_header(caplog):
    caplog.set_level(logging.INFO, logger='puddl.felix.git')
    print(caplog.records)
    records = list(iter_records(Path('/home/felix/github/kimai-in-docker')))
    assert len(records) > 0
