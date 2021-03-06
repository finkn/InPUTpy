"""
Note that some tests run multiple test cases and in effect bypass the
setUp for each case. This shouldn't be a problem, but it is worth being
aware of. Each iteration could simply call setUp if necessary.

:copyright: (c) 2013 by Christoffer Fink.
:license: MIT. See LICENSE for details.
"""
import unittest
import inputpy.generators as gen
from test.factories import *
from test.tools import *
from test.types.simple import EmptyClass
from test.types.geo import Point

DESIGN_SPACE_FILE = 'arraySpace.xml'
CODE_MAPPING_FILE = 'arrayMapping.xml'
paramStore = None
designSpace = None

SA1 = 'StringArray1'
SA2 = 'StringArray2'
E = EmptyClass()
P = Point(1, 2)

EXPECTED_ARRAYS = {
    'IntArray1':        [1, 1, 1],
    'IntArray2':        [[[2, 2]], [[2, 2]], [[2, 2]]],
    'FloatArray1':      [3.5, 3.5, 3.5],
    'FloatArray2':      [[[4.5, 4.5]], [[4.5, 4.5]], [[4.5, 4.5]]],
    'StringArray1':     [SA1, SA1, SA1],
    'StringArray2':     [[[SA2, SA2]], [[SA2, SA2]], [[SA2, SA2]]],
    'FixedIntArray':    [[[5, 5]], [[5, 5]], [[5, 5]]],
    'FixedBoolArray':   [[[False, False]], [[False, False]], [[False, False]]],
    'EmptyClassArray1': [E, E, E],
    'EmptyClassArray2': [[[E, E]], [[E, E]], [[E, E]]],
    'PointArray1':      [P, P, P],
    'PointArray2':      [[[P, P]], [[P, P]], [[P, P]]],
}

# Expected array sizes for single / multi dimensional arrays.
SINGLE = (3,)       # [3]
# Note that these are the dimensions of the expected results, not the sizes
# that were declared in the config (missing sizes default to 1).
MULTI = (3, 1, 2)   # [3][][2]

EXPECTED_SIZES = {
    'IntArray1':        SINGLE,
    'IntArray2':        MULTI,
    'FloatArray1':      SINGLE,
    'FloatArray2':      MULTI,
    'StringArray1':     SINGLE,
    'StringArray2':     MULTI,
    'BoolArray1':       SINGLE,
    'BoolArray2':       MULTI,
    'FixedBoolArray':   MULTI,
    'FixedIntArray':    MULTI,
    'EmptyClassArray1': SINGLE,
    'EmptyClassArray2': MULTI,
}

VARIABILITY_TESTS = (
    'BoolArray1', 'EmptyChoiceArray', 'PointChoiceArray',
)

class TestArraySpace(unittest.TestCase):
    """ Various tests using the arraySpace.xml configurations. """

    def setUp(self):
        global paramStore, designSpace
        mappingFactory = PresetCodeMappingFactory.getCodeMapping
        paramStoreFactory = PresetParamStoreFactory.getParamStore
        designSpaceFactory = PresetDesignSpaceFactory.getDesignSpace

        mapping = mappingFactory(CODE_MAPPING_FILE)
        paramStore = paramStoreFactory(DESIGN_SPACE_FILE, mapping)

        designSpace = designSpaceFactory(DESIGN_SPACE_FILE)


    def testVariabilityWhenGettingArrayFromDesignSpace(self):
        for paramId in VARIABILITY_TESTS:
            assertVariability(lambda: designSpace.next(paramId))


    def testSizesForRawParam(self):
        for (paramId, sizes) in EXPECTED_SIZES.items():
            param = paramStore.getParam(paramId)
            array = gen.nextValue(param)
            assertMatchingArrayDimensions(sizes, array)

    def testEqualityForRawParam(self):
        for (paramId, expected) in EXPECTED_ARRAYS.items():
            param = paramStore.getParam(paramId)
            if param.isDependent():
                continue    # Fix: Map ID to dependencies and use those.
            result = gen.nextValue(param)
            self.assertEqual(expected, result)

    def testEqualityForDesignSpaceNext(self):
        for (paramId, expected) in EXPECTED_ARRAYS.items():
            result = designSpace.next(paramId)
            self.assertEqual(expected, result)


    def testUnfixedBooleanArrayShouldBeRandomForRawParam(self):
        param = paramStore.getParam('BoolArray1')
        f = lambda: gen.nextValue(param)
        assertVariability(f)

    # It's one thing to generate different arrays each time, but we also want
    # the elements within an array to be random.
    def testEmptyChoiceArrayShouldHaveRandomElements(self):
        paramId = 'EmptyChoiceArray'
        f = generatorFromSeq(designSpace.next(paramId))
        assertVariability(f)

    # It's one thing to generate different arrays each time, but we also want
    # the elements within an array to be random.
    def testPointChoiceArrayShouldHaveRandomElements(self):
        paramId = 'PointChoiceArray'
        # The array is only 10 elements long. Increasing the number of
        # iterations simply pops the same items multiple times.
        # Two arrays should be enough to guarantee variance.
        # The finite generator will prevent values from being repeated.
        values = designSpace.next(paramId) + designSpace.next(paramId)
        assertVariability(finiteGeneratorFromSeq(values), len(values))


if __name__ == '__main__':
    unittest.main()
