import pytest


# Override default element to take two arguments.
@pytest.fixture
def fake_element_cls(fake_element_cls):
    class FakeElement(fake_element_cls):
        def __init__(self, name, a=None, b=None):
            super().__init__(name)
            self.a = a
            self.b = b

    return FakeElement


@pytest.fixture
def fake_variadic_element_cls(fake_element_cls):
    class FakeVariadicElement(fake_element_cls):
        def __init__(self, name, a, *args, b=None, **kwargs):
            super().__init__(name)
            self.a = a
            self.args = args
            self.b = b
            self.kwargs = kwargs

    return FakeVariadicElement


@pytest.fixture
def spec(
    spec, fake_element_adapter_factory, fake_element_cls, fake_variadic_element_cls
):
    spec.register_element(
        fake_element_adapter_factory(
            fake_element_cls, full_name="fake_element", short_name="fake"
        )
    )
    spec.register_element(
        fake_element_adapter_factory(
            fake_variadic_element_cls,
            full_name="fake_variadic_element",
            short_name="fake_var",
        )
    )
    return spec


@pytest.mark.parametrize(
    "name,args,kwargs,argument_defaults,prefer_keywords,expected",
    (
        # No optional arguments.
        ("myel", [], {}, False, False, "fake_element myel"),
        ("myel", [], {}, False, True, "fake_element myel"),
        ("myel", [], {}, True, False, "fake_element myel none none"),
        ("myel", [], {}, True, True, "fake_element myel a=none b=none"),
        # Optional arguments as positional.
        ("myel", [None], {}, False, False, "fake_element myel"),
        ("myel", [None], {}, False, True, "fake_element myel"),
        ("myel", [None], {}, True, False, "fake_element myel none none"),
        ("myel", [None], {}, True, True, "fake_element myel a=none b=none"),
        ("myel", [None, None], {}, False, False, "fake_element myel"),
        ("myel", [None, None], {}, False, True, "fake_element myel"),
        ("myel", [None, None], {}, True, False, "fake_element myel none none"),
        ("myel", [None, None], {}, True, True, "fake_element myel a=none b=none"),
        # Mixed form optional arguments.
        ("myel", [None], {"b": None}, False, False, "fake_element myel"),
        ("myel", [None], {"b": None}, False, True, "fake_element myel"),
        ("myel", [None], {"b": None}, True, False, "fake_element myel none none"),
        ("myel", [None], {"b": None}, True, True, "fake_element myel a=none b=none"),
        ("myel", [], {"a": None}, False, False, "fake_element myel"),
        ("myel", [], {"a": None}, False, True, "fake_element myel"),
        ("myel", [], {"a": None}, True, False, "fake_element myel none none"),
        ("myel", [], {"a": None}, True, True, "fake_element myel a=none b=none"),
        ("myel", [], {"b": None}, False, False, "fake_element myel"),
        ("myel", [], {"b": None}, False, True, "fake_element myel"),
        ("myel", [], {"b": None}, True, False, "fake_element myel none none"),
        ("myel", [], {"b": None}, True, True, "fake_element myel a=none b=none"),
        ("myel", [], {"a": None, "b": None}, False, False, "fake_element myel"),
        ("myel", [], {"a": None, "b": None}, False, True, "fake_element myel"),
        (
            "myel",
            [],
            {"a": None, "b": None},
            True,
            False,
            "fake_element myel none none",
        ),
        (
            "myel",
            [],
            {"a": None, "b": None},
            True,
            True,
            "fake_element myel a=none b=none",
        ),
        ("myel", [1], {}, False, False, "fake_element myel 1"),
        ("myel", [1], {}, False, True, "fake_element myel a=1"),
        ("myel", [1], {}, True, False, "fake_element myel 1 none"),
        ("myel", [1], {}, True, True, "fake_element myel a=1 b=none"),
        ("myel", [1, 2], {}, False, False, "fake_element myel 1 2"),
        ("myel", [1, 2], {}, False, True, "fake_element myel a=1 b=2"),
        ("myel", [1, 2], {}, True, False, "fake_element myel 1 2"),
        ("myel", [1, 2], {}, True, True, "fake_element myel a=1 b=2"),
        # Optional arguments as keyword.
        ("myel", [], {"a": 1}, False, False, "fake_element myel 1"),
        ("myel", [], {"a": 1}, False, True, "fake_element myel a=1"),
        ("myel", [], {"a": 1}, True, False, "fake_element myel 1 none"),
        ("myel", [], {"a": 1}, True, True, "fake_element myel a=1 b=none"),
        ("myel", [], {"a": 1, "b": 2}, False, False, "fake_element myel 1 2"),
        (
            "myel",
            [],
            {"a": 1, "b": 2},
            False,
            True,
            "fake_element myel a=1 b=2",
        ),
        ("myel", [], {"a": 1, "b": 2}, True, False, "fake_element myel 1 2"),
        ("myel", [], {"a": 1, "b": 2}, True, True, "fake_element myel a=1 b=2"),
    ),
)
def test_element(
    unbuilder,
    model,
    element_dump,
    fake_element_cls,
    name,
    args,
    kwargs,
    argument_defaults,
    prefer_keywords,
    expected,
):
    """Element with normal signature."""
    model.add(fake_element_cls(name, *args, **kwargs))
    dump = next(iter(element_dump("fake_element", fake_element_cls, model)))
    script = unbuilder.unbuild(
        dump,
        argument_defaults=argument_defaults,
        prefer_keywords=prefer_keywords,
    )
    assert script == expected


@pytest.mark.parametrize(
    "name,args,kwargs,argument_defaults,prefer_keywords,expected",
    (
        # No optional arguments.
        ("myel", [None], {}, False, False, "fake_variadic_element myel none"),
        ("myel", [None], {}, False, True, "fake_variadic_element myel a=none"),
        ("myel", [None], {}, True, False, "fake_variadic_element myel none b=none"),
        ("myel", [None], {}, True, True, "fake_variadic_element myel a=none b=none"),
        # Variadic positional arguments.
        (
            "myel",
            [None, None],
            {},
            False,
            False,
            "fake_variadic_element myel none none",
        ),
        ("myel", [None, None], {}, False, True, "fake_variadic_element myel none none"),
        (
            "myel",
            [None, None],
            {},
            True,
            False,
            "fake_variadic_element myel none none b=none",
        ),
        (
            "myel",
            [None, None],
            {},
            True,
            True,
            "fake_variadic_element myel none none b=none",
        ),
        # Mixed form optional arguments.
        ("myel", [None], {"b": None}, False, False, "fake_variadic_element myel none"),
        ("myel", [None], {"b": None}, False, True, "fake_variadic_element myel a=none"),
        (
            "myel",
            [None],
            {"b": None},
            True,
            False,
            "fake_variadic_element myel none b=none",
        ),
        (
            "myel",
            [None],
            {"b": None},
            True,
            True,
            "fake_variadic_element myel a=none b=none",
        ),
        ("myel", [], {"a": None}, False, False, "fake_variadic_element myel none"),
        ("myel", [], {"a": None}, False, True, "fake_variadic_element myel a=none"),
        (
            "myel",
            [],
            {"a": None},
            True,
            False,
            "fake_variadic_element myel none b=none",
        ),
        (
            "myel",
            [],
            {"a": None},
            True,
            True,
            "fake_variadic_element myel a=none b=none",
        ),
        (
            "myel",
            [],
            {"a": None, "b": None},
            False,
            False,
            "fake_variadic_element myel none",
        ),
        (
            "myel",
            [],
            {"a": None, "b": None},
            False,
            True,
            "fake_variadic_element myel a=none",
        ),
        (
            "myel",
            [],
            {"a": None, "b": None},
            True,
            False,
            "fake_variadic_element myel none b=none",
        ),
        (
            "myel",
            [],
            {"a": None, "b": None},
            True,
            True,
            "fake_variadic_element myel a=none b=none",
        ),
        (
            "myel",
            [],
            {"a": None, "b": None},
            False,
            False,
            "fake_variadic_element myel none",
        ),
        (
            "myel",
            [],
            {"a": None, "b": None},
            False,
            True,
            "fake_variadic_element myel a=none",
        ),
        ("myel", [1], {}, False, False, "fake_variadic_element myel 1"),
        ("myel", [1], {}, False, True, "fake_variadic_element myel a=1"),
        ("myel", [1], {}, True, False, "fake_variadic_element myel 1 b=none"),
        ("myel", [1], {}, True, True, "fake_variadic_element myel a=1 b=none"),
        ("myel", [1, 2], {}, False, False, "fake_variadic_element myel 1 2"),
        ("myel", [1, 2], {}, False, True, "fake_variadic_element myel 1 2"),
        ("myel", [1, 2], {}, True, False, "fake_variadic_element myel 1 2 b=none"),
        ("myel", [1, 2], {}, True, True, "fake_variadic_element myel 1 2 b=none"),
        # Optional arguments as keyword.
        ("myel", [], {"a": 1}, False, False, "fake_variadic_element myel 1"),
        ("myel", [], {"a": 1}, False, True, "fake_variadic_element myel a=1"),
        ("myel", [], {"a": 1}, True, False, "fake_variadic_element myel 1 b=none"),
        ("myel", [], {"a": 1}, True, True, "fake_variadic_element myel a=1 b=none"),
        (
            "myel",
            [],
            {"a": 1, "b": 2},
            False,
            False,
            "fake_variadic_element myel 1 b=2",
        ),
        (
            "myel",
            [],
            {"a": 1, "b": 2},
            False,
            True,
            "fake_variadic_element myel a=1 b=2",
        ),
        (
            "myel",
            [],
            {"a": 1, "b": 2},
            True,
            False,
            "fake_variadic_element myel 1 b=2",
        ),
        (
            "myel",
            [],
            {"a": 1, "b": 2},
            True,
            True,
            "fake_variadic_element myel a=1 b=2",
        ),
        # Variadic keyword arguments.
        (
            "myel",
            [],
            {"a": 1, "b": 2, "c": 3},
            False,
            False,
            "fake_variadic_element myel 1 b=2 c=3",
        ),
        (
            "myel",
            [],
            {"a": 1, "b": 2, "c": 3},
            False,
            True,
            "fake_variadic_element myel a=1 b=2 c=3",
        ),
        (
            "myel",
            [],
            {"a": 1, "b": 2, "c": 3},
            True,
            False,
            "fake_variadic_element myel 1 b=2 c=3",
        ),
        (
            "myel",
            [],
            {"a": 1, "b": 2, "c": 3},
            True,
            True,
            "fake_variadic_element myel a=1 b=2 c=3",
        ),
        # Variadic positional and keyword arguments.
        (
            "myel",
            [1, 2],
            {"b": 3, "c": 4},
            False,
            False,
            "fake_variadic_element myel 1 2 b=3 c=4",
        ),
        (
            "myel",
            [1, 2],
            {"b": 3, "c": 4},
            False,
            True,
            "fake_variadic_element myel 1 2 b=3 c=4",
        ),
        (
            "myel",
            [1, 2],
            {"b": 3, "c": 4},
            True,
            False,
            "fake_variadic_element myel 1 2 b=3 c=4",
        ),
        (
            "myel",
            [1, 2],
            {"b": 3, "c": 4},
            True,
            True,
            "fake_variadic_element myel 1 2 b=3 c=4",
        ),
    ),
)
def test_variadic_element(
    unbuilder,
    model,
    element_dump,
    fake_variadic_element_cls,
    name,
    args,
    kwargs,
    argument_defaults,
    prefer_keywords,
    expected,
):
    """Element with variadic arguments in signature."""
    model.add(fake_variadic_element_cls(name, *args, **kwargs))
    dump = next(
        iter(element_dump("fake_variadic_element", fake_variadic_element_cls, model))
    )
    script = unbuilder.unbuild(
        dump,
        argument_defaults=argument_defaults,
        prefer_keywords=prefer_keywords,
    )
    assert script == expected
