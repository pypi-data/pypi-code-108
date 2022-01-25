"""
Example spec showing snippets functionality.

Peer Mawhorter 2021-8-19
"""

from potluck import specifications as spec
from potluck import context_utils as cu


#------------#
# Test cases #
#------------#

EXAMPLE = [
    {
        "name": "Two",
        "order": 2
    },
    {
        "name": "One",
        "order": 1,
    }
]

spec.TestCase("processData", (EXAMPLE, 3))
spec.TestCase("processData", (cu.SolnValue("DATA"), 3))

spec.group("processData").goal("core")

spec.TestImport().provide_inputs(["A", "B"])
spec.TestImport().provide_inputs(["A", "A"])
spec.TestImport().provide_inputs(["B", "B"])

spec.group("import").goal("extra")


spec.FunctionDef("processData").require(
    spec.FunctionCall("sorted")
)


#--------#
# Rubric #
#--------#

rubric = spec.rubric()


#------#
# Meta #
#------#

from potluck import meta # noqa E402

meta.example("perfect")

meta.example("imperfect")

meta.expect("failed", "procedure", "core", "define")
meta.expect("partial", "product", "core", "processData")
meta.expect("partial", "behavior", "extra", "run")
# Note: the submission fails all of the extra tests, but output is
# similar enough to count as partial success each time


#----------#
# Snippets #
#----------#

from potluck import snippets as sn # noqa E402

sn.Variables(
    "vars", # snippet ID
    "<code>EXAMPLE</code> and <code>DATA</code> variables", # snippet title
    (
        "A simple example of what the input data might look like, and"
        " the slightly more complex <code>DATA</code> variable provided"
        " in the starter code."
    ), # displayed snippet caption
    [ "EXAMPLE", "DATA" ] # list of variable names to display definitions of
).provide({ "EXAMPLE": EXAMPLE })
# provide overrides (or provides missing) solution module values

sn.FunctionCalls(
    "examples", # snippet ID
    "Example results", # title
    (
        "Some examples of what <code>processData</code> should return"
        " for various inputs, using the <code>EXAMPLE</code> and"
        " <code>DATA</code> variables shown above."
    ),
    # caption (note we're assuming the 'vars' snippet will be included
    # first, otherwise this caption doesn't make sense).
    [
        ("processData", (EXAMPLE, 1)),
        ("processData", (EXAMPLE, 2)),
        ("processData", (EXAMPLE, 3)),
        ("processData", (cu.SolnValue("DATA"), 3)),
    ], # list of expressions to evaluate
)

sn.RunModule(
    "run", # ID
    "Full output example", # title
    (
        "An example of what the output should look like when your code"
        " is run. Note that the blue text shows what inputs were"
        " provided in this example."
    ) # caption
).provide_inputs(["A", "B"]) # we're providing some inputs during the run
