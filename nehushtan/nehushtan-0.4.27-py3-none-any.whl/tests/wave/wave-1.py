from nehushtan.wave.Note import Note
from nehushtan.wave.SimpleComposer import SimpleComposer


def write_part_v1(composer: SimpleComposer):
    composer.add_note_to_line(Note(name="E"))
    composer.add_note_to_line(Note(name="E"))
    composer.add_note_to_line(Note(name="F"))
    composer.add_note_to_line(Note(name="G"))
    composer.add_note_to_line(Note(name="G"))
    composer.add_note_to_line(Note(name="F"))
    composer.add_note_to_line(Note(name="E"))
    composer.add_note_to_line(Note(name="D"))
    composer.add_note_to_line(Note(name="C"))
    composer.add_note_to_line(Note(name="C"))
    composer.add_note_to_line(Note(name="D"))
    composer.add_note_to_line(Note(name="E"))
    composer.add_note_to_line(Note(name="E", beats=1.5))
    composer.add_note_to_line(Note(name="D", beats=0.5))
    composer.add_note_to_line(Note(name="D", beats=2))

    composer.add_note_to_line(Note(name="G", group=4), 1)
    composer.add_note_to_line(Note(name="C", group=5), 1)
    composer.add_note_to_line(Note(name="A", group=4), 1)
    composer.add_note_to_line(Note(name="C", group=5), 1)
    composer.add_note_to_line(Note(name="G", group=5), 1)
    composer.add_note_to_line(Note(name="F", group=5), 1)
    composer.add_note_to_line(Note(name="E", group=5), 1)
    composer.add_note_to_line(Note(name="D", group=5), 1)
    composer.add_note_to_line(Note(name="C", group=5), 1)
    composer.add_note_to_line(Note(name="C", group=5), 1)
    composer.add_note_to_line(Note(name="D", group=5), 1)
    composer.add_note_to_line(Note(name="E", group=5), 1)
    composer.add_note_to_line(Note(name="E", group=5, beats=1.5), 1)
    composer.add_note_to_line(Note(name="D", group=5, beats=0.5), 1)
    composer.add_note_to_line(Note(name="D", group=5, beats=2), 1)


def write_part_v2(composer: SimpleComposer):
    composer.add_notes_to_lines([
        Note(name="E"),
        Note(name="C", group=3),
    ])
    composer.add_notes_to_lines([
        Note(name="E"),
        Note(name="G", group=3),
    ])
    composer.add_notes_to_lines([
        Note(name="F"),
        Note(name="A", group=3),
    ])
    composer.add_notes_to_lines([
        Note(name="G"),
        Note(name="B", group=3),
    ])
    composer.add_notes_to_lines([
        Note(name="G"),
        Note(name="B", group=3),
    ])
    composer.add_notes_to_lines([
        Note(name="F"),
        Note(name="A", group=3),
    ])
    composer.add_notes_to_lines([
        Note(name="E"),
        Note(name="G", group=3),
    ])
    composer.add_notes_to_lines([
        Note(name="D"),
        Note(name="F", group=3),
    ])
    composer.add_notes_to_lines([
        Note(name="C"),
        Note(name="C", group=3),
    ])
    composer.add_notes_to_lines([
        Note(name="C"),
        Note(name="E", group=3),
    ])
    composer.add_notes_to_lines([
        Note(name="D"),
        Note(name="G", group=3),
    ])
    composer.add_notes_to_lines([
        Note(name="E"),
        Note(name="E", group=3),
    ])
    composer.add_note_to_line(Note(name="E", beats=1.5), 0)
    composer.add_note_to_line(Note(name="C", group=3, beats=0.5), 1)
    composer.add_note_to_line(Note(name="E", group=3, beats=0.5), 1)
    composer.add_note_to_line(Note(name="G", group=3, beats=0.5), 1)

    composer.add_notes_to_lines([
        Note(name="D", beats=0.5),
        Note(name="D", group=3, beats=0.5),
    ])

    composer.add_note_to_line(Note(name="D", beats=2), 0)
    composer.add_note_to_line(Note(name="G", group=3, beats=0.5), 1)
    composer.add_note_to_line(Note(name="B", group=3, beats=1.5), 1)


if __name__ == '__main__':
    composer = SimpleComposer(r"/Users/leqee/code/nehushtan/debug/wave/test-1.wav")
    write_part_v2(composer)
    composer.close()
