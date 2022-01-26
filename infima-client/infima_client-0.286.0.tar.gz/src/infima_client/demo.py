import pprint
from textwrap import dedent, indent
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from infima_client.client import InfimaClient


def demo(client: "InfimaClient") -> None:  # 5,2021
    """
    Demo for pool and cohort predictions and realization functions
    """

    # def headline(msg: str) -> None:
    #     n = ((60 - len(msg)) // 2) - 2
    #     pre = post = " " + "=" * n + " "
    #     print("\n" + pre + msg + post + "\n")

    def headline(msg: str) -> None:
        n = (80 - len(msg)) // 2
        pre = post = "=" * 80
        print(pre)
        print(" " * n + msg)
        print(post)
        print()

    def statement(msg: str) -> None:
        pre = ">>> "
        print(pre + dedent(msg).strip())

    def assignment(name: str, vals: Any) -> None:
        statement(f"{name} = {pprint.pformat(vals)}")

    def output(msg: str) -> None:
        print("\n" + indent(msg, "    ") + "\n")

    as_of = "2021-10-28"
    pools = ["3133AE2D5", "3133AE2K9", "3133AE2U7", "3133AE3J1", "3133AE3S1"]
    cohorts = [
        "FNCL 1.5 2021",
        "FNCL 2.0 2021",
        "FNCL 2.5 2021",
        "FNCL 3.0 2021",
        "FNCL 3.5 2021",
    ]
    symbols = pools + cohorts

    headline("Demo of InfimaClient usage")
    assignment("pools", pools)
    assignment("cohorts", cohorts)
    assignment("symbols", symbols)

    # Get Latest Predictions on Symbols
    headline("Get Latest Predictions on Symbols")
    df = client.get_predictions(symbols=symbols)
    statement("df = client.get_predictions(symbols=symbols)")
    output(df.to_string(max_cols=6) if df is not None else "None")

    # Get As-Of Predictions on Symbols
    headline("Get As-Of Predictions on Symbols")
    assignment("as_of", as_of)
    df = client.get_predictions(symbols=symbols, as_of=as_of)
    statement("df = client.get_predictions(symbols=symbols, as_of=as_of)")
    output(df.to_string(max_cols=6) if df is not None else "None")

    # Get 3 Months Ahead Predictions on Symbols
    headline("Get 3 Months Ahead Predictions on Symbols")
    df = client.get_n_months_ahead_predictions(symbols=symbols, num_months=3)
    statement(
        "df = client.get_n_months_ahead_predictions(symbols=symbols, num_months=3)"
    )
    output(df.to_string(max_cols=6) if df is not None else "None")

    start = "2021-03-01"
    # Get 3 Months Ahead Predictions on Symbols From START DATE
    headline(f"Get 3 Months Ahead Predictions on Symbols From {start}")
    assignment("start", start)
    df = client.get_n_months_ahead_predictions(
        symbols=symbols, num_months=3, start=start
    )
    statement(
        """
    df = client.get_n_months_ahead_predictions(
        symbols=symbols,
        num_months=3,
        start=start,
    )
    """
    )
    output(df.to_string(max_cols=6) if df is not None else "None")

    end = "2021-09-01"
    # Get 3 Months Ahead Predictions on Symbols Prior to END DATE
    headline(f"Get 3 Months Ahead Predictions on Symbols Prior to {end}")
    assignment("end", end)
    df = client.get_n_months_ahead_predictions(symbols=symbols, num_months=3, end=end)
    statement(
        """
    df = client.get_n_months_ahead_predictions(
        symbols=symbols,
        num_months=3,
        end=end,
    )
    """
    )
    output(df.to_string(max_cols=6) if df is not None else "None")

    # Get 3 Months Ahead Predictions on Symbols From START DATE to END DATE
    headline(f"Get 3 Months Ahead Predictions on Symbols From {start} to {end}")
    df = client.get_n_months_ahead_predictions(
        symbols=symbols, num_months=3, start=start, end=end
    )
    statement(
        """
    df = client.get_n_months_ahead_predictions(
        symbols=symbols,
        num_months=3,
        start=start,
        end=end,
    )
    """
    )
    output(df.to_string(max_cols=6) if df is not None else "None")

    start = "2021-03-01"
    end = "2021-09-01"
    # Get Actual Prepaments on Symbols from START DATE to END DATE
    headline(f"Get Actual Prepaments on Symbols from {start} to {end}")
    assignment("start", start)
    assignment("end", end)
    df = client.get_actuals(symbols=symbols, start=start, end=end)
    statement("df = client.get_actuals(symbols=symbols, start=start, end=end)")
    output(df.to_string(max_cols=6) if df is not None else "None")
