"""
Variable-definition-based grading test.
"""

from potluck import specifications as spec

for n in range(1, 5):
    vn = f"var{n}"
    spec.TestValue(vn)
    spec.group(vn).goal("core")

rubric = spec.rubric()

from potluck import meta # noqa E402

meta.example("imperfect")

meta.expect("failed", "product", "core", "var2")
meta.expect("failed", "product", "core", "var3")

# var4 should succeed despite structural differences


from potluck import snippets as sn # noqa E402

sn.Variables(
    "vars",
    "Correct values",
    "These are the answers!",
    [
        "var1",
        "var2",
        "var3",
        "var4",
    ]
)
