import pandas as pd
import pytest

import forecast.data.date_featurizers as feat


@pytest.mark.parametrize('cls,dates', [
    (
        feat.SecondOfMinuteFeaturizer,
        pd.date_range(start='1/1/2019', end='1/2/2019', freq='S')
    ),
    (
        feat.MinuteOfHourFeaturizer,
        pd.date_range(start='1/1/2019', end='1/2/2019', freq='T')
    ),
    (
        feat.HourOfDayFeaturizer,
        pd.date_range(start='1/1/2019', end='1/2/2019', freq='H')
    ),
    # for day+ featurizers, include 2019 (non leap year) and 2020 (leap year)
    (
        feat.DayOfWeekFeaturizer,
        pd.date_range(start='1/1/2019', end='1/1/2021', freq='D')
    ),
    (
        feat.DayOfMonthFeaturizer,
        pd.date_range(start='1/1/2019', end='1/1/2021', freq='D')
    ),
    (
        feat.DayOfYearFeaturizer,
        pd.date_range(start='1/1/2019', end='1/1/2021', freq='D')
    ),
    # Not every year has 53 weeks, expand the range to include one
    (
        feat.WeekOfYearFeaturizer,
        pd.date_range(start='1/1/2019', end='1/1/2022', freq='W')
    ),
    (
        feat.MonthOfYearFeaturizer,
        pd.date_range(start='1/1/2019', end='1/1/2020', freq='M')
    ),
    (
        feat.HolidayFeaturizer,
        pd.date_range(start='1/1/2019', end='1/1/2021', freq='D')
    )])
def test_range(cls, dates):
    featurizer = cls()
    featurized = featurizer(dates)

    assert featurized.min() == 0
    assert featurized.max() == featurizer.num_values - 1

    if featurizer.num_values > 2:
        normalized = feat.NormalizedFeaturizer(featurizer)
        floats = normalized(dates)

        assert floats.min() >= -1
        assert floats.max() <= 1


def test_name_unique():
    featurizers = [
        feat.SecondOfMinuteFeaturizer,
        feat.MinuteOfHourFeaturizer,
        feat.HourOfDayFeaturizer,
        feat.DayOfWeekFeaturizer,
        feat.DayOfMonthFeaturizer,
        feat.DayOfYearFeaturizer,
        feat.WeekOfYearFeaturizer,
        feat.MonthOfYearFeaturizer
    ]
    inst_feat = [f() for f in featurizers]
    inst_feat += [feat.NormalizedFeaturizer(f()) for f in featurizers]
    inst_feat.append(feat.HolidayFeaturizer())
    names = [f.name for f in inst_feat]
    assert len(names) == len(set(names)) == len(featurizers) * 2 + 1
