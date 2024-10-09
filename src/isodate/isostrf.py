"""This module provides an alternative strftime method.

The strftime method in this module allows only a subset of Python's strftime
format codes, plus a few additional. It supports the full range of date values
possible with standard Python date/time objects. Furthermore there are several
pr-defined format strings in this module to make ease producing of ISO 8601
conforming strings.
"""

import re
from datetime import date, time, timedelta
from typing import Callable, Union

from isodate.duration import Duration
from isodate.isotzinfo import tz_isoformat

# Date specific format strings
DATE_BAS_COMPLETE = "%Y%m%d"
DATE_EXT_COMPLETE = "%Y-%m-%d"
DATE_BAS_WEEK_COMPLETE = "%YW%W%w"
DATE_EXT_WEEK_COMPLETE = "%Y-W%W-%w"
DATE_BAS_ORD_COMPLETE = "%Y%j"
DATE_EXT_ORD_COMPLETE = "%Y-%j"
DATE_BAS_WEEK = "%YW%W"
DATE_EXT_WEEK = "%Y-W%W"
DATE_BAS_MONTH = "%Y%m"
DATE_EXT_MONTH = "%Y-%m"
DATE_YEAR = "%Y"
DATE_CENTURY = "%C"

# Time specific format strings
TIME_BAS_COMPLETE = "%H%M%S"
TIME_EXT_COMPLETE = "%H:%M:%S"
TIME_BAS_MINUTE = "%H%M"
TIME_EXT_MINUTE = "%H:%M"
TIME_HOUR = "%H"

# Time zone formats
TZ_BAS = "%z"
TZ_EXT = "%Z"
TZ_HOUR = "%h"

# DateTime formats
DT_EXT_COMPLETE = DATE_EXT_COMPLETE + "T" + TIME_EXT_COMPLETE + TZ_EXT
DT_BAS_COMPLETE = DATE_BAS_COMPLETE + "T" + TIME_BAS_COMPLETE + TZ_BAS
DT_EXT_ORD_COMPLETE = DATE_EXT_ORD_COMPLETE + "T" + TIME_EXT_COMPLETE + TZ_EXT
DT_BAS_ORD_COMPLETE = DATE_BAS_ORD_COMPLETE + "T" + TIME_BAS_COMPLETE + TZ_BAS
DT_EXT_WEEK_COMPLETE = DATE_EXT_WEEK_COMPLETE + "T" + TIME_EXT_COMPLETE + TZ_EXT
DT_BAS_WEEK_COMPLETE = DATE_BAS_WEEK_COMPLETE + "T" + TIME_BAS_COMPLETE + TZ_BAS

# Duration formts
D_DEFAULT = "P%P"
D_WEEK = "P%p"
D_ALT_EXT = "P" + DATE_EXT_COMPLETE + "T" + TIME_EXT_COMPLETE
D_ALT_BAS = "P" + DATE_BAS_COMPLETE + "T" + TIME_BAS_COMPLETE
D_ALT_EXT_ORD = "P" + DATE_EXT_ORD_COMPLETE + "T" + TIME_EXT_COMPLETE
D_ALT_BAS_ORD = "P" + DATE_BAS_ORD_COMPLETE + "T" + TIME_BAS_COMPLETE

STRF_DT_MAP: dict[str, Callable[[Union[time, date], int], str]] = {
    "%d": lambda tdt, yds: "%02d" % tdt.day,  # type: ignore [union-attr]
    "%f": lambda tdt, yds: "%06d" % tdt.microsecond,  # type: ignore [union-attr]
    "%H": lambda tdt, yds: "%02d" % tdt.hour,  # type: ignore [union-attr]
    "%j": lambda tdt, yds: "%03d" % (tdt.toordinal() - date(tdt.year, 1, 1).toordinal() + 1),  # type: ignore [union-attr, operator] # noqa: E501
    "%m": lambda tdt, yds: "%02d" % tdt.month,  # type: ignore [union-attr]
    "%M": lambda tdt, yds: "%02d" % tdt.minute,  # type: ignore [union-attr]
    "%S": lambda tdt, yds: "%02d" % tdt.second,  # type: ignore [union-attr]
    "%w": lambda tdt, yds: "%1d" % tdt.isoweekday(),  # type: ignore [union-attr]
    "%W": lambda tdt, yds: "%02d" % tdt.isocalendar()[1],  # type: ignore [union-attr]
    "%Y": lambda tdt, yds: (((yds != 4) and "+") or "") + (("%%0%dd" % yds) % tdt.year),  # type: ignore [union-attr] # noqa: E501
    "%C": lambda tdt, yds: (((yds != 4) and "+") or "")  # type: ignore [union-attr]
    + (("%%0%dd" % (yds - 2)) % (tdt.year / 100)),  # type: ignore [union-attr]
    "%h": lambda tdt, yds: tz_isoformat(tdt, "%h"),  # type: ignore [arg-type]
    "%Z": lambda tdt, yds: tz_isoformat(tdt, "%Z"),  # type: ignore [arg-type]
    "%z": lambda tdt, yds: tz_isoformat(tdt, "%z"),  # type: ignore [arg-type]
    "%%": lambda tdt, yds: "%",
}

STRF_D_MAP: dict[str, Callable[[Union[timedelta, Duration], int], str]] = {
    "%d": lambda tdt, yds: "%02d" % tdt.days,
    "%f": lambda tdt, yds: "%06d" % tdt.microseconds,
    "%H": lambda tdt, yds: "%02d" % (tdt.seconds / 60 / 60),
    "%m": lambda tdt, yds: "%02d" % tdt.months,  # type: ignore [union-attr]
    "%M": lambda tdt, yds: "%02d" % ((tdt.seconds / 60) % 60),
    "%S": lambda tdt, yds: "%02d" % (tdt.seconds % 60),
    "%W": lambda tdt, yds: "%02d" % (abs(tdt.days / 7)),
    "%Y": lambda tdt, yds: (((yds != 4) and "+") or "") + (("%%0%dd" % yds) % tdt.years),  # type: ignore [union-attr] # noqa: E501
    "%C": lambda tdt, yds: (((yds != 4) and "+") or "")
    + (("%%0%dd" % (yds - 2)) % (tdt.years / 100)),  # type: ignore [union-attr]
    "%%": lambda tdt, yds: "%",
}


def _strfduration(tdt: Union[timedelta, Duration], format: str, yeardigits: int = 4) -> str:
    """This is the work method for timedelta and Duration instances.

    See strftime for more details.
    """

    def repl(match: re.Match[str]) -> str:
        """Lookup format command and return corresponding replacement."""
        if match.group(0) in STRF_D_MAP:
            return STRF_D_MAP[match.group(0)](tdt, yeardigits)
        elif match.group(0) == "%P":
            ret: list[str] = []
            if isinstance(tdt, Duration):
                if tdt.years:
                    ret.append("%sY" % abs(tdt.years))
                if tdt.months:
                    ret.append("%sM" % abs(tdt.months))
            usecs = abs((tdt.days * 24 * 60 * 60 + tdt.seconds) * 1000000 + tdt.microseconds)
            seconds, usecs = divmod(usecs, 1000000)
            minutes, seconds = divmod(seconds, 60)
            hours, minutes = divmod(minutes, 60)
            days, hours = divmod(hours, 24)
            if days:
                ret.append("%sD" % days)
            if hours or minutes or seconds or usecs:
                ret.append("T")
                if hours:
                    ret.append("%sH" % hours)
                if minutes:
                    ret.append("%sM" % minutes)
                if seconds or usecs:
                    if usecs:
                        ret.append(("%d.%06d" % (seconds, usecs)).rstrip("0"))
                    else:
                        ret.append("%d" % seconds)
                    ret.append("S")
            # at least one component has to be there.
            return "".join(ret) if ret else "0D"
        elif match.group(0) == "%p":
            return str(abs(tdt.days // 7)) + "W"
        return match.group(0)

    return re.sub("%d|%f|%H|%m|%M|%S|%W|%Y|%C|%%|%P|%p", repl, format)


def _strfdt(tdt: Union[time, date], format: str, yeardigits: int = 4) -> str:
    """This is the work method for time and date instances.

    See strftime for more details.
    """

    def repl(match: re.Match[str]) -> str:
        """Lookup format command and return corresponding replacement."""
        if match.group(0) in STRF_DT_MAP:
            return STRF_DT_MAP[match.group(0)](tdt, yeardigits)
        return match.group(0)

    return re.sub("%d|%f|%H|%j|%m|%M|%S|%w|%W|%Y|%C|%z|%Z|%h|%%", repl, format)


def strftime(tdt: Union[timedelta, Duration, time, date], format: str, yeardigits: int = 4) -> str:
    """Directive Meaning Notes.

    %d    Day of the month as a decimal number [01,31].
    %f    Microsecond as a decimal number [0,999999], zero-padded
          on the left (1)
    %H    Hour (24-hour clock) as a decimal number [00,23].
    %j    Day of the year as a decimal number [001,366].
    %m    Month as a decimal number [01,12].
    %M    Minute as a decimal number [00,59].
    %S    Second as a decimal number [00,61].    (3)
    %w    Weekday as a decimal number [0(Monday),6].
    %W    Week number of the year (Monday as the first day of the week)
          as a decimal number [00,53]. All days in a new year preceding the
          first Monday are considered to be in week 0.  (4)
    %Y    Year with century as a decimal number. [0000,9999]
    %C    Century as a decimal number. [00,99]
    %z    UTC offset in the form +HHMM or -HHMM (empty string if the
          object is naive).    (5)
    %Z    Time zone name (empty string if the object is naive).
    %P    ISO8601 duration format.
    %p    ISO8601 duration format in weeks.
    %%    A literal '%' character.

    """
    if isinstance(tdt, (timedelta, Duration)):
        return _strfduration(tdt, format, yeardigits)
    return _strfdt(tdt, format, yeardigits)
