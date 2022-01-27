from sym.sdk import hook, reducer


@hook
def simple_hook():
    return "simple_hook"


@reducer
def simple_reducer():
    return "simple_reducer"


class TestReducer:
    def test_all(self):
        assert simple_hook() == "simple_hook"
        assert simple_reducer() == "simple_reducer"
