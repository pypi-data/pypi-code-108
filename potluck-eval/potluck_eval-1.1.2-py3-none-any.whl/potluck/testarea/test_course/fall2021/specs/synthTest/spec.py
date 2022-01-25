"""
You must write a function called `arpeggio` which adds a 5-note arpeggio
to the current track. It has two parameters: a base pitch, and a
duration. Each added note will use the provided duration, and the first
and last notes will use the provided base pitch. The second and fourth
notes will be three half-steps above the base pitch, while the third note
will be seven half-steps above the base pitch.

[An example of correct behavior](#snippet:arpeggio)

Note that to set up expectations for arpeggio, you can use the
`printTrack` function to print descriptions of each note in the current
track, and so you can use `captureOutput` along with
`expectOutputContains` to test for the presence of certain notes or note
sequences. Here is [an example of this expectation
setup](#snippet:expectations). Your tests do not have to specify every
note that should be present, although they may if you wish. You will need
to [create at lest two expectations for track
descriptions](#goal:core.test:defines_enough) in this manner.
"""

import wavesynth

from potluck import specifications as spec
from potluck import contexts


# Make sure to reset the current track before we import:
# TODO: This shouldn't be necessary?!?
contexts.ModuleContext(prep=lambda _: wavesynth.resetTracks())

# Define a unit test
for case in [
    (wavesynth.C4, 0.5),
    (wavesynth.A4, 0.25),
    (wavesynth.B3, 0.3)
]:
    spec.TestCase("arpeggio", case)

spec.group("arpeggio").test_wavesynth_notes().goal("core")


# Second test of two calls back-to-back
spec.TestBlock(
    "double",
    "arpeggio(C4, 0.3)\narpeggio(E4, 0.2)", # visible
    "from wavesynth import *\narpeggio(C4, 0.3)\narpeggio(E4, 0.2)" # actual
)

spec.group("block:double")\
    .test_wavesynth_notes()\
    .goal("extra")\
    .set_goal_description(
        (
            "<code>arpeggio</code> adds to the end of the track",
            (
                "We will check the notes produced by calling"
                " <code>arpeggio</code> twice; it should create two"
                " arpeggios which happen one after the other."
            ),
            "<code>arpeggio</code> adds to the end of the track",
            (
                "We checked whether the notes produced by calling"
                " <code>arpeggio</code> twice were two arpeggios which"
                " happen one after the other."
            ),
        )
    )

# Checks
spec.FunctionDef("arpeggio", 2).require(
    spec.FunctionCall("addNote", limits=[5, 5]).softmin().softmax()
)

# Misc goals

spec.RequireDocstrings()

# Testing goals

# TODO: it's awkward that we can't require tests for `arpeggio`
# directly...
spec.RequireTestCases({ "printTrack": 2 })
spec.TestsMustPass()

# Construct our rubric
rubric = spec.rubric()


# Specifications tests using the meta module:
from potluck import meta # noqa E402

meta.example("imperfect")

meta.expect("partial", "#goal:core.check:def-arpeggio$")
meta.expect("partial", "#goal:core.check:def-arpeggio:call-addNote")

# These two expectations are the same, using a goal rubric path and a
# goal identifier
meta.expect("failed", "behavior", "core", "arpeggio")
meta.expect("failed", "#goal:core.test:arpeggio$")

meta.expect("failed", "#goal:extra.test:block:double")

meta.expect_validation("partial", "testing", "core", "defines required")
meta.expect_validation("partial", "testing", "extra", "checks must succeed")


# Snippets for the instructions
from potluck import snippets as sn # noqa E402

sn.Blocks(
    "arpeggio",
    "Examples for `arpeggio`",
    "Some examples of correct results for `arpeggio`:",
    [
        "arpeggio(C4, 0.5)\nprintTrack()",
        "arpeggio(A4, 0.2)\nprintTrack()",
        "arpeggio(G5, 0.3)\nprintTrack()",
    ]
).capture_wavesynth(just_capture="audio").play_audio()


def discard_first_log_line(ctx):
    """
    Edits a context by removing the first line of its error log output.
    """
    if "error_log" in ctx:
        ctx["error_log"] = '\n'.join(ctx["error_log"].splitlines()[1:])


sn.Blocks(
    "expectations",
    "How to set up expectations",
    (
        "Here's a example of how to set up expectations for `wavesynth`"
        " notes using `captureOutput` along with `printTrack`."
    ),
    [
        """\
from wavesynth import *

# Here's some code that creates notes
setPitch(C4)
addNote(0.2)
stepUp()
addNote(0.3)

# This isn't necessary, but we print the track first so you can see what
# the expectations are dealing with
printTrack()

import optimism as opt

# Use captureOutput to set up a test case for the printTrack output
opt.captureOutput()
opt.testCase(printTrack())
opt.expectOutputContains("a 0.2s keyboard note at C4")
opt.expectOutputContains("and a 0.3s keyboard note at D4")
# Note: our expectations don't constrain the volume level, but they could
"""
    ]
)\
    .capture_wavesynth(just_capture="audio")\
    .play_audio()\
    .final_edit(discard_first_log_line)
