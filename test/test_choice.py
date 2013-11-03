"""
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

class TestChoice(unittest.TestCase):

    def setUp(self):
        global paramStore, designSpace
        mappingFactory = PresetCodeMappingFactory.getCodeMapping
        paramStoreFactory = PresetParamStoreFactory.getParamStore
        designSpaceFactory = PresetDesignSpaceFactory.getDesignSpace

        mapping = mappingFactory(CODE_MAPPING_FILE)
        paramStore = paramStoreFactory(DESIGN_SPACE_FILE, mapping)

        designSpace = designSpaceFactory(DESIGN_SPACE_FILE)


    def testGetPointFromDesignSpaceShouldReturnOnlyValidTypes(self):
        f = lambda: type(designSpace.next('Point'))
        # The generated points are expected to be of these types.
        expected = [
            Point, DoublePoint, PointWithoutConstructor, PointWithoutAccessors
        ]
        assertGeneratesOnly(f, expected)

    # This test implicitly asserts variability as well.
    def testGetPointFromDesignSpaceShouldReturnAllValidTypes(self):
        f = lambda: type(designSpace.next('Point'))
        expected = [
            Point, DoublePoint, PointWithoutConstructor, PointWithoutAccessors
        ]
        assertGeneratesAll(f, expected)

    # Point.X is "fixed". While DoublePoint reinterprets the value and would
    # return an X value of 2 instead of 1, that is irrelevant. Point.X is
    # still defined as always being 1, so it is always 1.
    def testGetPointXFromDesignSpaceShouldBeConstant(self):
        f = lambda: designSpace.next('Point.X')
        self.assertEqual(1, f())
        assertConstancy(f)

    # While Point may be initialized using the DoublePoint subtype, which will
    # then inherit the nested X parameter from Point, there does not exist any
    # parameter named 'Point.Double.X'. So trying to generate a value for it
    # should return None.
    def testGetDoubleXFromDesignSpaceShouldBeNone(self):
        f = lambda: designSpace.next('Point.Double.X')
        self.assertIsNone(f())
        assertConstancy(f)


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

    # A random Point is created, and when the type is DoublePoint, then the
    # X value is indeed different (2 instead of 1). However, it seems that
    # design.getValue('Point.X') accesses the original Point.X value, and not
    # the X value that was used to instantiate the actual Point object.
    @unittest.expectedFailure
    def testGetDoubleXFromDesignShouldBeNone(self):
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


if __name__ == '__main__':
    unittest.main()
