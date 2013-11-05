"""
:copyright: (c) 2013 by Christoffer Fink.
:license: MIT. See LICENSE for details.
"""
import unittest
import warnings
from test.tools import *

# TODO:
# Make a more reliable generator that can replace random.
class TestTools(unittest.TestCase):

    # ----- checkVariability tests -----

    def testAssertVariabilityWithOneIterationShouldFail(self):
        with self.assertRaises(AssertionError):
            assertVariability(lambda: 1, iterations=1)

    def testAssertVariabilityWithConstantValueShouldFail(self):
        with self.assertRaises(AssertionError):
            assertVariability(lambda: 1)

    def testAssertVariabilityWithDifferentValuesShouldSucceed(self):
        values = [1, 1, 1, 1, 2]
        assertVariability(generatorFromSeq(values), 5)

    # The variability test fails even though different values are generated
    # because not enough values are generated to see the variation.
    def testAssertVariabilityFailsIfNotEnoughIterations(self):
        values = [1, 1, 1, 1, 2]
        with self.assertRaises(AssertionError):
            assertVariability(generatorFromSeq(values), 4)


    # ----- checkConstancy tests -----

    def testAssertConstancyWithOneIterationShouldFail(self):
        with self.assertRaises(AssertionError):
            assertConstancy(lambda: 1, iterations=1)

    def testAssertConstancyWithConstantValueShouldSucceed(self):
        assertConstancy(lambda: 1)

    def testAssertConstancyWithRandomValueShouldFail(self):
        values = [1, 1, 1, 1, 2]
        with self.assertRaises(AssertionError):
            assertConstancy(generatorFromSeq(values), 5)

    # Even though the values are not constant, not enough values are
    # generated to see the variation.
    def testAssertConstancySucceedsIfNotEnoughIterations(self):
        values = [1, 1, 1, 1, 2]
        assertConstancy(generatorFromSeq(values), 4)


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
        values = [6,7,8,9] * 20
        expected = [1,2,3,4,5]
        with self.assertRaises(AssertionError):
            assertGeneratesAny(generatorFromSeq(values), expected)

    # Only 2 will be generated, but it matches, and that's enough.
    def testAssertGeneratesAnyShouldSucceedIfAnyMatch(self):
        expected = [1,2,3,4,5]
        assertGeneratesAny(lambda: 2, expected)

    def testAssertGeneratesAllWithTooFewIterationsShouldFail(self):
        values = [2,2,1,5,4,1,1,5,4,3]    # 10 values, 1-5 occur at least once.
        expected = [1,2,3,4,5]
        f = generatorFromSeq(values)
        iterations = len(values) - 1
        with self.assertRaises(AssertionError):
            assertGeneratesAll(f, expected, iterations)

    # One value is missing from the range, so it's impossible to generate all.
    def testAssertGeneratesAllShouldFailIfAnyMismatch(self):
        values = [1,2,3,4] * 20
        expected = [1,2,3,4,5]
        with self.assertRaises(AssertionError):
            assertGeneratesAll(generatorFromSeq(values), expected)

    # 3 does not match, but that is irrelevant as long as 1 and 2 occur.
    def testAssertGeneratesAllShouldSucceedIfAllAreMatched(self):
        values = [1,2,3]
        expected = [1,2]
        assertGeneratesAll(generatorFromSeq(values), expected)

    def testAssertGeneratsAllFailsIfNotEnoughIterations(self):
        values = [1,2,3]
        expected = [1,2]
        assertGeneratesAll(generatorFromSeq(values), expected, 2)

    # 1 and 2 match, but 3 does not.
    def testAssertGeneratesOnlyShouldFailIfAnyMismatch(self):
        values = [1,2,3]
        expected = [1,2]
        with self.assertRaises(AssertionError):
            assertGeneratesOnly(generatorFromSeq(values), expected)

    # The value 3 should cause the test to fail, but there are not enough
    # iterations to reach that value.
    def testAssertGeneratesOnlySucceedsIfNotEnoughIterations(self):
        values = [1,2,3]
        expected = [1,2]
        assertGeneratesOnly(generatorFromSeq(values), expected, 2)

    # There are not enough iterations to generate all expected values, but we
    # don't need to. What is important is that no non-matching values occur.
    def testAssertGeneratesOnlyShouldSucceedIfNoMismatch(self):
        values = [3,4,3,4,5,6,5,6] * 20
        expected = [1,2,3,4,5,6,7,8,9,10]
        assertGeneratesOnly(generatorFromSeq(values), expected)


    def testGeneratorFromSeq(self):
        seq = [0,1,2,3,4,5,6,7,8,9]
        expected = [0,1,2,3,4,5,6,7,8,9]
        f = generatorFromSeq(seq)
        result = [i for i in range(10)]


if __name__ == '__main__':
    unittest.main()
