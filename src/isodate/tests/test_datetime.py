"""
Test cases for the isodatetime module.
"""
from __future__ import annotations

import unittest
from datetime import datetime
from unittest.suite import TestSuite

from isodate import (
    DATE_BAS_COMPLETE,
    DATE_BAS_ORD_COMPLETE,
    DATE_BAS_WEEK_COMPLETE,
    DATE_EXT_COMPLETE,
    DATE_EXT_ORD_COMPLETE,
    DATE_EXT_WEEK_COMPLETE,
    TIME_BAS_COMPLETE,
    TIME_BAS_MINUTE,
    TIME_EXT_COMPLETE,
    TIME_EXT_MINUTE,
    TZ_BAS,
    TZ_EXT,
    TZ_HOUR,
    UTC,
    FixedOffset,
    ISO8601Error,
    datetime_isoformat,
    parse_datetime,
)

# the following list contains tuples of ISO datetime strings and the expected
# result from the parse_datetime method. A result of None means an ISO8601Error
# is expected.
TEST_CASES = [
    (
        "19850412T1015",
        datetime(1985, 4, 12, 10, 15),
        DATE_BAS_COMPLETE + "T" + TIME_BAS_MINUTE,
        "19850412T1015",
    ),
    (
        "1985-04-12T10:15",
        datetime(1985, 4, 12, 10, 15),
        DATE_EXT_COMPLETE + "T" + TIME_EXT_MINUTE,
        "1985-04-12T10:15",
    ),
    (
        "1985102T1015Z",
        datetime(1985, 4, 12, 10, 15, tzinfo=UTC),
        DATE_BAS_ORD_COMPLETE + "T" + TIME_BAS_MINUTE + TZ_BAS,
        "1985102T1015Z",
    ),
    (
        "1985-102T10:15Z",
        datetime(1985, 4, 12, 10, 15, tzinfo=UTC),
        DATE_EXT_ORD_COMPLETE + "T" + TIME_EXT_MINUTE + TZ_EXT,
        "1985-102T10:15Z",
    ),
    (
        "1985W155T1015+0400",
        datetime(1985, 4, 12, 10, 15, tzinfo=FixedOffset(4, 0, "+0400")),
        DATE_BAS_WEEK_COMPLETE + "T" + TIME_BAS_MINUTE + TZ_BAS,
        "1985W155T1015+0400",
    ),
    (
        "1985-W15-5T10:15+04",
        datetime(
            1985,
            4,
            12,
            10,
            15,
            tzinfo=FixedOffset(4, 0, "+0400"),
        ),
        DATE_EXT_WEEK_COMPLETE + "T" + TIME_EXT_MINUTE + TZ_HOUR,
        "1985-W15-5T10:15+04",
    ),
    (
        "1985-W15-5T10:15-0430",
        datetime(
            1985,
            4,
            12,
            10,
            15,
            tzinfo=FixedOffset(-4, -30, "-0430"),
        ),
        DATE_EXT_WEEK_COMPLETE + "T" + TIME_EXT_MINUTE + TZ_BAS,
        "1985-W15-5T10:15-0430",
    ),
    (
        "1985-W15-5T10:15+04:45",
        datetime(
            1985,
            4,
            12,
            10,
            15,
            tzinfo=FixedOffset(4, 45, "+04:45"),
        ),
        DATE_EXT_WEEK_COMPLETE + "T" + TIME_EXT_MINUTE + TZ_EXT,
        "1985-W15-5T10:15+04:45",
    ),
    (
        "20110410T101225.123000Z",
        datetime(2011, 4, 10, 10, 12, 25, 123000, tzinfo=UTC),
        DATE_BAS_COMPLETE + "T" + TIME_BAS_COMPLETE + ".%f" + TZ_BAS,
        "20110410T101225.123000Z",
    ),
    (
        "2012-10-12T08:29:46.069178Z",
        datetime(2012, 10, 12, 8, 29, 46, 69178, tzinfo=UTC),
        DATE_EXT_COMPLETE + "T" + TIME_EXT_COMPLETE + ".%f" + TZ_BAS,
        "2012-10-12T08:29:46.069178Z",
    ),
    (
        "2012-10-12T08:29:46.691780Z",
        datetime(2012, 10, 12, 8, 29, 46, 691780, tzinfo=UTC),
        DATE_EXT_COMPLETE + "T" + TIME_EXT_COMPLETE + ".%f" + TZ_BAS,
        "2012-10-12T08:29:46.691780Z",
    ),
    (
        "2012-10-30T08:55:22.1234567Z",
        datetime(2012, 10, 30, 8, 55, 22, 123456, tzinfo=UTC),
        DATE_EXT_COMPLETE + "T" + TIME_EXT_COMPLETE + ".%f" + TZ_BAS,
        "2012-10-30T08:55:22.123456Z",
    ),
    (
        "2012-10-30T08:55:22.1234561Z",
        datetime(2012, 10, 30, 8, 55, 22, 123456, tzinfo=UTC),
        DATE_EXT_COMPLETE + "T" + TIME_EXT_COMPLETE + ".%f" + TZ_BAS,
        "2012-10-30T08:55:22.123456Z",
    ),
    (
        "2014-08-18 14:55:22.123456Z",
        None,
        DATE_EXT_COMPLETE + "T" + TIME_EXT_COMPLETE + ".%f" + TZ_BAS,
        "2014-08-18T14:55:22.123456Z",
    ),
]


def create_testcase(
    datetimestring: str, expectation: datetime | None, format: str, output: str
) -> TestSuite:
    """
    Create a TestCase class for a specific test.

    This allows having a separate TestCase for each test tuple from the
    TEST_CASES list, so that a failed test won't stop other tests.
    """

    class TestDateTime(unittest.TestCase):
        """
        A test case template to parse an ISO datetime string into a
        datetime object.
        """

        def test_parse(self):
            """
            Parse an ISO datetime string and compare it to the expected value.
            """
            if expectation is None:
                self.assertRaises(ISO8601Error, parse_datetime, datetimestring)
            else:
                self.assertEqual(parse_datetime(datetimestring), expectation)

        def test_format(self):
            """
            Take datetime object and create ISO string from it.
            This is the reverse test to test_parse.
            """
            if expectation is None:
                self.assertRaises(
                    AttributeError, datetime_isoformat, expectation, format
                )
            else:
                self.assertEqual(datetime_isoformat(expectation, format), output)

    return unittest.TestLoader().loadTestsFromTestCase(TestDateTime)


def test_suite() -> TestSuite:
    """
    Construct a TestSuite instance for all test cases.
    """
    suite = unittest.TestSuite()
    for datetimestring, expectation, format, output in TEST_CASES:
        suite.addTest(create_testcase(datetimestring, expectation, format, output))
    return suite


# load_tests Protocol
def load_tests(loader, tests, pattern):
    return test_suite()


if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
