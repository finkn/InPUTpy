"""
Note that some tests run multiple test cases and in effect bypass the
setUp for each case. This shouldn't be a problem, but it is worth being
aware of. Each iteration could simply call setUp if necessary.

:copyright: (c) 2013 by Christoffer Fink.
:license: MIT. See LICENSE for details.
"""
import unittest
from test.factories import *
from test.types.simple import *
from test.types.geo import *
from test.tools import *
from inputpy.q import *
from inputpy.factories import XMLFactory

DESIGN_SPACE_FILE = 'choiceSpace.xml'
CODE_MAPPING_FILE = 'choiceMapping.xml'
paramStore = None
designSpace = None

# Corresponds to generates all.
EXPECTED_ALL_TYPES = {
    'Empty':    [Empty1, Empty2, Empty3],
    'NonEmpty': [NonEmpty1, NonEmpty2],
    'Point':
        [Point, DoublePoint, PointWithoutConstructor, PointWithoutAccessors],
}

# Corresponds to generates only.
EXPECTED_ONLY_TYPES = {
    'Empty.E1':         [Empty1],
    'NonEmpty.NE1':     [NonEmpty1],
    'NonEmpty.NE1.Obj': [int],
    # Repeating all-tests:
    'Empty':            [Empty1, Empty2, Empty3],
    'NonEmpty':         [NonEmpty1, NonEmpty2],
    'Point':
        [Point, DoublePoint, PointWithoutConstructor, PointWithoutAccessors],
}

class TestChoice(unittest.TestCase):

    def setUp(self):
        global paramStore, designSpace
        mappingFactory = PresetCodeMappingFactory.getCodeMapping
        paramStoreFactory = PresetParamStoreFactory.getParamStore
        designSpaceFactory = PresetDesignSpaceFactory.getDesignSpace

        mapping = mappingFactory(CODE_MAPPING_FILE)
        paramStore = paramStoreFactory(DESIGN_SPACE_FILE, mapping)

        designSpace = designSpaceFactory(DESIGN_SPACE_FILE)


    # ----- Batch tests -----
    def testGetOnlyExpectedTypesFromDesignSpace(self):
        for (k,v) in EXPECTED_ONLY_TYPES.items():
            assertGeneratesOnly(lambda: type(designSpace.next(k)), v)

    def testGetAllExpectedTypesFromDesignSpace(self):
        for (k,v) in EXPECTED_ALL_TYPES.items():
            assertGeneratesAll(lambda: type(designSpace.next(k)), v)
    # ----- Batch tests -----


    def testGetNonEmptyObjectFromDesignSpaceShouldVary(self):
        f = lambda: designSpace.next('NonEmpty').getObject()
        assertVariability(f)

    def testGetNE1FromDesignSpaceShouldBeInt(self):
        f = lambda: type(designSpace.next('NonEmpty.NE1').getObject())
        assertGeneratesOnly(f, [int])


    # Point.X is "fixed". While DoublePoint reinterprets the value and would
    # return an X value of 2 instead of 1, that is irrelevant. Point.X is
    # still defined as always being 1, so it is always 1.
    def testGetPointXFromDesignSpaceShouldBeConstant(self):
        f = lambda: designSpace.next('Point.X')
        assertGeneratesOnly(f, [1])

    # While Point may be initialized using the DoublePoint subtype, which will
    # then inherit the nested X parameter from Point, there does not exist any
    # parameter named 'Point.Double.X'. So trying to generate a value for it
    # should return None.
    def testGetDoubleXFromDesignSpaceShouldBeNone(self):
        f = lambda: designSpace.next('Point.Double.X')
        assertGeneratesOnly(f, [None])

    # Explicitly getting one of the choices.
    def testGetPointDoubleFromDesignSpaceShouldAlwaysReturnDouble(self):
        f = lambda: designSpace.next('Point.Double')
        self.assertEqual(4, f().getY()) # Kinda redundant.
        assertGeneratesOnly(f, [DoublePoint(1, 2)])


    def testGetPointFromDesign(self):
        # For some reason, the preset factory does not work!
        # Initialization of Shape fails, but the design spaces are equal,
        # according to test_factories.
        #space = PresetDesignSpaceFactory.getDesignSpace(DESIGN_SPACE_FILE)
        space = XMLFactory.getDesignSpace(DESIGN_SPACE_FILE)
        f = lambda: type(space.nextDesign('Design').getValue('Point'))
        expected = [
            Point, DoublePoint, PointWithoutConstructor, PointWithoutAccessors
        ]
        assertGeneratesOnly(f, expected)

    def testGetPointFromDesignShouldReturnAllValidTypes(self):
        space = XMLFactory.getDesignSpace(DESIGN_SPACE_FILE)
        f = lambda: type(space.nextDesign('Design').getValue('Point'))
        expected = [
            Point, DoublePoint, PointWithoutConstructor, PointWithoutAccessors
        ]
        assertGeneratesAll(f, expected)

    # The behavior asserted by this test makes sense, but it contradicts
    # the current implementation of InPUT. Future specifications will have
    # to determine which behavior is correct.
    # It is tagged as an expected failure rather, than "fixed" to conform to
    # the current behavior, because it seems likely that it will change.
    #
    # A random Point is created, and when the type is DoublePoint the
    # X value is indeed different (2 instead of 1).
    # However, design.getValue('Point.X') accesses the original Point.X
    # parameter value, not the X value of the instantiated object. In other
    # words, the getter is not invoked. Therefore X does not vary.
    @unittest.expectedFailure
    def testGetPointXFromDesignShouldVary(self):
        space = XMLFactory.getDesignSpace(DESIGN_SPACE_FILE)
        f = lambda: space.nextDesign('Design').getValue('Point.X')
        assertVariability(f)

    def testTheSameDesignShouldAlwaysReturnTheSameValue(self):
        space = XMLFactory.getDesignSpace(DESIGN_SPACE_FILE)
        design = space.nextDesign('Design')
        f = lambda: design.getValue('Point')
        assertConstancy(f)

    def testGetShapeFromDesign(self):
        space = XMLFactory.getDesignSpace(DESIGN_SPACE_FILE)
        design = space.nextDesign('Design')
        f = lambda: space.nextDesign('Design').getValue('Shape')
        # These nested parameters all have constant values, so only the
        # choice of Square or Rectangle varies.
        point = space.next('Shape.Point')
        side = space.next('Shape.Square.Side')
        width = space.next('Shape.Rectangle.Width')
        height = space.next('Shape.Rectangle.Height')
        expected = [Square(point, side), Rectangle(point, width, height)]
        assertGeneratesAll(f, expected)


    # SChoices aren't "real" parameters. They do not exist in the design.
    def testGettingAnySChoiceFromDesignShouldYieldNone(self):
        space = XMLFactory.getDesignSpace(DESIGN_SPACE_FILE)
        design = space.nextDesign('Design')
        choices = [
            'Empty.E1', 'Empty.E2', 'Empty.E3', 'NonEmpty.NE1', 'NonEmpty.NE2',
            'Point.Double', 'Point.NoConstructor', 'Point.NoAccessors',
            'Shape.Square', 'Shape.Rectangle',
        ]
        for paramId in choices:
            self.assertIsNone(design.getValue(paramId))


if __name__ == '__main__':
    unittest.main()
