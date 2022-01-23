#
import nbformat


def point_bad_line(bad_line, source):
    result = ""
    for i, s in enumerate(source.split("\n")):
        result += (">>>" if i == bad_line else "   ") + s + "\n"
    return result


def _compute_sources(cell, k=None):
    if k is not None:
        print(f"Student code block(s) in cell {k}")
    exercise = []
    solution = []
    section = 0  # 0 == common, 1 == exercise, 2 == solution
    indent = 0
    for i, s in enumerate(cell.source.split("\n")):
        solution.append(s)
        if "STUDENT" in s:
            if "BEGIN" in s:
                exercise.append(s)
                indent = s.find("#")
                assert (
                    section == 0
                ), f'@@@ BAD SEQUENCE - "STUDENT BEGIN" NOT EXPECTED @@@:\n\n{point_bad_line(i, cell.source)}'
                section = 1
            elif "END" in s:
                exercise.append(s)
                assert (
                    section == 1
                ), f'@@@ BAD SEQUENCE - "STUDENT END" NOT EXPECTED @@@:\n{point_bad_line(i, cell.source)}'
                section = 2
            elif "SOLUTION" in s:
                assert (
                    section == 2
                ), f'@@@ BAD SEQUENCE - "STUDENT SOLUTION" NOT EXPECTED @@@:\n{point_bad_line(i, cell.source)}'
                section = 0
                print("[block processed ok]", end="", flush=True)
            else:
                assert (
                    1 == 0
                ), f'@@@ ERROR: "STUDENT" FOUND WITH NO KEYWORD (BEGIN, END or SOLUTION) @@@:\n{point_bad_line(i, cell.source)}'
                pass
        else:
            if section == 1:
                exercise.append((" " * indent) + s[indent + 2 :])
            elif section == 0:
                exercise.append(s)

    assert section == 0, "@@@ SEQUENCE OF STUDENT BEGIN/END/SOLUTION NOT RESPECTED @@@"
    print()
    return "\n".join(exercise), "\n".join(solution)


def _is_string_in_cell(cell, find_str="STUDENT"):
    return any(find_str in s for s in cell.source.split("\n"))


def generate_exercise_notebook(source, exercise=None):
    nb = nbformat.read(source, nbformat.NO_CONVERT)
    print("\n==== HUB EXERCISE NOTEBOOK GENERATION BEGIN =====")
    print(f"Source NB: {source}")

    if exercise is None:
        exercise = source.replace("SOLUTION", "EXERCISE")
        print(
            f'>> No exercise filename specified, replace "SOLUTION" with "EXERCISE" in {source}: {exercise}'
        )

    assert (
        exercise != source
    ), f"@@@ exercise notebook filename ({exercise}) must be different than solution ({solution}) @@@ "

    # exercise notebook now strict copy of solution notebook
    enb = nb.copy()
    for c in enb.cells:
        if c.cell_type == "code":
            c.outputs = []

    # cells id with code
    sk = [
        k
        for k in range(len(nb.cells))
        if nb.cells[k].source and nb.cells[k].cell_type == "code"
    ]

    for k in sk:
        if _is_string_in_cell(nb.cells[k], "STUDENT"):
            e, s = _compute_sources(nb.cells[k], k)
            # print(enb.cells[k].source)
            # print("*********************************************")
            # print(e)
            # print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
            enb.cells[k].source = e
            # print(enb.cells[k].source)
            # print("#############################################")
            # snb.cells[k].source = s
            # print("@@@@@@@@@@@@@@@", e == s)

    professor_cells = [
        k
        for k in range(len(nb.cells[k]))
        if _is_string_in_cell(enb.cells[k], "generate_exercise_notebook")
    ]
    # [enb.cells.pop(k) for k in professor_cells]
    for k in professor_cells:
        enb.cells[k].source = ""
    print(f"Professor cells removed: {professor_cells}")

    nbformat.write(enb, exercise)
    print(f"Exercise NB: {exercise}")
    print("==== HUB EXERCISE NOTEBOOK GENERATION END =====")