"""
interactiveTest rubric specification.

Peter Mawhorter 2021-6-28
"""

from potluck import specifications as spec

# Tests

# Different test cases as different goals using group_name
for category, case in [
    ("core", [ "Valentina", "3", "2", "1" ]),
    ("core", [ "Hamad", "1", "2.5", "0.75" ]),
    ("extra", [ "Wenyu", "1", "1.19201", "0.5842" ]),
    ("extra", [ "Paolo", "0", "0", "0" ]),
]:
    spec.TestImport(group_name=case[0])\
        .provide_inputs(case, policy="error")\
        .set_context_description(
            (
                f"Program output ('{case[0]}' input)",
                (
                    "We will run your program with some example inputs,"
                    " and observe what it prints."
                ),
                f"Program output ('{case[0]}' input)",
                (
                    "We  ran your program with some example inputs,"
                    " and observed what it printed."
                )
            )
        )
    spec.group("import", group_name=case[0])\
        .goal(category)\
        .test_output(capture_errors=True)\
        .set_goal_description(
            (
                f"Your code prints the correct output ('{case[0]}' input)",
                (
                    "The output when your program is run with certain"
                    " inputs must match the solution output."
                )
            )
        )


# Checks
spec.FunctionCall("input", limits=[4, 4])
spec.FunctionCall("int")
spec.FunctionCall("float")
spec.Check(
    "x7",
    ["7 * _"],
    limits=[1, None],
    name=("multiplication by 7", "multiplications by 7")
)
spec.Check(
    "x7",
    ["7 * _"],
    limits=[1, 1],
    name=("multiplication by 7", "multiplications by 7"),
    category="extra"
)


# Misc goals

spec.NoParseErrors()
spec.DontWasteFruit(category="core")
spec.DontWasteBoxes(category="core")

# Construct our rubric
rubric = spec.rubric()


# Specifications tests using the meta module:
from potluck import meta # noqa E402

meta.example("imperfect")

meta.expect("partial", "procedure", "core", "do not create")
meta.expect("failed", "procedure", "core", "use a multiplication")
meta.expect("failed", "procedure", "extra", "use a multiplication")
meta.expect("partial", "behavior", "core", "Valentina")
meta.expect("partial", "behavior", "core", "Hamad")
meta.expect("partial", "behavior", "extra", "Wenyu")
meta.expect("partial", "behavior", "extra", "Paolo")
