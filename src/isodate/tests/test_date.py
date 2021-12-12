"""
Test cases for the isodate module.
"""
import unittest
from datetime import date
from isodate import parse_date, ISO8601Error, date_isoformat
from isodate import DATE_CENTURY, DATE_YEAR
from isodate import DATE_BAS_MONTH, DATE_EXT_MONTH
from isodate import DATE_EXT_COMPLETE, DATE_BAS_COMPLETE
from isodate import DATE_BAS_ORD_COMPLETE, DATE_EXT_ORD_COMPLETE
from isodate import DATE_BAS_WEEK, DATE_BAS_WEEK_COMPLETE
from isodate import DATE_EXT_WEEK, DATE_EXT_WEEK_COMPLETE

# the following list contains tuples of ISO date strings and the expected
# result from the parse_date method. A result of None means an ISO8601Error
# is expected. The test cases are grouped into dates with 4 digit years
# and 6 digit years.
TEST_CASES = {
    4: [
        ("19", date(1901, 1, 1), DATE_CENTURY),
        ("1985", date(1985, 1, 1), DATE_YEAR),
        ("1985-04", date(1985, 4, 1), DATE_EXT_MONTH),
        ("198504", date(1985, 4, 1), DATE_BAS_MONTH),
        ("1985-04-12", date(1985, 4, 12), DATE_EXT_COMPLETE),
        ("19850412", date(1985, 4, 12), DATE_BAS_COMPLETE),
        ("1985102", date(1985, 4, 12), DATE_BAS_ORD_COMPLETE),
        ("1985-102", date(1985, 4, 12), DATE_EXT_ORD_COMPLETE),
        ("1985W155", date(1985, 4, 12), DATE_BAS_WEEK_COMPLETE),
        ("1985-W15-5", date(1985, 4, 12), DATE_EXT_WEEK_COMPLETE),
        ("1985W15", date(1985, 4, 8), DATE_BAS_WEEK),
        ("1985-W15", date(1985, 4, 8), DATE_EXT_WEEK),
        ("1989-W15", date(1989, 4, 10), DATE_EXT_WEEK),
        ("1989-W15-5", date(1989, 4, 14), DATE_EXT_WEEK_COMPLETE),
        ("1-W1-1", None, DATE_BAS_WEEK_COMPLETE),
    ],
    6: [
        ("+0019", date(1901, 1, 1), DATE_CENTURY),
        ("+001985", date(1985, 1, 1), DATE_YEAR),
        ("+001985-04", date(1985, 4, 1), DATE_EXT_MONTH),
        ("+001985-04-12", date(1985, 4, 12), DATE_EXT_COMPLETE),
        ("+0019850412", date(1985, 4, 12), DATE_BAS_COMPLETE),
        ("+001985102", date(1985, 4, 12), DATE_BAS_ORD_COMPLETE),
        ("+001985-102", date(1985, 4, 12), DATE_EXT_ORD_COMPLETE),
        ("+001985W155", date(1985, 4, 12), DATE_BAS_WEEK_COMPLETE),
        ("+001985-W15-5", date(1985, 4, 12), DATE_EXT_WEEK_COMPLETE),
        ("+001985W15", date(1985, 4, 8), DATE_BAS_WEEK),
        ("+001985-W15", date(1985, 4, 8), DATE_EXT_WEEK),
    ],
}


def create_testcase(yeardigits, datestring, expectation, format):
    """
    Create a TestCase class for a specific test.

    This allows having a separate TestCase for each test tuple from the
    TEST_CASES list, so that a failed test won't stop other tests.
    """

    class TestDate(unittest.TestCase):
        """
        A test case template to parse an ISO date string into a date
        object.
        """

        def test_parse(self):
            """
            Parse an ISO date string and compare it to the expected value.
            """
            if expectation is None:
                self.assertRaises(ISO8601Error, parse_date, datestring, yeardigits)
            else:
                result = parse_date(datestring, yeardigits)
                self.assertEqual(result, expectation)

        def test_format(self):
            """
            Take date object and create ISO string from it.
            This is the reverse test to test_parse.
            """
            if expectation is None:
                self.assertRaises(
                    AttributeError, date_isoformat, expectation, format, yeardigits
                )
            else:
                self.assertEqual(
                    date_isoformat(expectation, format, yeardigits), datestring
                )

    return unittest.TestLoader().loadTestsFromTestCase(TestDate)


def test_suite():
    """
    Construct a TestSuite instance for all test cases.
    """
    suite = unittest.TestSuite()
    for yeardigits, tests in TEST_CASES.items():
        for datestring, expectation, format in tests:
            suite.addTest(create_testcase(yeardigits, datestring, expectation, format))
    return suite


# load_tests Protocol
def load_tests(loader, tests, pattern):
    return test_suite()


if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
