from argparse import ArgumentParser, Namespace

import pandas as pd
from pandas import DataFrame, Series


def get_args() -> Namespace:
    ap: ArgumentParser = ArgumentParser(
        prog="SSL Metrics Git Productivity Computer",
        usage="Calculates productivity metric of a git project.",
        description="Productivity is defined as |ΔLOC| / (Team Effort) where Team Effort is the total elapsed time between commits.",
    )
    ap.add_argument(
        "-i",
        "--input",
        required=True,
        type=str,
        help="JSON file containing data formatted by ssl-metrics-git-commits-loc-extract",
    )
    ap.add_argument(
        "-o",
        "--output",
        required=True,
        type=str,
        help="JSON file containing data outputted by the application",
    )
    args: Namespace = ap.parse_args()
    return args


def get_prod(df: DataFrame) -> DataFrame:
    divedend: int = df["days_since_0"].max()
    daysSince0: Series = df["days_since_0"].unique()

    data: list = []

    day: int
    for day in range(daysSince0.max() + 1):
        temp: dict = {}

        productivity: float = (
            df[df["days_since_0"] == day]["delta_loc"].abs().sum() / divedend
        )

        temp["days_since_0"] = day
        temp["productivity"] = productivity

        data.append(temp)

    return DataFrame(data)


def main():
    args = get_args()

    if args.input[-5::] != ".json":
        print("Input must be a .json file")
        quit(1)

    dfIn: DataFrame = pd.read_json(args.input)
    dfOut: DataFrame = get_prod(df=dfIn)

    dfOut.to_json(args.output)


if __name__ == "__main__":
    main()
