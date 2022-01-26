from argparse import ArgumentParser, Namespace

import pandas
from pandas import DataFrame, Series


def get_argparse() -> Namespace:
    parser: ArgumentParser = ArgumentParser(
        prog="SSL Metrics Bus Factor Computer",
        usage="Computes the bus factor per day",
        description="Computes the bus factor per day using the output of ssl-metrics-git-commit-loc-extract",
    )
    parser.add_argument(
        "-i",
        "--input",
        help="JSON file outputted from ssl-metrics-git-commits-loc-extract to be used to calculate bus factor",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-o",
        "--output",
        help="JSON file that will contain the bus factor metric information",
        type=str,
        required=True,
    )
    return parser.parse_args()


def buildBusFactor(df: DataFrame) -> DataFrame:
    daysSince0: Series = df["days_since_0"].unique()

    data: list = []

    day: int
    for day in range(daysSince0.max() + 1):
        temp: dict = {}

        busFactor: int = len(df[df["days_since_0"] == day]["author_email"].unique())

        temp["days_since_0"] = day
        temp["bus_factor"] = busFactor

        data.append(temp) 
    return DataFrame(data)


def main() -> None:
    args: Namespace = get_argparse()

    if args.input[-5::] != ".json":
        print("Invalid input file type. Input file must be JSON")
        quit(1)

    dfIn: DataFrame = pandas.read_json(args.input)
    dfOut: DataFrame = buildBusFactor(df=dfIn)

    dfOut.to_json(args.output)


if __name__ == "__main__":
    main()
