#!/usr/bin/env python3
import matplotlib.pyplot as plt
import matplotlib.ticker
import more_itertools
import pandas as pd
import seaborn as sns

# Evaluated on wordlist human with fraction 0.5
data = [
    {
        "name": "simple",
        "duration": 1.4197125434875488,
        "histogram": {"1": 1, "2": 93, "3": 517, "4": 585, "5": 240, "6": 58, "7": 6},
    },
    {
        "name": "cheap_heuristic",
        "duration": 1.223166,
        "histogram": {1: 1, 2: 101, 3: 600, 4: 594, 5: 178, 6: 23, 7: 3},
    },
    {
        "name": "max_entropy",
        "duration": 40.83522057533264,
        "histogram": {"2": 75, "3": 943, "4": 464, "5": 17, "6": 1},
    },
    {
        "name": "maximin_surprise",
        "duration": 42.123921394348145,
        "histogram": {"1": 1, "2": 73, "3": 803, "4": 597, "5": 26},
    },
]


def _expanded_data():
    for obj in data:
        # for num_guess in more_itertools.run_length.decode(obj["histogram"].items()):
        yield {
            "name": obj["name"],
            "duration": obj["duration"],
            # "num_guess": int(num_guess),
            "num_guess": sum(int(k) * v for k, v in obj["histogram"].items()),
        }


# TODO: Would be cool to show the histogram but getting them spaced properly along x is tricky.
#  It is also hard to tell them apart in y since they are tall relative to the difference in position.
def main():
    df = pd.DataFrame.from_dict(_expanded_data())
    print(df)
    sns.scatterplot(data=df, x="duration", y="num_guess", hue="name")
    plt.show()


if __name__ == "__main__":
    main()
