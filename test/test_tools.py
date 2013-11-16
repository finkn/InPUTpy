"""
:copyright: (c) 2013 by Christoffer Fink.
:license: MIT. See LICENSE for details.
"""
import unittest
import warnings
from test.tools import *

class TestTools(unittest.TestCase):

    # ----- assertVariability tests -----

    def testAssertVariabilityWithOneIterationShouldFail(self):
        with self.assertRaises(AssertionError):
            Generator.fromSequence([1,2,3]).isVariable(iterations=1)

    def testAssertVariabilityWithConstantValueShouldFail(self):
        with self.assertRaises(AssertionError):
            Generator.fromFunction(lambda: 1).isVariable()

    def testAssertVariabilityWithDifferentValuesShouldSucceed(self):
        Generator.fromSequence([1,1,1,1,2]).isVariable(iterations=5)

    # The variability test fails even though different values are generated
    # because not enough values are generated to see the variation.
    def testAssertVariabilityFailsIfNotEnoughIterations(self):
        with self.assertRaises(AssertionError):
            Generator.fromSequence([1,1,1,1,2]).isVariable(iterations=4)


    # ----- assertConstancy tests -----

    def testAssertConstancyWithOneIterationShouldFail(self):
        with self.assertRaises(AssertionError):
            Generator.fromFunction(lambda: 1).isConstant(iterations=1)

    def testAssertConstancyWithConstantValueShouldSucceed(self):
        Generator.fromFunction(lambda: 1).isConstant()

    def testAssertConstancyWithDifferentValueShouldFail(self):
        with self.assertRaises(AssertionError):
            Generator.fromSequence([1,1,1,1,2]).isConstant(iterations=5)

    # Even though the values are not constant, not enough values are
    # generated to see the variation.
    def testAssertConstancySucceedsIfNotEnoughIterations(self):
        Generator.fromSequence([1,1,1,1,2]).isConstant(iterations=4)


    # ----- assertMatchingArrayDimensions tests -----

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


    # ----- assert generated values matching tests -----

    def testAssertGeneratesAnyShouldFailIfNoneMatch(self):
        values = [6,7,8,9]
        expected = [1,2,3,4,5]
        with self.assertRaises(AssertionError):
            Generator.fromSequence(values).generatesAny(expected)

    # Only 2 will be generated, but it matches, and that's enough.
    def testAssertGeneratesAnyShouldSucceedIfAnyMatch(self):
        expected = [1,2,3,4,5]
        Generator.fromFunction(lambda: 2).generatesAny(expected)

    def testAssertGeneratesAllWithTooFewIterationsShouldFail(self):
        values = [2,2,1,5,4,1,1,5,4,3]    # 10 values, 1-5 occur at least once.
        expected = [1,2,3,4,5]
        gen = Generator.fromSequence(values)
        iterations = len(values) - 1
        with self.assertRaises(AssertionError):
            gen.generatesAll(expected, iterations)

    def testAssertGeneratesAllShouldFailIfAnyMissing(self):
        values = [1,2,3,4]
        expected = [1,2,3,4,5]
        with self.assertRaises(AssertionError):
            Generator.fromSequence(values).generatesAll(expected)

    # 3 does not match, but that is irrelevant as long as 1 and 2 occur.
    def testAssertGeneratesAllShouldSucceedIfAllAreMatched(self):
        Generator.fromSequence([3,1,2]).generatesAll([1,2])

    def testAssertGeneratsAllFailsIfNotEnoughIterations(self):
        Generator.fromSequence([1,2,3]).generatesAll([1,2], 2)

    # 1 and 2 match, but 3 does not.
    def testAssertGeneratesOnlyShouldFailIfAnyMismatch(self):
        values = [1,2,3]
        expected = [1,2]
        with self.assertRaises(AssertionError):
            Generator.fromSequence([1,2,3]).generatesOnly([1,2])

    # The value 3 should cause the test to fail, but there are not enough
    # iterations to reach that value.
    def testAssertGeneratesOnlySucceedsIfNotEnoughIterations(self):
        Generator.fromSequence([1,2,3]).generatesOnly([1,2], 2)

    # All accepted values are not generated, but we don't need to.
    # What is important is that no non-matching values occur.
    def testAssertGeneratesOnlyShouldSucceedIfNoMismatch(self):
        values = [3,4,3,4,5,6,5,6]
        expected = [1,2,3,4,5,6,7,8,9,10]
        Generator.fromSequence(values).generatesOnly(expected)


    # ----- generator from sequence tests -----

    def testFiniteGeneratorFromSeq(self):
        seq = [0,1,2,3,4,5,6,7,8,9]
        expected = [0,1,2,3,4,5,6,7,8,9]
        f = Generator.fromSequence(seq, finite=True)
        result = [f() for i in range(len(seq))]
        self.assertEqual(expected, result)

    def testFiniteGeneratorFromSeqShouldRaiseErrorWhenExhausted(self):
        seq = [0,1,2,3,4,5,6,7,8,9]
        f = Generator.fromSequence(seq, finite=True)
        with self.assertRaises(IndexError):
            result = [f() for i in range(len(seq) + 1)]

    # Expecting a result that is 3 times as long as the sequence.
    def testInfiniteGeneratorFromSeqShouldWrapAround(self):
        seq = [0,1,2,3]
        expected = [0,1,2,3] * 3
        f = Generator.fromSequence(seq)
        iterations = len(expected)
        self.assertTrue(len(seq) < iterations)
        result = [f() for i in range(iterations)]
        self.assertEqual(expected, result)


    # This test is partially redundant, but it specifically confirms that
    # most functions do not execute all iterations unless they have to.
    # A finite generator of otherwise insufficient length is used as a test.
    def testShortcut(self):
        seq = [1,2,3,4,1]
        expected = [1,2,3]
        it = len(seq) * 100  # Much greater than length.
        # Now do tests. If they didn't shortcut, an IndexError would be raised.
        assertVariability(finiteGeneratorFromSeq(seq), it)
        assertGeneratesAny(finiteGeneratorFromSeq(seq), expected, it)
        assertGeneratesAll(finiteGeneratorFromSeq(seq), expected, it)
        # We expect these tests to fail early (not because values ran out).
        with self.assertRaises(AssertionError):
            assertConstancy(finiteGeneratorFromSeq(seq), it)
        with self.assertRaises(AssertionError):
            assertGeneratesOnly(finiteGeneratorFromSeq(seq), expected, it)


    # ----- Interval tests -----
    def testInterval(self):
        tests = {
            '[1,3]':    ([1,2,3], [0,4]),
            ']1,3]':    ([2,3], [0,1,4]),
            '[1,3[':    ([1,2], [0,3,4]),
            ']1,3[':    ([2], [0,1,3,4]),

            '[*,3]':    ([-1,3], [4,5]),
            '[1,*]':    ([1,2,3], [-1,0]),
            '[*,3[':    ([-1,2], [3,4,5]),
            ']1,*]':    ([2,3], [-1,0,1]),
            '[*,*]':    ([1,2,3], []),
            ']*,*[':    ([1,2,2], []),

            '[.005,.01]': ([.005, .0051, .009, .01], [.0049, .011]),
            '].005,.01]': ([.0051, .009, .01], [.005, .0049, .011]),
            '[.005,.01[': ([.005, .0051, .009], [.0049, .011, .01]),
            '].005,.01[': ([.0051, .009], [.005, .0049, .011, .01]),
        }
        for (k, v) in tests.items():
            (included, excluded) = v
            for value in included:
                Interval(k).contains(value)
                with self.assertRaises(AssertionError):
                    Interval(k).doesNotContain(value)
            for value in excluded:
                Interval(k).doesNotContain(value)
                with self.assertRaises(AssertionError):
                    Interval(k).contains(value)

    def testEvaluatedIntervalWithDependenciesFails(self):
        with self.assertRaises(AssertionError):
            Interval('[A, 3]')


    def testValueSink(self):
        def acceptGT3(x):
            if x <= 3: raise ValueError
        def acceptLT3(x):
            if x >= 3: raise ValueError
        def accept3(x):
            if x != 3: raise ValueError
        def acceptAll(x):
            pass
        def rejectAll(x):
            raise ValueError

        tests = {
            # function    accepts, rejects
            acceptGT3:    ([4,5],   [2,3]),
            acceptLT3:    ([1,2],   [3,4]),
            accept3:      ([3],     [2,4]),
            acceptAll:    ([1,2,3], []),
            rejectAll:    ([],      [1,2,3]),
        }

        # Make a ValueSink from each (lambda) function...
        for (k,v) in tests.items():
            (accepted, rejected) = v
            sink = ValueSink(k)

            # ...and check that it accepts and rejects the appropriate values.
            for value in accepted:
                sink.accepts(value)
                with self.assertRaises(AssertionError):
                    sink.rejects(value)

            for value in rejected:
                sink.rejects(value)
                with self.assertRaises(AssertionError):
                    sink.accepts(value)

if __name__ == '__main__':
    unittest.main()
