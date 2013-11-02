"""
:copyright: (c) 2013 by Christoffer Fink.
:license: MIT. See LICENSE for details.
"""
import unittest
import random
from test.tools import *

class TestTools(unittest.TestCase):

    # --- checkVariability tests ---
    def testCheckVariabilityWithOneIterationShouldFail(self):
        with self.assertRaises(AssertionError):
            checkVariability(None, iterations=1)

    def testCheckVariabilityWithConstantValueShouldFail(self):
        self.assertFalse(checkVariability(lambda: 1))

    def testCheckVariabilityWithRandomValueShouldSucceed(self):
        self.assertTrue(checkVariability(lambda: random.randint(1, 10000)))


    # --- checkConstancy tests ---
    def testCheckConstancyWithOneIterationShouldFail(self):
        with self.assertRaises(AssertionError):
            checkConstancy(None, iterations=1)

    def testCheckConstancyWithConstantValueShouldFail(self):
        self.assertTrue(checkConstancy(lambda: 1))

    def testCheckConstancyWithRandomValueShouldSucceed(self):
        self.assertFalse(checkConstancy(lambda: random.randint(1, 10000)))


    # --- checkArrayDimensions tests ---
    def testSingleDimensionArrayWithMatchingSizeShouldSucceed(self):
        tests = (
            ((0,), []),
            ((1,), [1]),
            ((5,), [1, 1, 1, 1, 1]),
        )
        for (sizes, array) in tests:
            self.assertTrue(checkArrayDimensions(sizes, array))

    def testSingleDimensionArrayWithWrongSizeShouldFail(self):
        tests = (
            ((1,), []),
            ((0,), [1]),
            ((1,), [1, 1, 1, 1, 1]),
        )
        for (sizes, array) in tests:
            self.assertFalse(checkArrayDimensions(sizes, array))

    def testMultiDimensionalArrayWithMatchingSizesShouldSucceed(self):
        tests = (
            ((2, 0), [[], []]),
            ((2, 1), [[1], [1]]),
            ((2, 1), [[[]], [[]]]), # The elements happen to be lists.
            ((1, 2, 2), [[[1, 1], [1, 1]]]),
        )
        for (sizes, array) in tests:
            msg = 'sizes %s did not match array %s' % (sizes, array)
            self.assertTrue(checkArrayDimensions(sizes, array), msg=msg)

    def testMultiDimensionalArrayWithWrongSizesShouldFail(self):
        tests = (
            ((2, 0), [1]),              # Actually (1,)
            ((2, 1), [[1, 1], [1, 1]]), # Actually (2, 2)
            ((1, 2, 2), [[[1], [1]]]),  # Actually (1, 2, 1)
        )
        for (sizes, array) in tests:
            msg = 'sizes %s matched array %s' % (sizes, array)
            self.assertFalse(checkArrayDimensions(sizes, array), msg=msg)

if __name__ == '__main__':
    unittest.main()
