import pytest


# Override default analysis to take one positional-only, one positional-or-keyword,
# and one keyword-only argument.
@pytest.fixture
def fake_analysis_cls(fake_analysis_cls):
    class FakeAnalysis(fake_analysis_cls):
        def __init__(self, a, /, b=None, *, c=None):
            super().__init__()
            self.a = a
            self.b = b
            self.c = c

    return FakeAnalysis


@pytest.fixture
def spec(spec, fake_analysis_adapter_factory, fake_analysis_cls):
    spec.register_analysis(
        fake_analysis_adapter_factory(fake_analysis_cls, short_name="fake")
    )
    return spec


def _test_analysis_dump(unbuilder, analysis_dump, expected, **kwargs):
    assert unbuilder.unbuild(analysis_dump, **kwargs) == expected


@pytest.mark.parametrize(
    "directive_defaults,argument_defaults,prefer_keywords,expected",
    (
        (False, False, False, ""),
        (False, False, True, ""),
        (False, True, False, ""),
        (False, True, True, ""),
        (False, False, False, ""),
        (False, False, True, ""),
        (False, True, False, ""),
        (False, True, True, ""),
        (True, False, False, "fake_analysis(1)"),
        (True, False, True, "fake_analysis(1)"),
        (True, True, False, "fake_analysis(1, none, c=none)"),
        (True, True, True, "fake_analysis(1, b=none, c=none)"),
        (True, False, False, "fake_analysis(1)"),
        (True, False, True, "fake_analysis(1)"),
        (True, True, False, "fake_analysis(1, none, c=none)"),
        (True, True, True, "fake_analysis(1, b=none, c=none)"),
    ),
)
def test_default_analysis(
    unbuilder,
    model,
    analysis_dump,
    fake_analysis_cls,
    directive_defaults,
    argument_defaults,
    prefer_keywords,
    expected,
):
    model.analysis = fake_analysis_cls(1)  # Fake value.
    dump = next(iter(analysis_dump("fake_analysis", fake_analysis_cls, model)))
    dump.is_default = True

    _test_analysis_dump(
        unbuilder,
        dump,
        expected,
        directive_defaults=directive_defaults,
        argument_defaults=argument_defaults,
        prefer_keywords=prefer_keywords,
    )


@pytest.mark.parametrize(
    "args,kwargs,argument_defaults,prefer_keywords,expected",
    (
        # No optional arguments.
        ([None], {}, False, False, "fake_analysis(none)"),
        ([None], {}, False, True, "fake_analysis(none)"),
        ([None], {}, True, False, "fake_analysis(none, none, c=none)"),
        ([None], {}, True, True, "fake_analysis(none, b=none, c=none)"),
        ([1], {}, False, False, "fake_analysis(1)"),
        ([1], {}, False, True, "fake_analysis(1)"),
        ([1], {}, True, False, "fake_analysis(1, none, c=none)"),
        ([1], {}, True, True, "fake_analysis(1, b=none, c=none)"),
        # Optional-as-positional arguments.
        ([1, 2], {}, False, False, "fake_analysis(1, 2)"),
        ([1, 2], {}, False, True, "fake_analysis(1, b=2)"),
        ([1, 2], {}, True, False, "fake_analysis(1, 2, c=none)"),
        ([1, 2], {}, True, True, "fake_analysis(1, b=2, c=none)"),
        ([1, 2], {"c": 3}, False, False, "fake_analysis(1, 2, c=3)"),
        ([1, 2], {"c": 3}, False, True, "fake_analysis(1, b=2, c=3)"),
        ([1, 2], {"c": 3}, True, False, "fake_analysis(1, 2, c=3)"),
        ([1, 2], {"c": 3}, True, True, "fake_analysis(1, b=2, c=3)"),
        # Optional-as-keyword arguments.
        ([1], {"b": 2}, False, False, "fake_analysis(1, 2)"),
        ([1], {"b": 2}, False, True, "fake_analysis(1, b=2)"),
        ([1], {"b": 2}, True, False, "fake_analysis(1, 2, c=none)"),
        ([1], {"b": 2}, True, True, "fake_analysis(1, b=2, c=none)"),
        ([1], {"b": 2, "c": 3}, False, False, "fake_analysis(1, 2, c=3)"),
        ([1], {"b": 2, "c": 3}, False, True, "fake_analysis(1, b=2, c=3)"),
        ([1], {"b": 2, "c": 3}, True, False, "fake_analysis(1, 2, c=3)"),
        ([1], {"b": 2, "c": 3}, True, True, "fake_analysis(1, b=2, c=3)"),
    ),
)
def test_analysis(
    unbuilder,
    model,
    analysis_dump,
    fake_analysis_cls,
    args,
    kwargs,
    argument_defaults,
    prefer_keywords,
    expected,
):
    model.analysis = fake_analysis_cls(*args, **kwargs)

    _test_analysis_dump(
        unbuilder,
        next(iter(analysis_dump("fake_analysis", fake_analysis_cls, model))),
        expected,
        argument_defaults=argument_defaults,
        prefer_keywords=prefer_keywords,
    )
