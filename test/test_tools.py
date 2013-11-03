"""
:copyright: (c) 2013 by Christoffer Fink.
:license: MIT. See LICENSE for details.
"""
import unittest
import random
from test.tools import *

# TODO:
# Make a more reliable generator that can replace random.
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


    # --- check(Any|All)ValuesMatch tests ---
    def testCheckAnyValueMatchesForAnyEmptyArgumentShouldFail(self):
        self.assertFalse(checkAnyValueMatches([], []))
        self.assertFalse(checkAnyValueMatches([], [1,2,3]))
        self.assertFalse(checkAnyValueMatches([1,2,3], []))

    def testCheckAllValuesMatchForEmptyValuesShouldSucceed(self):
        self.assertTrue(checkAllValuesMatch([], [1,2,3]))
        self.assertTrue(checkAllValuesMatch([], []))

    def testCheckAllValuesMatchForEmptyExpectedShouldFail(self):
        self.assertFalse(checkAllValuesMatch([1,2,3], []))

    def testCheckAnyAndAllValuesShouldMatchWithSingleElement(self):
        self.assertTrue(checkAnyValueMatches([1], [1]))
        self.assertTrue(checkAllValuesMatch([1], [1]))

    def testCheckAnyValueMatchesShouldMatchWithMixedElements(self):
        self.assertTrue(checkAnyValueMatches([1,2,3], ['a',2,False]))

    def testCheckAllValuesMatchShouldNotMAtchWithMixedElements(self):
        self.assertFalse(checkAllValuesMatch([1,2,3], ['a',2,False]))


    # --- check generated values matching tests ---
    def testCheckGeneratesAnyExpectedShouldFailIfNoneMatch(self):
        f = lambda: random.randint(10,20)
        expected = [1,2,3,4,5]
        self.assertFalse(checkGeneratesAnyExpected(f, expected))

    # Only 2 will be generated, but it matches, and that's enough.
    def testCheckGeneratesAnyExpectedShouldSucceedIfAnyMatch(self):
        f = lambda: 2
        expected = [1,2,3,4,5]
        self.assertTrue(checkGeneratesAnyExpected(f, expected))

    def testCheckGeneratesAllExpectedWithTooFewIterationsShouldFail(self):
        f = lambda: random.randint(1,5)
        expected = [1,2,3,4,5]
        with self.assertRaises(AssertionError):
            self.assertFalse(checkGeneratesAllExpected(f, expected, 4))

    # One value is missing from the range, so it's impossible to generate all.
    def testCheckGeneratesAllExpectedShouldFailIfAnyMismatch(self):
        f = lambda: random.randint(1,4)
        expected = [1,2,3,4,5]
        self.assertFalse(checkGeneratesAllExpected(f, expected))

    # 3 does not match, but that is irrelevant as long as 1 and 2 occur.
    def testCheckGeneratesAllExpectedShouldSucceedIfAllAreMatched(self):
        f = lambda: random.randint(1,3)
        expected = [1,2]
        self.assertTrue(checkGeneratesAllExpected(f, expected))

    # 1 and 2 match, but 3 (which will probably be generated) does not.
    def testCheckGeneratesOnlyExpectedShouldFailIfAnyMismatch(self):
        f = lambda: random.randint(1,3)
        expected = [1,2]
        self.assertFalse(checkGeneratesOnlyExpected(f, expected, 20))

    # There are not enough iterations to generate all expected values, but we
    # don't need to. What is important is that no non-matching values occur.
    def testCheckGeneratesOnlyExpectedShouldSucceedIfNoMismatch(self):
        f = lambda: random.randint(1,10)
        expected = [1,2,3,4,5,6,7,8,9,10]
        self.assertTrue(checkGeneratesOnlyExpected(f, expected, 9))


if __name__ == '__main__':
    unittest.main()
