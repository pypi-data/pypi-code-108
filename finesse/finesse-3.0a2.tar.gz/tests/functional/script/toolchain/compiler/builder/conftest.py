from functools import partial
import pytest


@pytest.fixture
def compiler(monkeypatch, compiler, model):
    monkeypatch.setattr(compiler, "compile", partial(compiler.compile, model=model))
    return compiler


@pytest.fixture
def model_matcher(compiler, model):
    def matcher(script, elements):
        compiler.compile(script)
        # Just check names for simplicity.
        assert set(
            element.name
            for element in model.elements.values()
            if element.name != "fsig"
        ) == set(element.name for element in elements)

    return matcher
