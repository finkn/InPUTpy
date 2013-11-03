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

    def testAssertVariabilityWithOneIterationShouldFail(self):
        with self.assertRaises(AssertionError):
            assertVariability(None, iterations=1)

    def testAssertVariabilityWithConstantValueShouldFail(self):
        with self.assertRaises(AssertionError):
            assertVariability(lambda: 1)

    def testAssertVariabilityWithRandomValueShouldSucceed(self):
        assertVariability(lambda: random.randint(1, 10000))


    # ----- checkConstancy tests -----

    def testAssertConstancyWithOneIterationShouldFail(self):
        with self.assertRaises(AssertionError):
            assertConstancy(None, iterations=1)

    def testAssertConstancyWithConstantValueShouldSucceed(self):
        assertConstancy(lambda: 1)

    def testAssertConstancyWithRandomValueShouldFail(self):
        with self.assertRaises(AssertionError):
            assertConstancy(lambda: random.randint(1, 10000))


    # ----- checkArrayDimensions tests -----

    def testSingleDimensionArrayWithMatchingSizeShouldSucceed(self):
        tests = (
            ((0,), []),
            ((1,), [1]),
            ((5,), [1, 1, 1, 1, 1]),
        )
        for (sizes, array) in tests:
            assertMatchingArrayDimensions(sizes, array)

    def testSingleDimensionArrayWithWrongSizeShouldFail(self):
        tests = (
            ((1,), []),
            ((0,), [1]),
            ((1,), [1, 1, 1, 1, 1]),
        )
        for (sizes, array) in tests:
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
            assertMatchingArrayDimensions(sizes, array)

    def testMultiDimensionalArrayWithWrongSizesShouldFail(self):
        tests = (
            ((2, 0), [1]),              # Actually (1,)
            ((2, 1), [[1, 1], [1, 1]]), # Actually (2, 2)
            ((1, 2, 2), [[[1], [1]]]),  # Actually (1, 2, 1)
        )
        for (sizes, array) in tests:
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


    def testGeneratorFromSeq(self):
        seq = [0,1,2,3,4,5,6,7,8,9]
        expected = [0,1,2,3,4,5,6,7,8,9]
        f = generatorFromSeq(seq)
        result = [i for i in range(10)]


if __name__ == '__main__':
    unittest.main()
