import itertools


def exponential(base=2):
    return (pow(base, i) for i in itertools.count())  # pragma: no branch


def batched(gen, size):
    gen = iter(gen)
    while True:
        batch = list(itertools.islice(gen, size))
        if not batch:
            break
        yield batch
