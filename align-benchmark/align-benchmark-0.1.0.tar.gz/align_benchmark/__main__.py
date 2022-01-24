"""Bootstrap."""
from align_benchmark.benchmark import benchmark


def main():
    from icecream import ic

    res = round(benchmark(), 2)
    ic(benchmark.bench)
    ic("zip_longest:", benchmark.lst)
    ic(res)

    # ic(benchmark.mat[:10, :10])


if __name__ == "__main__":
    main()
