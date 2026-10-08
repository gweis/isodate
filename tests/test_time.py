"""Test cases for the isotime module."""

from datetime import time
from threading import Event, Thread, current_thread
from types import SimpleNamespace
from typing import Optional

import pytest

from isodate import (
    TIME_BAS_COMPLETE,
    TIME_BAS_MINUTE,
    TIME_EXT_COMPLETE,
    TIME_EXT_MINUTE,
    TIME_HOUR,
    TZ_BAS,
    TZ_EXT,
    TZ_HOUR,
    UTC,
    FixedOffset,
    ISO8601Error,
    isotime,
    parse_datetime,
    parse_time,
    time_isoformat,
)

# the following list contains tuples of ISO time strings and the expected
# result from the parse_time method. A result of None means an ISO8601Error
# is expected.
TEST_CASES: list[tuple[str, Optional[time], Optional[str]]] = [
    ("232050", time(23, 20, 50), TIME_BAS_COMPLETE + TZ_BAS),
    ("23:20:50", time(23, 20, 50), TIME_EXT_COMPLETE + TZ_EXT),
    ("2320", time(23, 20), TIME_BAS_MINUTE),
    ("23:20", time(23, 20), TIME_EXT_MINUTE),
    ("23", time(23), TIME_HOUR),
    ("232050,5", time(23, 20, 50, 500000), None),
    ("23:20:50.5", time(23, 20, 50, 500000), None),
    # test precision
    ("15:33:42.123456", time(15, 33, 42, 123456), None),
    ("15:33:42.1234564", time(15, 33, 42, 123456), None),
    ("15:33:42.1234557", time(15, 33, 42, 123455), None),
    (
        "10:59:59.9999999Z",
        time(10, 59, 59, 999999, tzinfo=UTC),
        None,
    ),  # TIME_EXT_COMPLETE + TZ_EXT),
    ("2320,8", time(23, 20, 48), None),
    ("23:20,8", time(23, 20, 48), None),
    ("23,3", time(23, 18), None),
    ("232030Z", time(23, 20, 30, tzinfo=UTC), TIME_BAS_COMPLETE + TZ_BAS),
    ("2320Z", time(23, 20, tzinfo=UTC), TIME_BAS_MINUTE + TZ_BAS),
    ("23Z", time(23, tzinfo=UTC), TIME_HOUR + TZ_BAS),
    ("23:20:30Z", time(23, 20, 30, tzinfo=UTC), TIME_EXT_COMPLETE + TZ_EXT),
    ("23:20Z", time(23, 20, tzinfo=UTC), TIME_EXT_MINUTE + TZ_EXT),
    (
        "152746+0100",
        time(15, 27, 46, tzinfo=FixedOffset(1, 0, "+0100")),
        TIME_BAS_COMPLETE + TZ_BAS,
    ),
    (
        "152746-0500",
        time(15, 27, 46, tzinfo=FixedOffset(-5, 0, "-0500")),
        TIME_BAS_COMPLETE + TZ_BAS,
    ),
    (
        "152746+01",
        time(15, 27, 46, tzinfo=FixedOffset(1, 0, "+01:00")),
        TIME_BAS_COMPLETE + TZ_HOUR,
    ),
    (
        "152746-05",
        time(15, 27, 46, tzinfo=FixedOffset(-5, -0, "-05:00")),
        TIME_BAS_COMPLETE + TZ_HOUR,
    ),
    (
        "15:27:46+01:00",
        time(15, 27, 46, tzinfo=FixedOffset(1, 0, "+01:00")),
        TIME_EXT_COMPLETE + TZ_EXT,
    ),
    (
        "15:27:46-05:00",
        time(15, 27, 46, tzinfo=FixedOffset(-5, -0, "-05:00")),
        TIME_EXT_COMPLETE + TZ_EXT,
    ),
    (
        "15:27:46+01",
        time(15, 27, 46, tzinfo=FixedOffset(1, 0, "+01:00")),
        TIME_EXT_COMPLETE + TZ_HOUR,
    ),
    (
        "15:27:46-05",
        time(15, 27, 46, tzinfo=FixedOffset(-5, -0, "-05:00")),
        TIME_EXT_COMPLETE + TZ_HOUR,
    ),
    (
        "15:27:46-05:30",
        time(15, 27, 46, tzinfo=FixedOffset(-5, -30, "-05:30")),
        TIME_EXT_COMPLETE + TZ_EXT,
    ),
    (
        "15:27:46-0545",
        time(15, 27, 46, tzinfo=FixedOffset(-5, -45, "-0545")),
        TIME_EXT_COMPLETE + TZ_BAS,
    ),
    ("1:17:30", None, TIME_EXT_COMPLETE),
]


@pytest.mark.parametrize("timestring, expectation, format", TEST_CASES)
def test_parse(timestring: str, expectation: Optional[time], format: Optional[str]):
    """Parse an ISO time string and compare it to the expected value."""
    if expectation is None:
        with pytest.raises(ISO8601Error):
            parse_time(timestring)
    else:
        assert parse_time(timestring) == expectation


@pytest.mark.parametrize("timestring, expectation, format", TEST_CASES)
def test_format(timestring: str, expectation: Optional[time], format: Optional[str]):
    """Take time object and create ISO string from it.

    This is the reverse test to test_parse.
    """
    if expectation is None:
        with pytest.raises(AttributeError):
            time_isoformat(expectation, format)  # type: ignore [arg-type]
    elif format is not None:
        assert time_isoformat(expectation, format) == timestring


@pytest.mark.parametrize("parser, prefix", [(parse_time, ""), (parse_datetime, "2024-10-09T")])
def test_concurrent_first_parse(parser, prefix, monkeypatch):
    monkeypatch.setattr(isotime, "TIME_REGEX_CACHE", [])
    compiling = Event()
    resume = Event()
    compile_pattern = isotime.re.compile
    compilation_calls = 0
    first_results = []

    def paused_compile(pattern):
        nonlocal compilation_calls
        if current_thread() is worker:
            compilation_calls += 1
            if compilation_calls == 2:
                compiling.set()
                assert resume.wait(5)
        return compile_pattern(pattern)

    def first_parse():
        try:
            first_results.append(parser(prefix + "12:34:56+02:00").isoformat())
        except Exception as error:
            first_results.append(error)

    worker = Thread(target=first_parse)
    monkeypatch.setattr(isotime, "re", SimpleNamespace(compile=paused_compile))
    worker.start()
    try:
        assert compiling.wait(5)
        # This reduced format needs a pattern not yet compiled by the first thread.
        result = parser(prefix + "12:34+02:00")
    finally:
        resume.set()
        worker.join(5)
        assert not worker.is_alive()
    assert result.isoformat() == prefix + "12:34:00+02:00"
    assert first_results == [prefix + "12:34:56+02:00"]


def test_warm_cache_does_not_compile(monkeypatch):
    monkeypatch.setattr(isotime, "TIME_REGEX_CACHE", [])
    assert parse_time("12:34:56") == time(12, 34, 56)

    def unexpected_compile(pattern):
        pytest.fail("An initialized time parser should reuse its compiled patterns")

    monkeypatch.setattr(isotime, "re", SimpleNamespace(compile=unexpected_compile))
    assert parse_time("12:34") == time(12, 34)
    assert parse_time("12") == time(12)
