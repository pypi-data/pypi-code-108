import os
import numpy as np

from typing import List, Optional

try:
    from SkateTracker.art import ascii_art
except ModuleNotFoundError:
    from art import ascii_art


from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown


def ordinal(n: int):
    """Utility function that gives the correct string ordinal given a number. For example, 1 gives 1st, 2 give 2nd,
     14 gives 14th etc... From: https://stackoverflow.com/questions/9647202/ordinal-numbers-replacement

    :param int n: integer that the user wants to convert to an ordinal string
    :return:
    """
    return "%d%s" % (n, "tsnrhtdd"[(n // 10 % 10 != 1) * (n % 10 < 4) * n % 10::4])


def update_best_times(names: List[str], times: np.array, best_names: List[str], best_times: np.array) -> np.array:
    """Utility function that takes the new times and best times as input and updates the top 3 best times according
     to the new times.

    :param List[str] names: List of strings with the names of the athletes.
    :param np.array times: Numpy array with the times so far.
    :param List[str] best_names: List of strings with the names of the best athletes so far.
    :param np.array best_times: Numpy array with the best times so far.
    :return np.array: Returns a Numpy array with the new top 3 times, shape=(3, nr_laps)
    """
    all_names = np.array(names + best_names, dtype=object)
    all_times = np.vstack((times, best_times))

    total_times = all_times.sum(axis=1)
    total_times[total_times == 0] = np.infty
    total_times_sorted = total_times.argsort()
    return list(all_names[total_times_sorted[:3]]), all_times[total_times_sorted[:3]]


def check_saved(tournament: str, gender: str, length: int) -> str:
    """Check if there already exists file for this particular race

    :param str tournament: string with the name of the tournament where the race is being held.
    :param str gender: string indicating if the race is for Men or Women. Accepted values are ["M", "F"]
    :param int length: integer indicating the length of the race. Accepted values are
     [500, 1000, 1500, 3000, 5000, 10000]

    :return str: Return a string ("y", "n", "no file") Indicating if a file was found if it is going to be used
    """
    gender_name = "Men" if gender == "M" else "Women"

    if os.path.isfile(os.path.join(os.getcwd(), 'skate_data', f"{tournament}_race_{gender_name}_{length}m_data.csv")):
        correct = False
        while not correct:
            use = input("Data for this race was already found. Do you want to use it? [y/n]")
            if not (use == "y" or use == "n"):
                print("ERROR: please input a valid response!")
            else:
                correct = True
    else:
        use = "no file"
    return use


def save_results(tournament: str, gender: str, length: int, names: List[str], times: np.array):
    """Saves the current names and times.

    :param str tournament: string with the name of the tournament where the race is being held.
    :param str gender: string indicating if the race is for Men or Women. Accepted values are ["M", "F"]
    :param int length: integer indicating the length of the race. Accepted values are
     [500, 1000, 1500, 3000, 5000, 10000]

    :param List[str] names: List of strings with the names of the athletes.
    :param np.array times: Numpy array with the times so far.
    :return None:
    """
    if not os.path.isdir(os.path.join(os.getcwd(), 'skate_data')):
        os.mkdir(os.path.join(os.getcwd(), 'skate_data'))

    gender_name = "Men" if gender == "M" else "Women"

    np.savetxt(
        os.path.join(os.getcwd(), 'skate_data', f"{tournament}_race_{gender_name}_{length}m_data.csv"),
        times,
        header=",".join(names),
        delimiter=",",
        comments="",
        fmt="%1.2f"
    )


def load_results(
        tournament: str,
        gender: Optional[str] = None,
        length: Optional[int] = None,
        fname: Optional[str] = None) -> (List[str], np.array):
    """Loads the results if a specific file is specified, or from a given set of parameters

    :param str tournament:
    :param (str, None) fname: string of a previously recorded race.
    :param (str, None) gender: string indicating if the race is for Men or Women. Accepted values are ["M", "F"]
    :param (int, None) length: integer indicating the length of the race. Accepted values are
     [500, 1000, 1500, 3000, 5000, 10000]

    :return (List[str], np.array): Returns the names of all the athletes aas a list and all the results as a Numpy array
    """
    if fname is not None:
        with open(fname) as f:
            names = f.readline().rstrip().split(",")
        results = np.loadtxt(fname, delimiter=",", skiprows=1)
    else:
        if gender is not None and length is not None:
            gender_name = "Men" if gender == "M" else "Women"
            fname = os.path.join(os.getcwd(), 'skate_data', f"race_{gender_name}_{length}m_data.csv")
            with open(fname) as f:
                names = f.readline().rstrip().split(",")
            results = np.loadtxt(fname, delimiter=",", skiprows=1)
        else:
            raise ValueError("ERROR: Please insert a valid gender or length")
    return names, results.T


class Header:
    """Display header with clock."""

    def __rich__(self) -> Panel:
        grid = Table.grid(expand=True)
        grid.add_column(justify="right", width=5)
        grid.add_column(justify='right', width=40, vertical="middle")
        grid.add_column(justify="center", ratio=1)
        grid.add_row(
            " ",
            Markdown("# Welcome to this CLI speed skate race tracker!\n"),
            ascii_art
        )
        return Panel(grid, style="bold white on blue")