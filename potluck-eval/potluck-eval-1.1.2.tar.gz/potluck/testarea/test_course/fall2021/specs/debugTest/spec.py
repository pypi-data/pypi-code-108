"""
debugTest rubric specification

Peter Mawhorter 2021-6-28
"""

from potluck import specifications as spec


# We want to run the file and see what happens
base_cases = [
    spec.TestImport()
        .provide_inputs(inputs, policy="hold")
        .set_context_description(
            (
                f"Program output (test #{i+1})",
                (
                    "We will run your program with some example inputs."
                    " It must not crash. The inputs used are integers"
                    " between 1 and 20, as the program requires."
                ),
                f"Program output (test #{i+1})",
                (
                    f"We ran your program with <code>{inputs[0]}</code>"
                    f" and <code>{inputs[1]}</code> as the inputs."
                )
            )
        )

    for i, inputs in enumerate([
        ["15", "7", ""],
        ["5", "6", ""],
    ])
]


base = spec.group("import").test_output(capture_errors=True)

base.refine(
    spec.Find,
    r"(?m)^Let.*$",
    "the first line of output",
    missing_result="-not found-"
)\
    .goal("core")\
    .compare_strings_firmly()\
    .set_goal_description(
        (
            "bug #1",
            "Hint Causes a <code>SyntaxError</code>",
            "bug #1 (string quotation marks)",
            (
                "You need to change the single-quotes on line 13"
                " into double quotes because of the apostrophe in"
                " \"Let's\"."
            )
        )
    )

base.refine(
    spec.Find,
    r"(?m)^The smaller number is.*$",
    "the 'smaller number' line",
    missing_result="-not found-"
).goal("core")\
    .compare_strings_firmly()\
    .set_goal_description(
        (
            "bug #2",
            "Hint: How does int() work?",
            "bug #2 (type conversion)",
            (
                "The call to <code>int</code> on line 17 converts"
                " <code>firstNum</code> to an integer, but the result"
                " is discarded. The code on line 19 is correct in that"
                " it converts the value and then overwrites the result."
                " Changing line 17 to look like line 19 solves the"
                " issue, which doesn't manifest until line 27, when the"
                " types of the values change how <code>min</code>"
                " works."
            )
        ),
    )

base.refine(
    spec.Find,
    r"(?m)^The numbers you.*$",
    "the line 'The numbers you entered...'",
    missing_result="-not found-"
).goal("core")\
    .compare_strings_firmly()\
    .set_goal_description(
        (
            "bug #3",
            "Hint: Should show both numbers.",
            "bug #3 (variable vs. string)",
            (
                "On line 25, the quotes around the word"
                " <code>secondNum</code> tell Python to literally use"
                " that text, rather than using the value of the"
                " variable with that name. Earlier on the same line,"
                " <code>firstNum</code> is used correctly, without"
                " quotes."
            )
        )
    )

base.refine(
    spec.Find,
    r"(?m)^The larger number is.*$",
    "the 'larger number' line",
    missing_result="-not found-"
).goal("core")\
    .compare_strings_firmly()\
    .set_goal_description(
        (
            "bug #4",
            "Hint: Is 12 larger than 5?",
            "bug #4 (string max)",
            (
                "On line 26, the <code>max</code> function is used, but"
                " the <code>str</code> function is used inside of the"
                " function call to convert both arguments to strings."
                " The arguments should be compared as numbers, not as"
                " text, because when compared as text alphabetical"
                " ordering is used, making '7' count as \"larger than\""
                " '15' since '7' comes after '1' in the dictionary."
            )
        )
    )

base.refine(
    spec.Find,
    r"(?m)^=.*=\n=.*=$",
    "the two lines of '=' signs",
    missing_result="-not found-"
).goal("core")\
    .compare_strings_firmly()\
    .set_goal_description(
        (
            "bug #5",
            "Hint: How are the bars created?",
            "bug #5 (string repetition)",
            (
                "On line 29, a series of equals signs to represent a"
                " horizontal bar is printed, using multiplication"
                " between a string and a number. Line 30 has the bug,"
                " where addition is attempted instead of"
                " multiplication."
            )
        )
    )

base.refine(
    spec.Find,
    r"(?m)^\[Addition] What is.*$",
    "the addition question",
    missing_result="-not found-"
).goal("core")\
    .compare_strings_firmly()\
    .set_goal_description(
        (
            "bug #11", # numbered 11 to test meta goal-name-disambiguation
            "Hint: Can you add a number to a string?",
            "bug #11 (concatenation vs. addition)",
            (
                "Online 34, concatenation of strings is used to build"
                " a prompt. However, while <code>firstNum</code> is"
                " turned into a string using the <code>str</code>"
                " function, <code>secondNum</code> is not. Depending on"
                " what you did with bug #2, this will probably cause an"
                " error, as numbers and strings cannot be directly"
                " added together."
            )

        )
    )


spec.FunctionCall(
    "int",
    limits=[2, 2],
).set_description(
    "Use <code>int()</code> in exactly two places.",
    (
        "To minimize repetition, use the <code>int()</code>"
        " function in exactly two places."
    ),
    "Use <code>int()</code> in exactly two places.",
    (
        "It's only necessary to use <code>int()</code> twice:"
        " right at the very start after collecting inputs you"
        " can convert the to integers (once per input) and then"
        " use those variables throughout the rest of the program."
    )
)


# Construct our rubric
rubric = spec.rubric()


# Specifications tests using the meta module:
from potluck import meta # noqa E402

meta.example("imperfect")

meta.expect_warnings('invalid syntax (debugMe.py, line 13)')

for bug_nr in [1, 2, 3, 5, 11]:
    meta.expect(
        "failed",
        "behavior",
        "core",
        f"bug #{bug_nr}$"
    )

meta.expect(
    "partial",
    "behavior",
    "core",
    "bug #4$"
)
