##############################################################################
# Copyright 2009, Gerhard Weis
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#  * Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#  * Neither the name of the authors nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT
##############################################################################
'''
Test cases for the isodatetime module.
'''
import unittest
from datetime import datetime

from isodate import parse_datetime, UTC, FixedOffset

# the following list contains tuples of ISO datetime strings and the expected
# result from the parse_datetime method. A result of None means an ISO8601Error
# is expected.
TEST_CASES = [('19850412T1015', datetime(1985, 4, 12, 10, 15)),
              ('1985-04-12T10:15', datetime(1985, 4, 12, 10, 15)),
              ('1985102T1015Z', datetime(1985, 4, 12, 10, 15, tzinfo=UTC)),
              ('1985-102T10:15Z', datetime(1985, 4, 12, 10, 15, tzinfo=UTC)),
              ('1985W155T1015+0400', datetime(1985, 4, 12, 10, 15, 
                                              tzinfo=FixedOffset(4, 0, 
                                                                 '+0400'))),
              ('1985-W15-5T10:15+04', datetime(1985, 4, 12, 10, 15, 
                                               tzinfo=FixedOffset(4, 0, 
                                                                  '+0400')))]

def create_testcase(datetimestring, expectation):
    '''
    Create a TestCase class for a specific test.
    
    This allows having a separate TestCase for each test tuple from the
    TEST_CASES list, so that a failed test won't stop other tests.
    '''
    
    class TestDateTime(unittest.TestCase):
        '''
        A test case template to parse an ISO datetime string into a 
        datetime object.
        '''
        
        def test_parse(self):
            '''
            Parse an ISO datetime string and compare it to the expected value.
            '''
            result = parse_datetime(datetimestring)
            self.assertEqual(result, expectation)
            
    return unittest.TestLoader().loadTestsFromTestCase(TestDateTime)

def test_suite():
    '''
    Construct a TestSuite instance for all test cases.
    '''
    suite = unittest.TestSuite()
    for datetimestring, expectation in TEST_CASES:
        suite.addTest(create_testcase(datetimestring, expectation))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
