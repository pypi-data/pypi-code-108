from functools import partial
import pytest


@pytest.fixture
def compiler(monkeypatch, compiler):
    monkeypatch.setattr(
        compiler, "compile", partial(compiler.compile, resolve=True, build=False)
    )
    return compiler
