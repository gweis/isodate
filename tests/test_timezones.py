"""Formatting must follow datetime's protocol for time-only zone offsets."""

from datetime import datetime, time, timedelta, timezone, tzinfo

import pytest

from isodate import UTC, datetime_isoformat, parse_time, time_isoformat
from isodate.isotzinfo import tz_isoformat


@pytest.mark.parametrize(
    "offset, suffixes",
    [
        (timedelta(hours=5, minutes=30), ("+05:30", "+0530", "+05")),
        (timedelta(hours=-3, minutes=-30), ("-03:30", "-0330", "-03")),
        (timedelta(0), ("+00:00", "+0000", "+00")),
    ],
)
@pytest.mark.parametrize("index, directive", enumerate(("%Z", "%z", "%h")))
def test_standard_library_timezones(offset, suffixes, index, directive):
    value = time(12, 34, 56, tzinfo=timezone(offset))
    expected = "12:34:56" + suffixes[index]
    assert tz_isoformat(value, directive) == suffixes[index]
    assert time_isoformat(value, "%H:%M:%S" + directive) == expected
    if directive != "%h" or offset == timedelta(0):
        assert parse_time(expected) == value


class DateDependentZone(tzinfo):
    """A time alone has no offset; a datetime has a date-dependent offset."""

    def utcoffset(self, value):
        if value is None:
            return None
        assert isinstance(value, datetime)
        return timedelta(hours=value.month)

    def dst(self, value):
        return timedelta(0)


def test_date_dependent_timezone():
    zone = DateDependentZone()
    assert time_isoformat(time(12, tzinfo=zone)) == "12:00:00"
    assert datetime_isoformat(datetime(2026, 2, 1, 12, tzinfo=zone)) == (
        "2026-02-01T12:00:00+02:00"
    )


@pytest.mark.parametrize("zone, suffix", [(None, ""), (UTC, "Z")])
def test_existing_timezones(zone, suffix):
    assert time_isoformat(time(12, tzinfo=zone)) == "12:00:00" + suffix
