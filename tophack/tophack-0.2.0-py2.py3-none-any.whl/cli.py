"""Console script for top_hack."""
import argparse
import sys
import webbrowser
from .top_hack import TopHack


def main():
    """Console script for top_hack."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-ms",
        "--min-score",
        metavar="N",
        type=int,
        default=100,
        help="Minimum score to fetch.",
    )
    parser.add_argument(
        "-n",
        "--amount",
        metavar="N",
        type=int,
        default=10,
        help="Amount of results to fetch.",
    )
    parser.add_argument(
        "-s",
        "--sleep",
        metavar="S",
        default=3,
        help="Number of seconds to sleep between requests.",
    )
    args = parser.parse_args()

    app = TopHack(args.amount, args.min_score, args.sleep)
    results = app.run()

    presentation = ""

    for idx, result in enumerate(results):
        presentation += f"[{idx}] {result['title']} ({result['score']})\n"

    print(presentation)

    while True:
        try:
            chosen = input("Which number? q to quit. ")

            if chosen == "q":
                break
            else:
                chosen = int(chosen)
        except Exception:
            continue
        action = input("Action: [o/c/q] ")

        if action == "o":
            url = results[chosen]["url"]
            if not url.startswith("http"):
                url = results[chosen]["comment_url"]
        elif action == "c":
            url = results[chosen]["comment_url"]
        else:
            continue
        webbrowser.open(url, new=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
