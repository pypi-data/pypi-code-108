from difflib import get_close_matches
from task1 import task


def program_run(afterkeyword: str) -> None:
    try:
        print("Approximate to", approx_program := get_close_matches(afterkeyword, task.getprogramnames(), n = 1, cutoff = 0.7))
        print("No program found") if not approx_program else task.programopener([approx_program[0]])
    except: print("Sorry the program is not yet supported.Please request the developer for more info.")
