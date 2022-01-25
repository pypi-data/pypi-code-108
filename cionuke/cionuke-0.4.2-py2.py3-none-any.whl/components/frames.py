import nuke

from cioseq.sequence import Sequence
import re

SCOUT_AUTO_REGEX = re.compile(r"^auto[, :]+(\d+)$")


def build(submitter):
    """Build knobs to specify frame ranges."""
    knob = nuke.Int_Knob("cio_chunk_size", "Chunk size")
    knob.setValue(1)
    submitter.addKnob(knob)

    knob = nuke.String_Knob("cio_custom_frames", "Custom frames", "1-10")
    submitter.addKnob(knob)

    knob = nuke.Boolean_Knob("cio_use_custom_frames", "Use custom range")
    knob.clearFlag(nuke.STARTLINE)
    knob.setValue(False)
    submitter.addKnob(knob)

    knob = nuke.String_Knob("cio_scout_tasks", "Scout tasks", "auto:3")
    submitter.addKnob(knob)

    knob = nuke.Boolean_Knob("cio_use_scout_tasks", "Use scout tasks    ")
    knob.clearFlag(nuke.STARTLINE)
    knob.setValue(True)
    submitter.addKnob(knob)

    knobChanged(submitter, submitter.knob("cio_use_custom_frames"))


def knobChanged(node, knob):
    """Hide/show string knobs based on checkbox changes."""


    if knob.name() not in ["cio_use_scout_tasks", "cio_use_custom_frames"]:
        return

    value = bool(node.knob("cio_use_custom_frames").getValue())
    node.knob("cio_custom_frames").setVisible(value)

    value = bool(node.knob("cio_use_scout_tasks").getValue())
    node.knob("cio_scout_tasks").setVisible(value)


def affector_knobs():
    return [
        "cio_chunk_size",
        "cio_custom_frames",
        "cio_use_custom_frames",
        "cio_scout_tasks",
        "cio_use_scout_tasks",
    ]


def resolve(submitter, **kwargs):
    main_sequence, scout_sequence = get_sequences(submitter)

    tasks = []
    chunks = main_sequence.chunks()
    for i, chunk in enumerate(chunks):
        arg = "{}-{}".format(chunk.start, chunk.end)
        submitter.knob("cio_range_args").setValue(arg)
        cmd = submitter.knob("cio_task").getValue()

        tasks.append({"command": cmd, "frames": str(chunk)})

    return {"tasks_data": tasks, "scout_frames": ",".join([str(s) for s in scout_sequence or []])}


def get_sequences(submitter):
    """
    Create a cioseq.sequence for each of main frames and scout frames

    Returns:
        [tuple of sequence]: main frames and scout frames
    """
    chunk_size = submitter.knob("cio_chunk_size").getValue()
    use_custom_frames = submitter.knob("cio_use_custom_frames").getValue()
    scout_tasks = submitter.knob("cio_scout_tasks").getValue()
    use_scout_tasks = submitter.knob("cio_use_scout_tasks").getValue()

    frame_spec = submitter.knob("cio_custom_frames").getValue()
    if not use_custom_frames:
        frame_spec = _get_scene_frame_spec()

    try:
        main_sequence = Sequence.create(
            frame_spec, chunk_size=chunk_size, chunk_strategy="progressions"
        )
    except (ValueError, TypeError):
        main_sequence = None

    scout_sequence = None
    if use_scout_tasks and main_sequence:

        match = SCOUT_AUTO_REGEX.match(scout_tasks)
        if match:
            samples = int(match.group(1))
            scout_sequence = main_sequence.subsample(samples)
        else:
            try:
                scout_sequence = Sequence.create(scout_tasks)
            except (ValueError, TypeError):
                scout_sequence = None

    return (main_sequence, scout_sequence)


def _get_scene_frame_spec():
    root = nuke.Root()
    ff = int(root["first_frame"].getValue())
    lf = int(root["last_frame"].getValue())
    return "{}-{}".format(ff,lf)
