"""This module provides some datetime.tzinfo implementations.

All those classes are taken from the Python documentation.
"""

import time
from datetime import datetime, timedelta, tzinfo
from typing import Literal, Optional

ZERO = timedelta(0)
# constant for zero time offset.


class Utc(tzinfo):
    """UTC

    Universal time coordinated time zone.
    """

    def utcoffset(self, dt: Optional[datetime]) -> timedelta:
        """Return offset from UTC in minutes east of UTC, which is ZERO for UTC."""
        return ZERO

    def tzname(self, dt: Optional[datetime]) -> Literal["UTC"]:
        """Return the time zone name corresponding to the datetime object dt,
        as a string.
        """
        return "UTC"

    def dst(self, dt: Optional[datetime]) -> timedelta:
        """Return the daylight saving time (DST) adjustment, in minutes east
        of UTC.
        """
        return ZERO

    def __reduce__(self):
        """When unpickling a Utc object, return the default instance below, UTC."""
        return _Utc, ()


UTC = Utc()
# the default instance for UTC.


def _Utc() -> Utc:
    """Helper function for unpickling a Utc object."""
    return UTC


class FixedOffset(tzinfo):
    """A class building tzinfo objects for fixed-offset time zones.

    Note that FixedOffset(0, 0, "UTC") or FixedOffset() is a different way to
    build a UTC tzinfo object.
    """

    def __init__(
        self, offset_hours: float = 0, offset_minutes: float = 0, name: str = "UTC"
    ) -> None:
        """Initialise an instance with time offset and name.

        The time offset should be positive for time zones east of UTC
        and negate for time zones west of UTC.
        """
        self.__offset = timedelta(hours=offset_hours, minutes=offset_minutes)
        self.__name = name

    def utcoffset(self, dt: Optional[datetime]) -> timedelta:
        """Return offset from UTC in minutes of UTC."""
        return self.__offset

    def tzname(self, dt: Optional[datetime]) -> str:
        """Return the time zone name corresponding to the datetime object dt, as a
        string.
        """
        return self.__name

    def dst(self, dt: Optional[datetime]) -> timedelta:
        """Return the daylight saving time (DST) adjustment, in minutes east of
        UTC.
        """
        return ZERO

    def __repr__(self) -> str:
        """Return nicely formatted repr string."""
        return "<FixedOffset %r>" % self.__name


STDOFFSET = timedelta(seconds=-time.timezone)
# locale time zone offset

# calculate local daylight saving offset if any.
DSTOFFSET = timedelta(seconds=-time.altzone) if time.daylight else STDOFFSET

DSTDIFF = DSTOFFSET - STDOFFSET
# difference between local time zone and local DST time zone


class LocalTimezone(tzinfo):
    """A class capturing the platform's idea of local time."""

    def utcoffset(self, dt: Optional[datetime]) -> timedelta:
        """Return offset from UTC in minutes of UTC."""
        if self._isdst(dt):
            return DSTOFFSET
        else:
            return STDOFFSET

    def dst(self, dt: Optional[datetime]) -> timedelta:
        """Return daylight saving offset."""
        if self._isdst(dt):
            return DSTDIFF
        else:
            return ZERO

    def tzname(self, dt: Optional[datetime]) -> str:
        """Return the time zone name corresponding to the datetime object dt, as a
        string.
        """
        return time.tzname[self._isdst(dt)]

    def _isdst(self, dt: Optional[datetime]) -> bool:
        """Returns true if DST is active for given datetime object dt."""
        if dt is None:
            raise Exception("datetime object dt was None!")
        tt = (
            dt.year,
            dt.month,
            dt.day,
            dt.hour,
            dt.minute,
            dt.second,
            dt.weekday(),
            0,
            -1,
        )
        stamp = time.mktime(tt)
        tt = time.localtime(stamp)
        return tt.tm_isdst > 0


# the default instance for local time zone.
LOCAL = LocalTimezone()
