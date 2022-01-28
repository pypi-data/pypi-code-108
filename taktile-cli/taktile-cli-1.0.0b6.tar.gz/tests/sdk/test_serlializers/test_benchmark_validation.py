import pandas as pd
import pytest

from tktl.future.registration.validation import validate


@pytest.mark.parametrize(
    "value,sample",
    [
        (
            pd.DataFrame(0, index=range(10000), columns=range(10000)),
            pd.DataFrame(0, index=range(10000), columns=range(10000)),
        )
    ],
)
def test_benchmark_validate(benchmark, value, sample):

    benchmark(validate, value, sample=sample)
