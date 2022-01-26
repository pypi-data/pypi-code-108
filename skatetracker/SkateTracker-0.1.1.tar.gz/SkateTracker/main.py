"""
CLI tool (python module) that helps you track lap times during a speed skating race.
It will also predict the final time, as well as visualise some useful  statistics
"""
import argparse
from math import ceil

from rich import print

try:
    from SkateTracker.layout import *
    from SkateTracker.utils import *
    from SkateTracker.plot import create_plotext_panel
except ModuleNotFoundError:
    from layout import *
    from utils import *
    from plot import create_plotext_panel


def welcome_print(tournament: str, gender: str, length: int, prediction_method: str, accumulate: str, save: str) -> Panel:
    """Prints a welcome message showing what parameters have been set and wat will happen next.

    :param str tournament: string with the name of the tournament where the race is being held.
    :param str gender: string indicating if the race is for Men or Women. Accepted values are ["M", "F"]
    :param int length: integer indicating the length of the race. Accepted values are
     [500, 1000, 1500, 3000, 5000, 10000]

    :param str prediction_method: string indicating which prediction method to use. NOT IMPLEMENTED YET
    :param str accumulate: string which indicates if all previous results should also be shown. Accepted values
     ["y", "n"]. NOT IMPLEMENTED YET

    :param str save: string which indicates if the results after each race should be saved to a csv file.
     If the user exits the tool and restarts it again with the same settings, it will use this file to load the previous
     results type

    :return rich.Panel: returns a rich.Panel with the welcome message
    """
    gender_name = "Men" if gender == "M" else "Women"
    accumulated = "be accumulated" if accumulate == "y" else "not be accumulated"
    save_text = "be saved" if save == "y" else "not be saved"

    panel = Panel(
        f"I will start tracking the race with the following parameters:\n\n"
        f"\t-- {gender_name}'s {length}m race in {tournament},\n"
        f"\t-- Predictions will be made with {prediction_method},\n"
        f"\t-- The results will {accumulated},\n"
        f"\t-- The results will {save_text}.\n\n",
        title="CLI speed skate race tracker",
        padding=(2, 2),
        border_style="green"
    )

    return panel


def make_instruction_panel() -> Panel:
    """Prints the instruction message showing what the user has to do next

    :return rich.Panel: returns a rich.Panel with the instruction message
    """
    panel = Panel(
        Align.center(
            f"During every race, you will be able to track one athlete or both athletes.\n\n"
            f"Indicate which one you want by typing the name(s) of the athlete(s) in a comma separated fashion",
            vertical="middle"
        ),
        title="Instructions",
        padding=(2, 2),
        border_style="red",
    )
    return panel


def create_race_view(
        gender: str,
        names: List[str],
        times: np.array,
        nr_laps: int,
        best_names: List[str],
        best_times: np.array,
        race_layout: Layout,
        first: bool = False,
        final: bool = False) -> None:
    """Creates the main race view and layout.

    :param str gender: string indicating if the race is for Men or Women. Accepted values are ["M", "F"].
    :param List[str] names: List of strings with the names of the athletes.
    :param np.array times: Numpy array with the times so far.
    :param int nr_laps: integer indicating how many laps this race is going to take.
    :param List[str] best_names: List of strings with the names of the best athletes so far.
    :param np.array best_times: Numpy array with the best times so far.
    :param rich.Layout race_layout: rich.Layout object with the prescribed layout for all the tables and plots
    :param bool first: Boolean indicating if this is the first time making the view. Otherwise, the progress bar will
     be advanced instead of initiated.

    :param bool final: Boolean indicating if this is the final time the view will be shown. THe progress bar does not
     need to be progressed or initiated then.

    :return None: Nothing
    """

    # Extract all the sub-layouts from the main race layout
    plotext_layout = race_layout["plotext"]
    current_race_layout = race_layout["main"]["current_race"]
    best_results_layout = race_layout["main"]["best_results"]
    progress_layout = race_layout["progress"]

    if first:
        # For the first iteration, the progress panel needs to be created and advanced
        progress_panel = create_progress_panel(nr_laps)
        progress_layout.update(progress_panel)
    else:
        if not final:
            # If this iteration is not the firs or the last, then we advance the progress bar
            progress_panel = progress_layout.renderable
            progress_panel.renderable.renderable.advance(progress_panel.renderable.renderable.task_ids[0])
            progress_layout.update(progress_panel)

    _ = create_plotext_panel(
        gender,
        nr_laps,
        names,
        times,
        plotext_layout
    )

    table_progression = create_lap_time_table(names, times, best_times)
    table_best_results = create_best_table(best_names, best_times)

    current_race_layout.update(table_progression)
    best_results_layout.update(table_best_results)


def track_race(
        gender: str,
        names: List[str],
        nr_laps: int,
        best_names: List[str],
        best_times: np.array) -> (np.array, Layout):
    """For each race, this function does the tracking of the race. It will create the race layout and view. For each
     lap it will ask the user for the lap times and incorporate them into the views

    :param str gender: string indicating if the race is for Men or Women. Accepted values are ["M", "F"]
    :param List[str] names: List of strings with the names of the athletes.
    :param int nr_laps: integer indicating how many laps this race is going to take.
    :param List[str] best_names: List of strings with the names of the best athletes so far.
    :param np.array best_times: Numpy array with the best times so far.
    :return (np.array, rich.Layout): Returns the final lap times of the athletes.
     So that they may used to save the times and update the best times. Also returns the layout so that all the results
     can be shown one last time.
    """
    n_athletes = len(names)
    times = np.zeros((len(names), nr_laps))

    race_layout = make_race_layout()
    create_race_view(
        gender,
        names,
        times,
        nr_laps,
        best_names,
        best_times,
        race_layout,
        first=True
    )
    print(race_layout)

    for i in range(nr_laps):
        correct = False
        while not correct:
            try:
                lap_time = np.array([float(t) for t in input(f"Lap times of {ordinal(i+1)} lap:").replace(" ", "").split(",")])
            except ValueError:
                print("ERROR: You need to enter numbers!")
            else:
                if lap_time.shape[0] != n_athletes:
                    print("ERROR: you need to enter the correct amount of times!")

                else:
                    correct = True
                    times[:, i] = lap_time

                # For now the view is erased and updated each time. The reason being that rich.Live does not work
                # nicely with input and a progress bar. (As far as I could figure out)
                os.system("clear")
                create_race_view(
                    gender,
                    names,
                    times,
                    nr_laps,
                    best_names,
                    best_times,
                    race_layout
                )
                print(race_layout)
    return times, race_layout


def main_tracking(tournament: str, gender: str, length: int, prediction_method: str, accumulate: str, save: str):
    """Main function that parses the initial arguments. Prompts the user for the names of the athletes and calls
     all the other functions that create the layouts, views, tracking etc.

    :param str tournament: string with the name of the tournament where the race is being held.
    :param str gender: string indicating if the race is for Men or Women. Accepted values are ["M", "F"]
    :param int length: integer indicating the length of the race. Accepted values are
     [500, 1000, 1500, 3000, 5000, 10000]

    :param str prediction_method: string indicating which prediction method to use. NOT IMPLEMENTED YET
    :param str accumulate: string which indicates if all previous results should also be shown. Accepted values
     ["y", "n"]. NOT IMPLEMENTED YET

    :param str save: string which indicates if the results after each race should be saved to a csv file.
     If the user exits the tool and restarts it again with the same settings, it will use this file to load the previous
     results type

    :return None:
    """

    # verify if all the arguments are correct (some combinations are not possible)
    if gender == "M" and length == 3000:
        raise ValueError("This combination is not a valid race!")
    if gender == "F" and length == 10000:
        raise ValueError("This combination is not a valid race!")

    use = check_saved(tournament, gender, length)
    # Creates the main start layout
    layout_start = make_start_layout()

    # Below the sub-layouts are extracted and updated for the welcome view
    layout_start["header"].update(Header())

    welcome_panel = welcome_print(tournament, gender, length, prediction_method, accumulate, save)
    instruction_panel = make_instruction_panel()
    layout_start["main"]["side"].update(instruction_panel)
    layout_start["main"]["body"].update(welcome_panel)
    print(layout_start)

    nr_laps = ceil(length / 400)
    best_names = ["None", "None", "None"]
    best_times = np.zeros((3, nr_laps))

    if use == "y":
        all_names, all_results = load_results(tournament, gender=gender, length=length)
        best_names, best_times = update_best_times(all_names, all_results, best_names, best_times)
    else:
        all_names = []
        all_results = []

    tracking = True
    while tracking:
        names = input("The names of the athletes are: ").replace(" ", "").split(",")
        # A full race is tracked, the lap times and final race view are returned
        lap_times, race_layout = track_race(gender, names, nr_laps, best_names, best_times)
        best_names, best_times = update_best_times(names, lap_times, best_names, best_times)

        if save == "y":
            if len(all_names) != 0:
                all_results = np.vstack((all_results, lap_times))
                all_names = all_names + names
                save_results(tournament, gender, length, all_names, all_results.T)
            else:
                all_results = lap_times
                all_names = names
                save_results(tournament, gender, length, all_names, all_results.T)

        correct = False
        while not correct:
            next_race = input("Do you want to start tracking the next race? [y/n]: ")
            if not (next_race == "y" or next_race == "n"):
                print("ERROR: please select a valid response!")
            else:
                correct = True

        if next_race == "n":
            create_race_view(
                gender,
                names,
                lap_times,
                nr_laps,
                best_names,
                best_times,
                race_layout,
                final=True
            )
            print(race_layout)
            input("Input anything to quit the Tracker!")
            tracking = False

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="CLI tool to track and predict Speed Skating races"
    )

    parser.add_argument('--tournament', '-t', type=str, required=True,
                        help="The name of the tournament where the race is taking place. "
                             "Will be used in the saved file.")
    parser.add_argument('--gender', '-g', type=str, choices=["M", "F"], required=True,
                        help="Indicate if the race is for the Men (M) or the Women (W).")
    parser.add_argument('--length', '-l', type=int, choices=[500, 1000, 1500, 3000, 5000, 10000], required=True,
                        help="Indicate the length of the race.")
    parser.add_argument("--save", "-s", choices=["y", "n"], type=str, default="y",
                        help="Indicate if all the results should be saved.")
    # TODO: implement these arguments
    parser.add_argument('--prediction_method', '-pm', nargs="+", type=str,
                        choices=["mean", "latest", "lr", "LSTM", "online"],
                        help="Indicate which method to use to predict the ending time.")
    parser.add_argument("--accumulate", "-a", choices=["y", "n"], type=str, default="y",
                        help="Indicate if previous results should be accumulated in the visualisations.")
    # For now this will be a simple csv, might change into something like an sqlite db

    args = parser.parse_args()
    kwargs = vars(args)

    main_tracking(**kwargs)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
