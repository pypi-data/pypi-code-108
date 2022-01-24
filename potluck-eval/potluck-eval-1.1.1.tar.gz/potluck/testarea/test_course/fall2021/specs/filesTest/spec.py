"""
This task involves writing three functions: `listFile`, `grep`, and
`addRecords`.

- `listFile` prints each line of a target file, along with line numbers.
- `grep` reads lines from one file, finds those that contain a certain
    string fragment, and then writes those to a second file.
- `addRecords` appends lines to a file based on a list of strings, adding
    a newline character to the end of each string as it writes into the
    file so that they appear as different lines.

Note that these tests do not clean up created files, as it's assumed
that the entire sandbox will be cleaned up at some point.
"""

from potluck import specifications as spec
from potluck import harness


# Establish test cases

spec.TestCase('listFile', ('birds.txt',))
spec.TestCase('listFile', ('fish.txt',))
spec.TestCase('listFile', ('dir/mammals.txt',))

spec.group("listFile").goal("core")\
    .test_output()\
    .compare_strings_semi_strict()


for info_file, grep_for in [
    ("birds.txt", "er"),
    ("birds.txt", "xy"),
    ("fish.txt", "er"),
    ("fish.txt", "xy"),
    ("dir/mammals.txt", "er"),
]:
    write_to = info_file + '.' + grep_for
    spec.TestCase(
        'grep',
        (info_file, grep_for, write_to)
    ).capture_file_contents(write_to)

spec.group("grep").goal("core")

for records, pre in [
    (['a', 'b', 'c'], ''),
    (['a', 'b', 'c'], 'a\nb\nc\n'),
    (['x', 'y', 'z'], 'hello'),
]:
    spec.TestCase('addRecords', ('records.txt', records))\
        .do_setup(harness.file_contents_setter('records.txt', pre))

spec.group("addRecords").goal("extra").test_file_contents("records.txt")


# Create rubric

rubric = spec.rubric()


# Meta tests

from potluck import meta # noqa E402

meta.example("imperfect")

meta.expect("failed", "product", "core", "grep")
meta.expect("failed", "behavior", "core", "listFile")
meta.expect("failed", "behavior", "extra", "addRecords")


# Snippets

from potluck import snippets as sn # noqa E402

sn.FunctionCalls(
    "listFile",
    "`listFile` examples",
    """\
These examples show how `listFile` should work on the birds and fish
lists provided with the starter code.""",
    [
        ("listFile", ("birds.txt",)),
        ("listFile", ("fish.txt",))
    ]
)

grep_examples = [
    ("grep", ("birds.txt", "er", "birds.txt.er")),
    ("grep", ("fish.txt", "er", "fish.txt.er")),
    ("grep", ("dir/mammals.txt", "er", "dir/mammals.txt.er")),
]

grep_sn = sn.FunctionCalls(
    "grep",
    "`grep` examples",
    """\
These examples show how `grep` should work on the birds and fish
lists provided with the starter code.""",
    grep_examples
)

for test, example in zip(grep_sn.tests, grep_examples):
    outfile = example[1][-1]
    test.capture_file_contents(outfile)

grep_sn.show_file_contents()
