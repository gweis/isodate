"""
Test cases for the isodate module.
"""
import unittest
import time
from datetime import datetime, timedelta
from isodate import strftime
from isodate import LOCAL
from isodate import DT_EXT_COMPLETE
from isodate import tzinfo


TEST_CASES = (
    (
        datetime(2012, 12, 25, 13, 30, 0, 0, LOCAL),
        DT_EXT_COMPLETE,
        "2012-12-25T13:30:00+10:00",
    ),
    # DST ON
    (
        datetime(1999, 12, 25, 13, 30, 0, 0, LOCAL),
        DT_EXT_COMPLETE,
        "1999-12-25T13:30:00+11:00",
    ),
    # microseconds
    (
        datetime(2012, 10, 12, 8, 29, 46, 69178),
        "%Y-%m-%dT%H:%M:%S.%f",
        "2012-10-12T08:29:46.069178",
    ),
    (
        datetime(2012, 10, 12, 8, 29, 46, 691780),
        "%Y-%m-%dT%H:%M:%S.%f",
        "2012-10-12T08:29:46.691780",
    ),
)


def create_testcase(dt, format, expectation):
    """
    Create a TestCase class for a specific test.

    This allows having a separate TestCase for each test tuple from the
    TEST_CASES list, so that a failed test won't stop other tests.
    """

    class TestDate(unittest.TestCase):
        """
        A test case template to test ISO date formatting.
        """

        # local time zone mock function
        def localtime_mock(self, secs):
            """
            mock time.localtime so that it always returns a time_struct with
            tm_idst=1
            """
            tt = self.ORIG["localtime"](secs)
            # befor 2000 everything is dst, after 2000 no dst.
            if tt.tm_year < 2000:
                dst = 1
            else:
                dst = 0
            tt = (
                tt.tm_year,
                tt.tm_mon,
                tt.tm_mday,
                tt.tm_hour,
                tt.tm_min,
                tt.tm_sec,
                tt.tm_wday,
                tt.tm_yday,
                dst,
            )
            return time.struct_time(tt)

        def setUp(self):
            self.ORIG = {}
            self.ORIG["STDOFFSET"] = tzinfo.STDOFFSET
            self.ORIG["DSTOFFSET"] = tzinfo.DSTOFFSET
            self.ORIG["DSTDIFF"] = tzinfo.DSTDIFF
            self.ORIG["localtime"] = time.localtime
            # ovveride all saved values with fixtures.
            # calculate LOCAL TZ offset, so that this test runs in
            # every time zone
            tzinfo.STDOFFSET = timedelta(seconds=36000)  # assume LOC = +10:00
            tzinfo.DSTOFFSET = timedelta(seconds=39600)  # assume DST = +11:00
            tzinfo.DSTDIFF = tzinfo.DSTOFFSET - tzinfo.STDOFFSET
            time.localtime = self.localtime_mock

        def tearDown(self):
            # restore test fixtures
            tzinfo.STDOFFSET = self.ORIG["STDOFFSET"]
            tzinfo.DSTOFFSET = self.ORIG["DSTOFFSET"]
            tzinfo.DSTDIFF = self.ORIG["DSTDIFF"]
            time.localtime = self.ORIG["localtime"]

        def test_format(self):
            """
            Take date object and create ISO string from it.
            This is the reverse test to test_parse.
            """
            if expectation is None:
                self.assertRaises(AttributeError, strftime(dt, format))
            else:
                self.assertEqual(strftime(dt, format), expectation)

    return unittest.TestLoader().loadTestsFromTestCase(TestDate)


def test_suite():
    """
    Construct a TestSuite instance for all test cases.
    """
    suite = unittest.TestSuite()
    for dt, format, expectation in TEST_CASES:
        suite.addTest(create_testcase(dt, format, expectation))
    return suite


# load_tests Protocol
def load_tests(loader, tests, pattern):
    return test_suite()


if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
