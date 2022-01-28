import finesse
import locale

def test_cyexpr_parse():
    """Simple test to see if cyexpr parses strings correctly 
    after setting the user locale."""

    # set the user locale (this is done within finesse.__init__)
    locale.setlocale(locale.LC_ALL, "")

    # should pass even if user numeric locale is set to `.,`
    assert finesse.cyexpr.test_expr('(0.0+1)')
    assert finesse.cyexpr.test_expr('(1.0-0.5)')

    # should also pass
    assert finesse.cyexpr.test_expr('(0,0+1)')
    assert finesse.cyexpr.test_expr('(1,0-0.5)')

    # should fail since its an invalid expression
    assert not finesse.cyexpr.test_expr('(0!0+1)')