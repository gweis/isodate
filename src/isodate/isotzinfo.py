"""This module provides an ISO 8601:2004 time zone info parser.

It offers a function to parse the time zone offset as specified by ISO 8601.
"""

import re
from datetime import datetime, tzinfo
from typing import Union

from isodate.isoerror import ISO8601Error
from isodate.tzinfo import UTC, ZERO, FixedOffset, Utc

TZ_REGEX = r"(?P<tzname>(Z|(?P<tzsign>[+-])" r"(?P<tzhour>[0-9]{2})(:?(?P<tzmin>[0-9]{2}))?)?)"

TZ_RE = re.compile(TZ_REGEX)


def build_tzinfo(
    tzname: Union[str, None], tzsign: str = "+", tzhour: float = 0, tzmin: float = 0
) -> Union[FixedOffset, Utc, None]:
    """
    create a tzinfo instance according to given parameters.

    tzname:
      'Z'       ... return UTC
      '' | None ... return None
      other     ... return FixedOffset
    """
    if tzname is None or tzname == "":
        return None
    if tzname == "Z":
        return UTC
    tzsignum = ((tzsign == "-") and -1) or 1
    return FixedOffset(tzsignum * tzhour, tzsignum * tzmin, tzname)


def parse_tzinfo(tzstring: str) -> Union[tzinfo, None]:
    """Parses ISO 8601 time zone designators to tzinfo objects.

    A time zone designator can be in the following format:
              no designator indicates local time zone
      Z       UTC
      +-hhmm  basic hours and minutes
      +-hh:mm extended hours and minutes
      +-hh    hours
    """
    match = TZ_RE.match(tzstring)
    if match:
        groups = match.groupdict()
        return build_tzinfo(
            groups["tzname"],
            groups["tzsign"],
            int(groups["tzhour"] or 0),
            int(groups["tzmin"] or 0),
        )
    raise ISO8601Error("%s not a valid time zone info" % tzstring)


def tz_isoformat(dt: datetime, format: str = "%Z") -> str:
    """Return time zone offset ISO 8601 formatted.

    The various ISO formats can be chosen with the format parameter.

    if tzinfo is None returns ''
    if tzinfo is UTC returns 'Z'
    else the offset is rendered to the given format.
    format:
        %h ... +-HH
        %z ... +-HHMM
        %Z ... +-HH:MM
    """
    tzinfo = dt.tzinfo
    if (tzinfo is None) or (tzinfo.utcoffset(dt) is None):
        return ""
    if tzinfo.utcoffset(dt) == ZERO and tzinfo.dst(dt) == ZERO:
        return "Z"
    tdelta = tzinfo.utcoffset(dt)
    if tdelta is None:
        return ""
    seconds = tdelta.days * 24 * 60 * 60 + tdelta.seconds
    sign = ((seconds < 0) and "-") or "+"
    seconds = abs(seconds)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours > 99:
        raise OverflowError("can not handle differences > 99 hours")
    if format == "%Z":
        return "%s%02d:%02d" % (sign, hours, minutes)
    elif format == "%z":
        return "%s%02d%02d" % (sign, hours, minutes)
    elif format == "%h":
        return "%s%02d" % (sign, hours)
    raise ValueError('unknown format string "%s"' % format)
