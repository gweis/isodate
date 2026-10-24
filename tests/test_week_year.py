"""ISO week dates must use the week year, not the calendar year."""

from datetime import date, datetime, timedelta, timezone

import pytest

from isodate import (
    DATE_BAS_WEEK,
    DATE_BAS_WEEK_COMPLETE,
    DATE_EXT_WEEK,
    DATE_EXT_WEEK_COMPLETE,
    DT_BAS_WEEK_COMPLETE,
    DT_EXT_WEEK_COMPLETE,
    Duration,
    date_isoformat,
    datetime_isoformat,
    parse_date,
    parse_datetime,
    strftime,
)


@pytest.mark.parametrize("value", [date(2019, 12, 30), date(2021, 1, 1), date(2020, 6, 15)])
@pytest.mark.parametrize("yeardigits", [4, 6])
@pytest.mark.parametrize(
    "format, extended, complete",
    [
        (DATE_BAS_WEEK, False, False),
        (DATE_EXT_WEEK, True, False),
        (DATE_BAS_WEEK_COMPLETE, False, True),
        (DATE_EXT_WEEK_COMPLETE, True, True),
    ],
)
def test_week_date_year(value, yeardigits, format, extended, complete):
    year, week, weekday = value.isocalendar()
    separator = "-" if extended else ""
    expected = ("+" if yeardigits != 4 else "") + f"{year:0{yeardigits}d}"
    expected += f"{separator}W{week:02d}"
    if complete:
        expected += f"{separator}{weekday}"
    result = date_isoformat(value, format, yeardigits)
    assert result == expected
    assert parse_date(result, yeardigits) == (
        value if complete else value - timedelta(days=weekday - 1)
    )


@pytest.mark.parametrize(
    "value", [datetime(2019, 12, 30, 12, 34, 56), datetime(2021, 1, 1, 12, 34, 56)]
)
@pytest.mark.parametrize(
    "format, separator", [(DT_BAS_WEEK_COMPLETE, ""), (DT_EXT_WEEK_COMPLETE, "-")]
)
def test_week_datetime_year(value, format, separator):
    year, week, weekday = value.isocalendar()
    date_text = f"{year:04d}{separator}W{week:02d}{separator}{weekday}"
    time_text = "12:34:56" if separator else "123456"
    result = datetime_isoformat(value, format)
    assert result == date_text + "T" + time_text
    assert parse_datetime(result) == value


@pytest.mark.parametrize("yeardigits", [4, 6])
def test_calendar_and_week_year_directives_are_independent(yeardigits):
    value = date(2019, 12, 30)
    prefix = "+" if yeardigits != 4 else ""
    assert strftime(value, "%Y|%G|%%G", yeardigits) == (
        f"{prefix}{2019:0{yeardigits}d}|{prefix}{2020:0{yeardigits}d}|%G"
    )
    assert date_isoformat(value) == "2019-12-30"


@pytest.mark.parametrize("offset", [-5, 0, 9])
def test_week_datetime_keeps_local_date_and_offset(offset):
    value = datetime(2019, 12, 30, 0, 15, tzinfo=timezone(timedelta(hours=offset)))
    result = datetime_isoformat(value, DT_EXT_WEEK_COMPLETE)
    assert result.startswith("2020-W01-1T00:15:00")
    assert parse_datetime(result) == value


@pytest.mark.parametrize("value", [timedelta(days=12), Duration(years=2, months=3)])
def test_duration_formatting_does_not_gain_a_week_year(value):
    assert strftime(value, "%G|%%G") == "%G|%G"
