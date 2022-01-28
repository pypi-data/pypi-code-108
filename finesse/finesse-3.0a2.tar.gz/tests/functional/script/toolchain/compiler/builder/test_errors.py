import pytest
from finesse.script.exceptions import KatScriptError
from ......util import escape_full


@pytest.fixture
def fake_element_positional_args_cls(fake_element_cls):
    class FakeElementPositionalArgs(fake_element_cls):
        def __init__(self, name, a, b):
            super().__init__(name)
            self.a = a
            self.b = b

    return FakeElementPositionalArgs


@pytest.fixture
def fake_element_keyword_args_cls(fake_element_cls):
    class FakeElementKeywordArgs(fake_element_cls):
        def __init__(self, name, a=None, b=None):
            super().__init__(name)
            self.a = a
            self.b = b

    return FakeElementKeywordArgs


@pytest.fixture
def fake_element_mixed_args_cls(fake_element_cls):
    class FakeElementMixedArgs(fake_element_cls):
        def __init__(self, name, a, b, c, d=None):
            super().__init__(name)
            self.a = a
            self.b = b
            self.c = c
            self.d = d

    return FakeElementMixedArgs


@pytest.fixture
def fake_element_variadic_mixed_args_cls(fake_element_cls):
    class FakeElementVariadicMixedArgs(fake_element_cls):
        def __init__(self, name, a, b, c, *myargs, d=None, **mykwargs):
            super().__init__(name)
            self.a = a
            self.b = b
            self.c = c
            self.myargs = myargs
            self.d = d
            self.mykwargs = mykwargs

    return FakeElementVariadicMixedArgs


@pytest.fixture
def fake_command_positional_args_func():
    def fake_command_positional_args(model, a, b, c):
        pass

    return fake_command_positional_args


@pytest.fixture
def fake_command_keyword_args_func():
    def fake_command_keyword_args(model, a=None, b=None, c=None):
        pass

    return fake_command_keyword_args


@pytest.fixture
def fake_command_mixed_args_func():
    def fake_command_mixed_args(model, a, b, c, d=None):
        pass

    return fake_command_mixed_args


@pytest.fixture
def fake_command_variadic_mixed_args_func():
    def fake_command_variadic_mixed_args(model, a, b, c, *myargs, d=None, **mykwargs):
        pass

    return fake_command_variadic_mixed_args


@pytest.fixture
def spec(
    spec,
    fake_element_adapter_factory,
    fake_element_positional_args_cls,
    fake_element_keyword_args_cls,
    fake_element_mixed_args_cls,
    fake_element_variadic_mixed_args_cls,
    fake_command_adapter_factory,
    fake_command_positional_args_func,
    fake_command_keyword_args_func,
    fake_command_mixed_args_func,
    fake_command_variadic_mixed_args_func,
    finesse_binop_add,
    finesse_unop_neg,
):
    spec.register_element(
        fake_element_adapter_factory(
            fake_element_positional_args_cls, "fake_element_with_args"
        )
    )
    spec.register_element(
        fake_element_adapter_factory(
            fake_element_keyword_args_cls, "fake_element_with_kwargs"
        )
    )
    spec.register_element(
        fake_element_adapter_factory(fake_element_mixed_args_cls, "fake_element_mixed")
    )
    spec.register_element(
        fake_element_adapter_factory(
            fake_element_variadic_mixed_args_cls, "fake_element_variadic_mixed"
        )
    )
    spec.register_command(
        fake_command_adapter_factory(
            fake_command_positional_args_func, "fake_command_with_args"
        )
    )
    spec.register_command(
        fake_command_adapter_factory(
            fake_command_keyword_args_func, "fake_command_with_kwargs"
        )
    )
    spec.register_command(
        fake_command_adapter_factory(fake_command_mixed_args_func, "fake_command_mixed")
    )
    spec.register_command(
        fake_command_adapter_factory(
            fake_command_variadic_mixed_args_func, "fake_command_variadic_mixed"
        )
    )
    # Have to use real Finesse operators here because the builder matches against
    # Finesse operations.
    spec.binary_operators["+"] = finesse_binop_add
    spec.unary_operators["-"] = finesse_unop_neg
    return spec


@pytest.mark.parametrize(
    "script,error",
    (
        ## Elements
        # The error handler should compensate for the `self` argument of the setters
        # that are not exposed in KatScript. We also consider the `name` parameter not
        # to be an "argument" in KatScript, so that gets dealt with too.
        # Element with positional arguments.
        pytest.param(
            "fake_element_with_args myelement",
            "\nline 1: 'fake_element_with_args' missing 2 required positional arguments: 'a' and 'b'\n"
            "-->1: fake_element_with_args myelement\n"
            "                                       ^\n"
            "Syntax: fake_element_with_args name a b",
            id="two-arg-element-called-with-no-args",
        ),
        pytest.param(
            "fake_element_with_args myelement 1",
            "\nline 1: 'fake_element_with_args' missing 1 required positional argument: 'b'\n"
            "-->1: fake_element_with_args myelement 1\n"
            "                                         ^\n"
            "Syntax: fake_element_with_args name a b",
            id="two-arg-element-called-with-one-arg",
        ),
        # Element with positional and keyword arguments - no arguments.
        pytest.param(
            "fake_element_mixed myelement",
            "\nline 1: 'fake_element_mixed' missing 3 required positional arguments: 'a', 'b', and 'c'\n"
            "-->1: fake_element_mixed myelement\n"
            "                                   ^\n"
            "Syntax: fake_element_mixed name a b c d=none",
            id="four-mixed-arg-element-called-with-no-args",
        ),
        # Element with positional and keyword arguments - called by position.
        pytest.param(
            "fake_element_mixed myelement 1",
            "\nline 1: 'fake_element_mixed' missing 2 required positional arguments: 'b' and 'c'\n"
            "-->1: fake_element_mixed myelement 1\n"
            "                                     ^\n"
            "Syntax: fake_element_mixed name a b c d=none",
            id="four-mixed-arg-element-called-with-one-arg",
        ),
        # Element with positional and keyword arguments - called by keyword.
        pytest.param(
            "fake_element_mixed myelement a=1",
            "\nline 1: 'fake_element_mixed' missing 2 required positional arguments: 'b' and 'c'\n"
            "-->1: fake_element_mixed myelement a=1\n"
            "                                       ^\n"
            "Syntax: fake_element_mixed name a b c d=none",
            id="four-mixed-arg-element-called-with-one-kwarg",
        ),
        # Element with positional and keyword arguments - mixed call.
        pytest.param(
            "fake_element_mixed myelement 1 b=2",
            "\nline 1: 'fake_element_mixed' missing 1 required positional argument: 'c'\n"
            "-->1: fake_element_mixed myelement 1 b=2\n"
            "                                         ^\n"
            "Syntax: fake_element_mixed name a b c d=none",
            id="four-mixed-arg-element-called-with-one-arg-one-kwarg",
        ),
        # Element with variadic positional and keyword arguments - no arguments.
        pytest.param(
            "fake_element_variadic_mixed myelement",
            "\nline 1: 'fake_element_variadic_mixed' missing 3 required positional arguments: 'a', 'b', and 'c'\n"
            "-->1: fake_element_variadic_mixed myelement\n"
            "                                            ^\n"
            "Syntax: fake_element_variadic_mixed name a b c *myargs d=none **mykwargs",
            id="four-variadic-mixed-arg-element-called-with-no-args",
        ),
        # Element with variadic positional and keyword arguments - called by position.
        pytest.param(
            "fake_element_variadic_mixed myelement 1",
            "\nline 1: 'fake_element_variadic_mixed' missing 2 required positional arguments: 'b' and 'c'\n"
            "-->1: fake_element_variadic_mixed myelement 1\n"
            "                                              ^\n"
            "Syntax: fake_element_variadic_mixed name a b c *myargs d=none **mykwargs",
            id="four-variadic-mixed-arg-element-called-with-one-arg",
        ),
        # Element with variadic positional and keyword arguments - called by keyword.
        pytest.param(
            "fake_element_variadic_mixed myelement a=1",
            "\nline 1: 'fake_element_variadic_mixed' missing 2 required positional arguments: 'b' and 'c'\n"
            "-->1: fake_element_variadic_mixed myelement a=1\n"
            "                                                ^\n"
            "Syntax: fake_element_variadic_mixed name a b c *myargs d=none **mykwargs",
            id="four-variadic-mixed-arg-element-called-with-one-kwarg",
        ),
        # Element with variadic positional and keyword arguments - mixed call.
        pytest.param(
            "fake_element_variadic_mixed myelement 1 b=2",
            "\nline 1: 'fake_element_variadic_mixed' missing 1 required positional argument: 'c'\n"
            "-->1: fake_element_variadic_mixed myelement 1 b=2\n"
            "                                                  ^\n"
            "Syntax: fake_element_variadic_mixed name a b c *myargs d=none **mykwargs",
            id="four-variadic-mixed-arg-element-called-with-one-arg-one-kwarg",
        ),
        ## Commands
        # The error handler should compensate for the `self` (for direct setters) or
        # `model` (for setter proxies) of the setter arguments that are not exposed in
        # KatScript.
        # Command with positional arguments.
        pytest.param(
            "fake_command_with_args()",
            "\nline 1: 'fake_command_with_args' missing 3 required positional arguments: 'a', 'b', and 'c'\n"
            "-->1: fake_command_with_args()\n"
            "                             ^\n"
            "Syntax: fake_command_with_args(a, b, c)",
            id="three-arg-command-called-with-no-args",
        ),
        pytest.param(
            "fake_command_with_args(1)",
            "\nline 1: 'fake_command_with_args' missing 2 required positional arguments: 'b' and 'c'\n"
            "-->1: fake_command_with_args(1)\n"
            "                              ^\n"
            "Syntax: fake_command_with_args(a, b, c)",
            id="three-arg-command-called-with-one-arg",
        ),
        pytest.param(
            "fake_command_with_args(1, 2)",
            "\nline 1: 'fake_command_with_args' missing 1 required positional argument: 'c'\n"
            "-->1: fake_command_with_args(1, 2)\n"
            "                                 ^\n"
            "Syntax: fake_command_with_args(a, b, c)",
            id="three-arg-command-called-with-two-args",
        ),
        # Command with positional and keyword arguments - no arguments.
        pytest.param(
            "fake_command_mixed()",
            "\nline 1: 'fake_command_mixed' missing 3 required positional arguments: 'a', 'b', and 'c'\n"
            "-->1: fake_command_mixed()\n"
            "                         ^\n"
            "Syntax: fake_command_mixed(a, b, c, d=none)",
            id="four-mixed-arg-command-called-with-no-args",
        ),
        # Command with positional and keyword arguments - called by position.
        pytest.param(
            "fake_command_mixed(1)",
            "\nline 1: 'fake_command_mixed' missing 2 required positional arguments: 'b' and 'c'\n"
            "-->1: fake_command_mixed(1)\n"
            "                          ^\n"
            "Syntax: fake_command_mixed(a, b, c, d=none)",
            id="four-mixed-arg-command-called-with-one-arg",
        ),
        pytest.param(
            "fake_command_mixed(1, 2)",
            "\nline 1: 'fake_command_mixed' missing 1 required positional argument: 'c'\n"
            "-->1: fake_command_mixed(1, 2)\n"
            "                             ^\n"
            "Syntax: fake_command_mixed(a, b, c, d=none)",
            id="four-mixed-arg-command-called-with-two-args",
        ),
        # Command with positional and keyword arguments - called by keyword.
        pytest.param(
            "fake_command_mixed(a=1)",
            "\nline 1: 'fake_command_mixed' missing 2 required positional arguments: 'b' and 'c'\n"
            "-->1: fake_command_mixed(a=1)\n"
            "                            ^\n"
            "Syntax: fake_command_mixed(a, b, c, d=none)",
            id="four-mixed-arg-command-called-with-one-kwarg",
        ),
        pytest.param(
            "fake_command_mixed(a=1, b=2)",
            "\nline 1: 'fake_command_mixed' missing 1 required positional argument: 'c'\n"
            "-->1: fake_command_mixed(a=1, b=2)\n"
            "                                 ^\n"
            "Syntax: fake_command_mixed(a, b, c, d=none)",
            id="four-mixed-arg-command-called-with-two-kwargs",
        ),
        # Command with positional and keyword arguments - mixed call.
        pytest.param(
            "fake_command_mixed(1, b=2)",
            "\nline 1: 'fake_command_mixed' missing 1 required positional argument: 'c'\n"
            "-->1: fake_command_mixed(1, b=2)\n"
            "                               ^\n"
            "Syntax: fake_command_mixed(a, b, c, d=none)",
            id="four-mixed-arg-command-called-with-one-arg-one-kwarg",
        ),
        # Command with variadic positional and keyword arguments - no arguments.
        pytest.param(
            "fake_command_variadic_mixed()",
            "\nline 1: 'fake_command_variadic_mixed' missing 3 required positional arguments: 'a', 'b', and 'c'\n"
            "-->1: fake_command_variadic_mixed()\n"
            "                                  ^\n"
            "Syntax: fake_command_variadic_mixed(a, b, c, *myargs, d=none, **mykwargs)",
            id="four-variadic-mixed-arg-command-called-with-no-args",
        ),
        # Command with variadic positional and keyword arguments - called by position.
        pytest.param(
            "fake_command_variadic_mixed(1)",
            "\nline 1: 'fake_command_variadic_mixed' missing 2 required positional arguments: 'b' and 'c'\n"
            "-->1: fake_command_variadic_mixed(1)\n"
            "                                   ^\n"
            "Syntax: fake_command_variadic_mixed(a, b, c, *myargs, d=none, **mykwargs)",
            id="four-variadic-mixed-arg-command-called-with-one-arg",
        ),
        pytest.param(
            "fake_command_variadic_mixed(1, 2)",
            "\nline 1: 'fake_command_variadic_mixed' missing 1 required positional argument: 'c'\n"
            "-->1: fake_command_variadic_mixed(1, 2)\n"
            "                                      ^\n"
            "Syntax: fake_command_variadic_mixed(a, b, c, *myargs, d=none, **mykwargs)",
            id="four-variadic-mixed-arg-command-called-with-two-args",
        ),
        # Command with variadic positional and keyword arguments - called by keyword.
        pytest.param(
            "fake_command_variadic_mixed(a=1)",
            "\nline 1: 'fake_command_variadic_mixed' missing 2 required positional arguments: 'b' and 'c'\n"
            "-->1: fake_command_variadic_mixed(a=1)\n"
            "                                     ^\n"
            "Syntax: fake_command_variadic_mixed(a, b, c, *myargs, d=none, **mykwargs)",
            id="four-variadic-mixed-arg-command-called-with-one-kwarg",
        ),
        pytest.param(
            "fake_command_variadic_mixed(a=1, b=2)",
            "\nline 1: 'fake_command_variadic_mixed' missing 1 required positional argument: 'c'\n"
            "-->1: fake_command_variadic_mixed(a=1, b=2)\n"
            "                                          ^\n"
            "Syntax: fake_command_variadic_mixed(a, b, c, *myargs, d=none, **mykwargs)",
            id="four-variadic-mixed-arg-command-called-with-two-kwargs",
        ),
        # Command with variadic positional and keyword arguments - mixed call.
        pytest.param(
            "fake_command_variadic_mixed(1, b=2)",
            "\nline 1: 'fake_command_variadic_mixed' missing 1 required positional argument: 'c'\n"
            "-->1: fake_command_variadic_mixed(1, b=2)\n"
            "                                        ^\n"
            "Syntax: fake_command_variadic_mixed(a, b, c, *myargs, d=none, **mykwargs)",
            id="four-variadic-mixed-arg-command-called-with-one-arg-one-kwarg",
        ),
    ),
)
def test_not_enough_arguments(compiler, script, error):
    with pytest.raises(KatScriptError, match=escape_full(error)):
        compiler.compile(script)


@pytest.mark.parametrize(
    "script,error",
    (
        ## Elements
        # Element with positional arguments.
        pytest.param(
            "fake_element_with_args myelement 1 2 3",
            "\nline 1: 'fake_element_with_args' takes 2 positional arguments but 3 were given\n"
            "-->1: fake_element_with_args myelement 1 2 3\n"
            "                                           ^\n"
            "Syntax: fake_element_with_args name a b",
            id="two-arg-element-called-with-three-args",
        ),
        pytest.param(
            "fake_element_with_args myelement 1 2 3 4",
            "\nline 1: 'fake_element_with_args' takes 2 positional arguments but 4 were given\n"
            "-->1: fake_element_with_args myelement 1 2 3 4\n"
            "                                           ^ ^\n"
            "Syntax: fake_element_with_args name a b",
            id="two-arg-element-called-with-four-args",
        ),
        # Element with keyword arguments.
        pytest.param(
            "fake_element_with_kwargs myelement 1 2 3",
            "\nline 1: 'fake_element_with_kwargs' takes from 0 to 2 positional arguments but 3 were given\n"
            "-->1: fake_element_with_kwargs myelement 1 2 3\n"
            "                                             ^\n"
            "Syntax: fake_element_with_kwargs name a=none b=none",
            id="two-kwarg-element-called-with-three-args",
        ),
        pytest.param(
            "fake_element_with_kwargs myelement 1 2 3 4",
            "\nline 1: 'fake_element_with_kwargs' takes from 0 to 2 positional arguments but 4 were given\n"
            "-->1: fake_element_with_kwargs myelement 1 2 3 4\n"
            "                                             ^ ^\n"
            "Syntax: fake_element_with_kwargs name a=none b=none",
            id="two-kwarg-element-called-with-four-args",
        ),
        # Element with positional and keyword arguments - called by position.
        pytest.param(
            "fake_element_mixed myelement 1 2 3 4 5",
            "\nline 1: 'fake_element_mixed' takes from 3 to 4 positional arguments but 5 were given\n"
            "-->1: fake_element_mixed myelement 1 2 3 4 5\n"
            "                                           ^\n"
            "Syntax: fake_element_mixed name a b c d=none",
            id="four-mixed-arg-element-called-with-five-args",
        ),
        pytest.param(
            "fake_element_mixed myelement 1 2 3 4 5 6",
            "\nline 1: 'fake_element_mixed' takes from 3 to 4 positional arguments but 6 were given\n"
            "-->1: fake_element_mixed myelement 1 2 3 4 5 6\n"
            "                                           ^ ^\n"
            "Syntax: fake_element_mixed name a b c d=none",
            id="four-mixed-arg-element-called-with-six-args",
        ),
        # Element with positional and keyword arguments - called by keyword.
        pytest.param(
            "fake_element_mixed myelement a=1 b=2 c=3 d=4 e=5",
            "\nline 1: 'fake_element_mixed' got an unexpected keyword argument 'e'\n"
            "-->1: fake_element_mixed myelement a=1 b=2 c=3 d=4 e=5\n"
            "                                                   ^\n"
            "Syntax: fake_element_mixed name a b c d=none",
            id="four-mixed-arg-element-called-with-four-kwargs-one-invalid-kwarg",
        ),
        pytest.param(
            "fake_element_mixed myelement a=1 b=2 c=3 d=4 e=5 f=6",
            "\nline 1: 'fake_element_mixed' got an unexpected keyword argument 'e'\n"
            "-->1: fake_element_mixed myelement a=1 b=2 c=3 d=4 e=5 f=6\n"
            "                                                   ^\n"
            "Syntax: fake_element_mixed name a b c d=none",
            id="four-mixed-arg-element-called-with-four-kwargs-two-invalid-kwargs",
        ),
        # Element with positional and keyword arguments - mixed call.
        pytest.param(
            "fake_element_mixed myelement 1 2 3 d=4 e=5",
            "\nline 1: 'fake_element_mixed' got an unexpected keyword argument 'e'\n"
            "-->1: fake_element_mixed myelement 1 2 3 d=4 e=5\n"
            "                                             ^\n"
            "Syntax: fake_element_mixed name a b c d=none",
            id="four-mixed-arg-element-called-with-three-args-one-kwarg-one-invalid-kwarg",
        ),
        pytest.param(
            "fake_element_mixed myelement 1 2 3 d=4 e=5 f=6",
            "\nline 1: 'fake_element_mixed' got an unexpected keyword argument 'e'\n"
            "-->1: fake_element_mixed myelement 1 2 3 d=4 e=5 f=6\n"
            "                                             ^\n"
            "Syntax: fake_element_mixed name a b c d=none",
            id="four-mixed-arg-element-called-with-three-args-one-kwarg-two-invalid-kwargs",
        ),
        ## Commands
        # Command with positional arguments.
        pytest.param(
            "fake_command_with_args(1, 2, 3, 4)",
            "\nline 1: 'fake_command_with_args' takes 3 positional arguments but 4 were given\n"
            "-->1: fake_command_with_args(1, 2, 3, 4)\n"
            "                                      ^\n"
            "Syntax: fake_command_with_args(a, b, c)",
            id="three-arg-command-called-with-four-args",
        ),
        pytest.param(
            "fake_command_with_args(1, 2, 3, 4, 5)",
            "\nline 1: 'fake_command_with_args' takes 3 positional arguments but 5 were given\n"
            "-->1: fake_command_with_args(1, 2, 3, 4, 5)\n"
            "                                      ^  ^\n"
            "Syntax: fake_command_with_args(a, b, c)",
            id="three-arg-command-called-with-five-args",
        ),
        # Command with keyword arguments.
        pytest.param(
            "fake_command_with_kwargs(1, 2, 3, 4)",
            "\nline 1: 'fake_command_with_kwargs' takes from 0 to 3 positional arguments but 4 were given\n"
            "-->1: fake_command_with_kwargs(1, 2, 3, 4)\n"
            "                                        ^\n"
            "Syntax: fake_command_with_kwargs(a=none, b=none, c=none)",
            id="three-kwarg-command-called-with-four-args",
        ),
        pytest.param(
            "fake_command_with_kwargs(1, 2, 3, 4, 5)",
            "\nline 1: 'fake_command_with_kwargs' takes from 0 to 3 positional arguments but 5 were given\n"
            "-->1: fake_command_with_kwargs(1, 2, 3, 4, 5)\n"
            "                                        ^  ^\n"
            "Syntax: fake_command_with_kwargs(a=none, b=none, c=none)",
            id="three-kwarg-command-called-with-five-args",
        ),
        # Command with positional and keyword arguments - called by position.
        pytest.param(
            "fake_command_mixed(1, 2, 3, 4, 5)",
            "\nline 1: 'fake_command_mixed' takes from 3 to 4 positional arguments but 5 were given\n"
            "-->1: fake_command_mixed(1, 2, 3, 4, 5)\n"
            "                                     ^\n"
            "Syntax: fake_command_mixed(a, b, c, d=none)",
            id="four-mixed-arg-command-called-with-five-args",
        ),
        pytest.param(
            "fake_command_mixed(1, 2, 3, 4, 5, 6)",
            "\nline 1: 'fake_command_mixed' takes from 3 to 4 positional arguments but 6 were given\n"
            "-->1: fake_command_mixed(1, 2, 3, 4, 5, 6)\n"
            "                                     ^  ^\n"
            "Syntax: fake_command_mixed(a, b, c, d=none)",
            id="four-mixed-arg-command-called-with-six-args",
        ),
        # Command with positional and keyword arguments - called by keyword.
        pytest.param(
            "fake_command_mixed(a=1, b=2, c=3, d=4, e=5)",
            "\nline 1: 'fake_command_mixed' got an unexpected keyword argument 'e'\n"
            "-->1: fake_command_mixed(a=1, b=2, c=3, d=4, e=5)\n"
            "                                             ^\n"
            "Syntax: fake_command_mixed(a, b, c, d=none)",
            id="four-mixed-arg-command-called-with-four-kwargs-one-invalid-kwarg",
        ),
        pytest.param(
            "fake_command_mixed(a=1, b=2, c=3, d=4, e=5, f=6)",
            "\nline 1: 'fake_command_mixed' got an unexpected keyword argument 'e'\n"
            "-->1: fake_command_mixed(a=1, b=2, c=3, d=4, e=5, f=6)\n"
            "                                             ^\n"
            "Syntax: fake_command_mixed(a, b, c, d=none)",
            id="four-mixed-arg-command-called-with-four-kwargs-two-invalid-kwargs",
        ),
    ),
)
def test_too_many_arguments(compiler, script, error):
    with pytest.raises(KatScriptError, match=escape_full(error)):
        compiler.compile(script)


@pytest.mark.parametrize(
    "script,error",
    (
        pytest.param(
            "fake_command_with_args(1, 2, 3, a=1)",
            "\nline 1: 'fake_command_with_args' got multiple values for argument 'a'\n"
            "-->1: fake_command_with_args(1, 2, 3, a=1)\n"
            "                             ^          ^\n"
            "Syntax: fake_command_with_args(a, b, c)",
            id="three-arg-command-called-with-three-args-one-duplicate-kwarg",
        ),
        pytest.param(
            "fake_command_variadic_mixed(1, 2, 3, a=1)",
            "\nline 1: 'fake_command_variadic_mixed' got multiple values for argument 'a'\n"
            "-->1: fake_command_variadic_mixed(1, 2, 3, a=1)\n"
            "                                  ^          ^\n"
            "Syntax: fake_command_variadic_mixed(a, b, c, *myargs, d=none, **mykwargs)",
            id="variadic-mixed-command-called-with-three-args-one-duplicate-kwarg",
        ),
        # Duplicate keyword argument errors triggered before extraneous positional
        # arguments.
        pytest.param(
            "fake_command_with_args(1, 2, 3, 4, a=1)",
            "\nline 1: 'fake_command_with_args' got multiple values for argument 'a'\n"
            "-->1: fake_command_with_args(1, 2, 3, 4, a=1)\n"
            "                             ^             ^\n"
            "Syntax: fake_command_with_args(a, b, c)",
            id="three-arg-command-called-with-three-args-one-invalid-arg-one-duplicate-kwarg",
        ),
        pytest.param(
            "fake_command_with_args(1, 2, 3, 4, 5, a=1)",
            "\nline 1: 'fake_command_with_args' got multiple values for argument 'a'\n"
            "-->1: fake_command_with_args(1, 2, 3, 4, 5, a=1)\n"
            "                             ^                ^\n"
            "Syntax: fake_command_with_args(a, b, c)",
            id="three-arg-command-called-with-three-args-two-invalid-args-one-duplicate-kwarg",
        ),
        pytest.param(
            "fake_command_with_args(1, 2, 3, a=1, b=2)",
            "\nline 1: 'fake_command_with_args' got multiple values for argument 'a'\n"
            "-->1: fake_command_with_args(1, 2, 3, a=1, b=2)\n"
            "                             ^          ^\n"
            "Syntax: fake_command_with_args(a, b, c)",
            id="three-arg-command-called-with-three-args-two-duplicate-kwargs",
        ),
    ),
)
def test_duplicate_arguments(compiler, script, error):
    """Duplicate arguments are not allowed.

    Note: duplicate keyword arguments (i.e. multiple arguments specified with the same
    keyword) are tested in ../resolver/test_arguments.py as they are caught by the
    resolver, not builder.
    """
    with pytest.raises(KatScriptError, match=escape_full(error)):
        compiler.compile(script)
