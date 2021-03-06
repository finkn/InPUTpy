"""
:copyright: (c) 2013 by Christoffer Fink.
:license: MIT. See LICENSE for details.
"""
import unittest
import inputpy.generators as generator
import test.tools as tools
from inputpy.q import *
from inputpy.param import getParameter, paramFactory
from test.types.simple import EmptyClass
from test.types.geo import Point
from inputpy.mapping import Mapping, CodeMapping, NULL_CODE_MAPPING

class TestGenerators(unittest.TestCase):

    def testGeneratorRandomness(self):
        params = (
            getParameter('A', NPARAM, INTEGER, inclMin=1, inclMax=10),
            getParameter('A', NPARAM, FLOAT, inclMin=1, inclMax=10),
            getParameter('A', NPARAM, BOOLEAN),
        )
        for p in params:
            self.checkGeneratorRandomness(p)

    def testGeneratorReturnType(self):
        params = (
            (getParameter('A', NPARAM, SHORT, inclMin=1, inclMax=10), int),
            (getParameter('A', NPARAM, INTEGER, inclMin=1, inclMax=10), int),
            (getParameter('A', NPARAM, LONG, inclMin=1, inclMax=10), int),
            (getParameter('A', NPARAM, FLOAT, inclMin=1, inclMax=10), float),
            (getParameter('A', NPARAM, DOUBLE, inclMin=1, inclMax=10), float),
            (getParameter('A', NPARAM, DECIMAL, inclMin=1, inclMax=10), float),
            (getParameter('A', NPARAM, BOOLEAN, inclMin=1, inclMax=10), bool),
        )
        # Go through parameter-type pairs.
        for pair in params:
            self.assertIsInstance(generator.nextValue(pair[0]), pair[1])

    # Note that this test does not include a float parameter with an
    # exclusive limit.
    def testGeneratorRange(self):
        tests = (
            {
                'param': getParameter('A', NPARAM, SHORT,
                            inclMin=-2, inclMax=0),
                'inclMin': (-2,), 'inclMax': (0,),
            },
            {
                'param': getParameter('A', NPARAM, LONG, exclMin=1, exclMax=4),
                'inclMin': (2,), 'inclMax': (3,),
            },
            {
                'param': getParameter('A', NPARAM, INTEGER,
                            inclMin=(1,2,), exclMax=(2,4,)),
                'inclMin': (1,2,), 'inclMax': (1,3,),
            },
            {
                'param': getParameter('A', NPARAM, FLOAT,
                            inclMin=0.5, inclMax=0.6),
                'inclMin': (0.5,), 'inclMax': (0.6,),
            },
            {
                'param': getParameter('A', NPARAM, BOOLEAN),
                'inclMin': (0,), 'inclMax': (1,),
            },
            {
                'param': getParameter('A', NPARAM, DOUBLE,
                            inclMin=('Math.cos(Math.pi)','.5/2 + B'),
                            inclMax=(.9,'Math.sqrt(16) + B')),
                'dep': {'B': 3},
                'inclMin': (-1.0,3.25,), 'inclMax': (.9,7,),
            },
        )
        for kwarg in tests:
            self.checkRange(**kwarg)

    def testNextArray(self):
        param = getParameter('A', NPARAM, INTEGER, inclMin=1, inclMax=1)
        sizes = (2, 3, 4)
        expected = [
            [
                [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1],
            ],
            [
                [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1],
            ],
        ]
        result = generator.nextArray(param, sizes)
        self.checkDimensions(result, sizes)
        self.assertEqual(expected, result)

    def testNextArrayWithFixedParameter(self):
        param = getParameter('A', NPARAM, INTEGER,
            inclMin=1, inclMax=1, fixed=2)
        sizes = (2, 3)
        expected = [
            [2, 2, 2],
            [2, 2, 2],
        ]
        result = generator.nextArray(param, sizes)
        self.checkDimensions(result, sizes)
        self.assertEqual(expected, result)

    def testNextValueWithArrayParameter(self):
        params = (
            getParameter('A', NPARAM, SHORT+'[2][3]', inclMin=1, inclMax=1),
            getParameter('A', NPARAM, INTEGER+'[2][3]', inclMin=2, inclMax=2),
            getParameter('A', NPARAM, FLOAT+'[2][3]', inclMin=1, inclMax=1,
                fixed=3.5),
            getParameter('A', NPARAM, BOOLEAN+'[2][3]', fixed='true'),
        )
        sizes = (2, 3)
        for p in params:
            result = generator.nextValue(p)
            self.checkDimensions(result, sizes)

    def testSParamGenerator(self):
        dep = {'X': 2, 'Y': 3}
        nested = [
            getParameter('X', NPARAM, INTEGER, inclMin=2, inclMax=2,
                parentId='Point'),
            getParameter('Y', NPARAM, INTEGER, inclMin=3, inclMax=3,
                parentId='Point'),
        ]
        pointMapping = Mapping('Point', 'test.types.geo.Point', 'X Y')
        emptyMapping = Mapping('Empty', 'test.types.simple.EmptyClass')
        pointParam = getParameter('Point', SPARAM, nested=nested, mapping=pointMapping)
        emptyParam = getParameter('Empty', SPARAM, nested=[], mapping=emptyMapping)
        self.assertIsNotNone(emptyParam.getMapping())
        self.assertIsNotNone(pointParam.getMapping())

        expectedPoint = Point(2, 3)
        expectedEmpty = EmptyClass()
        empty = generator.nextValue(emptyParam)
        point = generator.nextValue(pointParam, dep)
        self.assertIsInstance(empty, EmptyClass)
        self.assertIsInstance(point, Point)
        self.assertEqual(2, point.getX())
        self.assertEqual(3, point.getY())

    def testSParamStringGenerator(self):
        cm = NULL_CODE_MAPPING
        args = {ID_ATTR: 'some string', TAG: SPARAM, TYPE_ATTR: STRING}
        param = paramFactory(args, cm)
        self.assertEqual('some string', generator.nextValue(param))

    def checkDimensions(self, array, sizes):
        tools.assertMatchingArrayDimensions(sizes, array)

    def checkGeneratorRandomness(self, param, dep={}, iterations=10):
        f = lambda: generator.nextValue(param, dep)
        tools.assertVariability(f)

    # This test always assumes that the range is inclusive.
    def checkRange(self, inclMin, inclMax, param, dep={}, iterations=10):
        self.assertTrue(iterations > 1, msg='1 iteration makes no sense!')
        for i in range(iterations):
            value = generator.nextValue(param, dep)
            result = [
                minLimit <= value <= maxLimit
                for (minLimit, maxLimit) in list(zip(inclMin, inclMax))
            ]
            msg='%s did not match any of the ranges' % (value,)
            self.assertTrue(any(result), msg=msg)


if __name__ == '__main__':
    unittest.main()
