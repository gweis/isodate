"""Formatting complete weeks should be symmetric around zero."""

from datetime import timedelta

import pytest

from isodate import D_WEEK, Duration, duration_isoformat, strftime


@pytest.mark.parametrize("days", [1, 6, 7, 8, 13, 14, 15])
@pytest.mark.parametrize("use_duration", [False, True])
def test_negative_weeks_match_the_positive_magnitude(days, use_duration):
    positive = Duration(days=days) if use_duration else timedelta(days=days)
    expected = days // 7
    assert duration_isoformat(positive, D_WEEK) == f"P{expected}W"
    assert duration_isoformat(-positive, D_WEEK) == f"-P{expected}W"
    assert strftime(-positive, "%W") == f"{expected:02d}"


@pytest.mark.parametrize("use_duration", [False, True])
def test_fractional_day_does_not_complete_a_negative_week(use_duration):
    duration = timedelta(days=-7, microseconds=1)
    if use_duration:
        duration = Duration(days=-7, microseconds=1)
    assert duration_isoformat(duration, D_WEEK) == "-P0W"
    assert strftime(duration, "%W") == "00"


def test_zero_and_exact_negative_week():
    assert duration_isoformat(timedelta(0), D_WEEK) == "P0W"
    assert duration_isoformat(timedelta(weeks=-1), D_WEEK) == "-P1W"
