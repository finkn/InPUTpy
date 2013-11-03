"""
:copyright: (c) 2013 by Christoffer Fink.
:license: MIT. See LICENSE for details.
"""
import unittest
import random
import warnings
from test.tools import *

# TODO:
# Make a more reliable generator that can replace random.
class TestTools(unittest.TestCase):

    # ----- checkVariability tests -----

    def testCheckVariabilityWithOneIterationShouldFail(self):
        with warnings.catch_warnings(record=False):
            warnings.simplefilter('ignore')
            with self.assertRaises(AssertionError):
                checkVariability(None, iterations=1)

    def testCheckVariabilityWithConstantValueShouldFail(self):
        with warnings.catch_warnings(record=False):
            warnings.simplefilter('ignore')
            self.assertFalse(checkVariability(lambda: 1))

    def testCheckVariabilityWithRandomValueShouldSucceed(self):
        with warnings.catch_warnings(record=False):
            warnings.simplefilter('ignore')
            self.assertTrue(checkVariability(lambda: random.randint(1, 10000)))


    # ----- checkConstancy tests -----

    def testCheckConstancyWithOneIterationShouldFail(self):
        with warnings.catch_warnings(record=False):
            warnings.simplefilter('ignore')
            with self.assertRaises(AssertionError):
                checkConstancy(None, iterations=1)

    def testCheckConstancyWithConstantValueShouldFail(self):
        with warnings.catch_warnings(record=False):
            warnings.simplefilter('ignore')
            self.assertTrue(checkConstancy(lambda: 1))

    def testCheckConstancyWithRandomValueShouldSucceed(self):
        with warnings.catch_warnings(record=False):
            warnings.simplefilter('ignore')
            self.assertFalse(checkConstancy(lambda: random.randint(1, 10000)))


    # ----- checkArrayDimensions tests -----

    def testSingleDimensionArrayWithMatchingSizeShouldSucceed(self):
        tests = (
            ((0,), []),
            ((1,), [1]),
            ((5,), [1, 1, 1, 1, 1]),
        )
        for (sizes, array) in tests:
            with warnings.catch_warnings(record=False):
                warnings.simplefilter('ignore')
                self.assertTrue(checkArrayDimensions(sizes, array))
            assertMatchingArrayDimensions(sizes, array)

    def testSingleDimensionArrayWithWrongSizeShouldFail(self):
        tests = (
            ((1,), []),
            ((0,), [1]),
            ((1,), [1, 1, 1, 1, 1]),
        )
        for (sizes, array) in tests:
            with warnings.catch_warnings(record=False):
                warnings.simplefilter('ignore')
                self.assertFalse(checkArrayDimensions(sizes, array))
            with self.assertRaises(AssertionError):
                assertMatchingArrayDimensions(sizes, array)

    def testMultiDimensionalArrayWithMatchingSizesShouldSucceed(self):
        tests = (
            ((2, 0), [[], []]),
            ((2, 1), [[1], [1]]),
            ((2, 1), [[[]], [[]]]), # The elements happen to be lists.
            ((1, 2, 2), [[[1, 1], [1, 1]]]),
        )
        for (sizes, array) in tests:
            with warnings.catch_warnings(record=False):
                warnings.simplefilter('ignore')
                msg = 'sizes %s did not match array %s' % (sizes, array)
                self.assertTrue(checkArrayDimensions(sizes, array), msg=msg)
            assertMatchingArrayDimensions(sizes, array)

    def testMultiDimensionalArrayWithWrongSizesShouldFail(self):
        tests = (
            ((2, 0), [1]),              # Actually (1,)
            ((2, 1), [[1, 1], [1, 1]]), # Actually (2, 2)
            ((1, 2, 2), [[[1], [1]]]),  # Actually (1, 2, 1)
        )
        for (sizes, array) in tests:
            with warnings.catch_warnings(record=False):
                warnings.simplefilter('ignore')
                msg = 'sizes %s matched array %s' % (sizes, array)
                self.assertFalse(checkArrayDimensions(sizes, array), msg=msg)
            with self.assertRaises(AssertionError):
                assertMatchingArrayDimensions(sizes, array)


    # ----- check(Any|All)ValuesMatch tests -----

    def testCheckAnyValueMatchesForAnyEmptyArgumentShouldFail(self):
        with warnings.catch_warnings(record=False):
            warnings.simplefilter('ignore')
            self.assertFalse(checkAnyValueMatches([], []))
            self.assertFalse(checkAnyValueMatches([], [1,2,3]))
            self.assertFalse(checkAnyValueMatches([1,2,3], []))

    def testCheckAllValuesMatchForEmptyValuesShouldSucceed(self):
        with warnings.catch_warnings(record=False):
            warnings.simplefilter('ignore')
            self.assertTrue(checkAllValuesMatch([], [1,2,3]))
            self.assertTrue(checkAllValuesMatch([], []))

    def testCheckAllValuesMatchForEmptyExpectedShouldFail(self):
        with warnings.catch_warnings(record=False):
            warnings.simplefilter('ignore')
            self.assertFalse(checkAllValuesMatch([1,2,3], []))

    def testCheckAnyAndAllValuesShouldMatchWithSingleElement(self):
        with warnings.catch_warnings(record=False):
            warnings.simplefilter('ignore')
            self.assertTrue(checkAnyValueMatches([1], [1]))
            self.assertTrue(checkAllValuesMatch([1], [1]))

    def testCheckAnyValueMatchesShouldMatchWithMixedElements(self):
        with warnings.catch_warnings(record=False):
            warnings.simplefilter('ignore')
            self.assertTrue(checkAnyValueMatches([1,2,3], ['a',2,False]))

    def testCheckAllValuesMatchShouldNotMAtchWithMixedElements(self):
        with warnings.catch_warnings(record=False):
            warnings.simplefilter('ignore')
            self.assertFalse(checkAllValuesMatch([1,2,3], ['a',2,False]))


    # ----- check generated values matching tests -----

    def testCheckGeneratesAnyExpectedShouldFailIfNoneMatch(self):
        with warnings.catch_warnings(record=False):
            warnings.simplefilter('ignore')
            f = lambda: random.randint(10,20)
            expected = [1,2,3,4,5]
            self.assertFalse(checkGeneratesAnyExpected(f, expected))

    # Only 2 will be generated, but it matches, and that's enough.
    def testCheckGeneratesAnyExpectedShouldSucceedIfAnyMatch(self):
        with warnings.catch_warnings(record=False):
            warnings.simplefilter('ignore')
            f = lambda: 2
            expected = [1,2,3,4,5]
            self.assertTrue(checkGeneratesAnyExpected(f, expected))

    def testCheckGeneratesAllExpectedWithTooFewIterationsShouldFail(self):
        with warnings.catch_warnings(record=False):
            warnings.simplefilter('ignore')
            f = lambda: random.randint(1,5)
            expected = [1,2,3,4,5]
            with self.assertRaises(AssertionError):
                self.assertFalse(checkGeneratesAllExpected(f, expected, 4))

    # One value is missing from the range, so it's impossible to generate all.
    def testCheckGeneratesAllExpectedShouldFailIfAnyMismatch(self):
        with warnings.catch_warnings(record=False):
            warnings.simplefilter('ignore')
            f = lambda: random.randint(1,4)
            expected = [1,2,3,4,5]
            self.assertFalse(checkGeneratesAllExpected(f, expected))

    # 3 does not match, but that is irrelevant as long as 1 and 2 occur.
    def testCheckGeneratesAllExpectedShouldSucceedIfAllAreMatched(self):
        with warnings.catch_warnings(record=False):
            warnings.simplefilter('ignore')
            f = lambda: random.randint(1,3)
            expected = [1,2]
            self.assertTrue(checkGeneratesAllExpected(f, expected))

    # 1 and 2 match, but 3 (which will probably be generated) does not.
    def testCheckGeneratesOnlyExpectedShouldFailIfAnyMismatch(self):
        with warnings.catch_warnings(record=False):
            warnings.simplefilter('ignore')
            f = lambda: random.randint(1,3)
            expected = [1,2]
            self.assertFalse(checkGeneratesOnlyExpected(f, expected, 20))

    # There are not enough iterations to generate all expected values, but we
    # don't need to. What is important is that no non-matching values occur.
    def testCheckGeneratesOnlyExpectedShouldSucceedIfNoMismatch(self):
        with warnings.catch_warnings(record=False):
            warnings.simplefilter('ignore')
            f = lambda: random.randint(1,10)
            expected = [1,2,3,4,5,6,7,8,9,10]
            self.assertTrue(checkGeneratesOnlyExpected(f, expected, 9))


    # ----- assert generated values matching tests -----

    def testAssertGeneratesAnyShouldFailIfNoneMatch(self):
        f = lambda: random.randint(10,20)
        expected = [1,2,3,4,5]
        with self.assertRaises(AssertionError):
            assertGeneratesAny(f, expected)

    # Only 2 will be generated, but it matches, and that's enough.
    def testAssertGeneratesAnyShouldSucceedIfAnyMatch(self):
        f = lambda: 2
        expected = [1,2,3,4,5]
        assertGeneratesAny(f, expected)

    def testAssertGeneratesAllWithTooFewIterationsShouldFail(self):
        f = lambda: random.randint(1,5)
        expected = [1,2,3,4,5]
        with self.assertRaises(AssertionError):
            assertGeneratesAll(f, expected, 4)

    # One value is missing from the range, so it's impossible to generate all.
    def testAssertGeneratesAllShouldFailIfAnyMismatch(self):
        f = lambda: random.randint(1,4)
        expected = [1,2,3,4,5]
        with self.assertRaises(AssertionError):
            assertGeneratesAll(f, expected)

    # 3 does not match, but that is irrelevant as long as 1 and 2 occur.
    def testAssertGeneratesAllShouldSucceedIfAllAreMatched(self):
        f = lambda: random.randint(1,3)
        expected = [1,2]
        assertGeneratesAll(f, expected)

    # 1 and 2 match, but 3 (which will probably be generated) does not.
    def testAssertGeneratesOnlyShouldFailIfAnyMismatch(self):
        f = lambda: random.randint(1,3)
        expected = [1,2]
        with self.assertRaises(AssertionError):
            assertGeneratesOnly(f, expected, 20)

    # There are not enough iterations to generate all expected values, but we
    # don't need to. What is important is that no non-matching values occur.
    def testAssertGeneratesOnlyShouldSucceedIfNoMismatch(self):
        f = lambda: random.randint(1,10)
        expected = [1,2,3,4,5,6,7,8,9,10]
        assertGeneratesOnly(f, expected, 9)

if __name__ == '__main__':
    unittest.main()
