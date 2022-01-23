from freiner import limits


def test_seconds_value():
    assert limits.RateLimitItemPerSecond(1).get_expiry() == 1
    assert limits.RateLimitItemPerMinute(1).get_expiry() == 60
    assert limits.RateLimitItemPerHour(1).get_expiry() == 60 * 60
    assert limits.RateLimitItemPerDay(1).get_expiry() == 24 * 60 * 60
    assert limits.RateLimitItemPerMonth(1).get_expiry() == 30 * 24 * 60 * 60
    assert limits.RateLimitItemPerYear(1).get_expiry() == 12 * 30 * 24 * 60 * 60


def test_str_representation():
    assert str(limits.RateLimitItemPerSecond(1)) == "1 per 1 second"
    assert str(limits.RateLimitItemPerMinute(1)) == "1 per 1 minute"
    assert str(limits.RateLimitItemPerHour(1)) == "1 per 1 hour"
    assert str(limits.RateLimitItemPerDay(1)) == "1 per 1 day"
    assert str(limits.RateLimitItemPerMonth(1)) == "1 per 1 month"
    assert str(limits.RateLimitItemPerYear(1)) == "1 per 1 year"


def test_repr_representation():
    assert repr(limits.RateLimitItemPerSecond(2)) == "RateLimitItemPerSecond<2 per 1 second>"
    assert repr(limits.RateLimitItemPerMinute(3)) == "RateLimitItemPerMinute<3 per 1 minute>"
    assert repr(limits.RateLimitItemPerHour(4)) == "RateLimitItemPerHour<4 per 1 hour>"
    assert repr(limits.RateLimitItemPerDay(5)) == "RateLimitItemPerDay<5 per 1 day>"
    assert repr(limits.RateLimitItemPerMonth(6)) == "RateLimitItemPerMonth<6 per 1 month>"
    assert repr(limits.RateLimitItemPerYear(7)) == "RateLimitItemPerYear<7 per 1 year>"


def test_comparison():
    assert limits.RateLimitItemPerSecond(1) < limits.RateLimitItemPerMinute(1)
    assert limits.RateLimitItemPerMinute(1) < limits.RateLimitItemPerHour(1)
    assert limits.RateLimitItemPerHour(1) < limits.RateLimitItemPerDay(1)
    assert limits.RateLimitItemPerDay(1) < limits.RateLimitItemPerMonth(1)
    assert limits.RateLimitItemPerMonth(1) < limits.RateLimitItemPerYear(1)


def test_no_granularity():
    def _define_class() -> None:
        class NoGranularity(limits.RateLimitItem):
            pass

    known_granularities_before = list(limits.GRANULARITIES.keys())
    _define_class()
    known_granularities_after = list(limits.GRANULARITIES.keys())

    assert known_granularities_after == known_granularities_before
