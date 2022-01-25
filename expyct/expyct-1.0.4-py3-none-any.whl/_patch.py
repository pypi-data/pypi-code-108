import ast
from functools import wraps
from typing import List, Mapping, Type


def patch_pytest_assert_comp_order():
    """
    Monkeypatches pytest's assertion rewriting logic by switching around the left and right
    operands of the comparison. This is needed because pytest (and IDEs) assumes the order to
    be `actual == expected`, but Expyct works better with `expected == actual` because then
    the `__eq__` method of the left Expyct objects get called.
    """

    import _pytest.assertion

    def invert_operator(op: ast.cmpop) -> ast.cmpop:
        mapping: Mapping[Type[ast.cmpop], ast.cmpop] = {
            ast.Lt: ast.Gt(),
            ast.LtE: ast.GtE(),
            ast.Gt: ast.Lt(),
            ast.GtE: ast.LtE(),
        }
        return mapping.get(type(op), op)

    def swap_compare(compare: ast.Compare) -> ast.Compare:
        # Swap left and right sides of comparison
        compare.left, compare.comparators[0] = compare.comparators[0], compare.left
        # Invert asymmetric operators <, <=, >, >=
        compare.ops[0] = invert_operator(compare.ops[0])
        return compare

    orig_visit_Assert = _pytest.assertion.rewrite.AssertionRewriter.visit_Assert

    @wraps(orig_visit_Assert)
    def new_visit_Assert(self, assert_: ast.Assert) -> List[ast.stmt]:
        stmts = orig_visit_Assert(self, assert_)
        try:
            i_compare = next(
                (i, stm)
                for i, stm in enumerate(stmts)
                if isinstance(stm, ast.Assign) and isinstance(stm.value, ast.Compare)
            )[0]
        except StopIteration:
            pass
        else:
            # Only the comparison is swapped. The output added by pytest is not changed
            stmts[i_compare].value = swap_compare(stmts[i_compare].value)
        return stmts

    _pytest.assertion.rewrite.AssertionRewriter.visit_Assert = new_visit_Assert
