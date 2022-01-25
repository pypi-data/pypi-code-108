"""Bootstrap."""
from itertools import zip_longest
from textwrap import wrap
from icecream import ic

from align_benchmark.benchmark import benchmark
from align_benchmark.benchmark import bm2
from align_benchmark.benchmark import bm3


def main():
    """Create __main__."""
    # bm1

    res = round(benchmark(), 2)  # default to bm1

    indent = " " * 16
    print(" bm1 wh ch2 ".center(40))
    # print(benchmark.bench)
    # print("zip_longest:", benchmark.lst)
    print(
        "benchmark:".ljust(16),
        "\n".join(wrap(str(benchmark.bench), subsequent_indent=indent)),
    )
    print(
        "zip_longest:".ljust(16),
        "\n".join(wrap(str(benchmark.lst), subsequent_indent=indent)),
    )
    ic(res)

    # bm2
    left, right = bm2[-1]
    fillvalue = left if left < right else right
    lst = [
        *zip_longest(
            range(left + 1),
            range(right + 1),
            fillvalue=fillvalue,
        )
    ]

    res = round(benchmark(lst, bm2), 2)

    print(" bm2 wh ch1 ".center(40))
    print("benchmark:".ljust(16), "\n".join(wrap(str(bm2), subsequent_indent=indent)))
    print("zip_longest:".ljust(16), "\n".join(wrap(str(lst), subsequent_indent=indent)))
    ic(res)

    # bm3
    left, right = [*zip(*bm3)]
    left = [elm for elm in left if str(elm).strip()][-1]
    right = [elm for elm in right if str(elm).strip()][-1]

    try:
        int(left)
        int(right)
    except ValueError as exc:
        raise SystemExit(" Unable to continue... likely ill-formatted data.") from exc

    fillvalue = ""
    lst = [
        *zip_longest(
            range(left + 1),
            range(right + 1),
            fillvalue=fillvalue,
        )
    ]

    res = round(benchmark(lst, bm3), 2)

    print(" bm3 nyt-article ".center(40))
    print("benchmark:".ljust(16), "\n".join(wrap(str(bm3), subsequent_indent=indent)))
    print("zip_longest:".ljust(16), "\n".join(wrap(str(lst), subsequent_indent=indent)))
    ic(res)


if __name__ == "__main__":
    main()
