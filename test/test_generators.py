"""
:copyright: (c) 2013 by Christoffer Fink.
:license: MIT. See LICENSE for details.
"""
import unittest
import inputpy.generators as generator
from inputpy.q import SHORT, INTEGER, LONG, FLOAT, DOUBLE, DECIMAL, BOOLEAN
from inputpy.q import SPARAM
from inputpy.param import Param, getParameter, paramFactory
from test.types.simple import EmptyClass
from test.types.geo import Point
from inputpy.mapping import Mapping

class TestGenerators(unittest.TestCase):

    def testGeneratorRandomness(self):
        params = (
            Param('A', INTEGER, inclMin=1, inclMax=10),
            Param('A', FLOAT, inclMin=1, inclMax=10),
            Param('A', BOOLEAN),
        )
        for p in params:
            self.checkGeneratorRandomness(p)

    def testGeneratorReturnType(self):
        params = (
            (Param('A', SHORT, inclMin=1, inclMax=10), int),
            (Param('A', INTEGER, inclMin=1, inclMax=10), int),
            (Param('A', LONG, inclMin=1, inclMax=10), int),
            (Param('A', FLOAT, inclMin=1, inclMax=10), float),
            (Param('A', DOUBLE, inclMin=1, inclMax=10), float),
            (Param('A', DECIMAL, inclMin=1, inclMax=10), float),
            (Param('A', BOOLEAN, inclMin=1, inclMax=10), bool),
        )
        # Go through parameter-type pairs.
        for pair in params:
            self.assertIsInstance(generator.nextValue(pair[0]), pair[1])

    # Note that this test does not include a float parameter with an
    # exclusive limit.
    def testGeneratorRange(self):
        tests = (
            {
                'param': Param('A', SHORT, inclMin=-2, inclMax=0),
                'inclMin': (-2,), 'inclMax': (0,),
            },
            {
                'param': Param('A', LONG, exclMin=1, exclMax=4),
                'inclMin': (2,), 'inclMax': (3,),
            },
            {
                'param': Param('A', INTEGER, inclMin=(1,2,), exclMax=(2,4,)),
                'inclMin': (1,2,), 'inclMax': (1,3,),
            },
            {
                'param': Param('A', FLOAT, inclMin=0.5, inclMax=0.6),
                'inclMin': (0.5,), 'inclMax': (0.6,),
            },
            {
                'param': Param('A', BOOLEAN),
                'inclMin': (0,), 'inclMax': (1,),
            },
            {
                'param': Param('A', DOUBLE,
                            inclMin=('Math.cos(Math.pi)','.5/2 + B'),
                            inclMax=(.9,'Math.sqrt(16) + B')),
                'dep': {'B': 3},
                'inclMin': (-1.0,3.25,), 'inclMax': (.9,7,),
            },
        )
        for kwarg in tests:
            self.checkRange(**kwarg)

    def testNextArray(self):
        param = Param('A', INTEGER, inclMin=1, inclMax=1)
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
        param = Param('A', INTEGER, inclMin=1, inclMax=1, fixed=2)
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
            getParameter('A', SHORT+'[2][3]', inclMin=1, inclMax=1),
            getParameter('A', INTEGER+'[2][3]', inclMin=2, inclMax=2),
            getParameter('A', FLOAT+'[2][3]', inclMin=1, inclMax=1, fixed=3.5),
            getParameter('A', BOOLEAN+'[2][3]', fixed='true'),
        )
        sizes = (2, 3)
        for p in params:
            result = generator.nextValue(p)
            self.checkDimensions(result, sizes)

    def testSParamGenerator(self):
        dep = {'X': 2, 'Y': 3}
        nested = [
            getParameter('X', INTEGER, inclMin=2, inclMax=2),
            getParameter('Y', INTEGER, inclMin=3, inclMax=3),
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

    def checkDimensions(self, array, sizes):
        size = sizes[0]
        self.assertEqual(size, len(array))
        if len(sizes) == 1:
            return
        for element in array:
            self.checkDimensions(element, sizes[1:])

    def checkGeneratorRandomness(self, param, dep={}, iterations=10):
        self.assertTrue(iterations > 1, msg='1 iteration makes no sense!')
        values = []
        for i in range(iterations):
            value = generator.nextValue(param, dep)
            if len(values) > 0 and value not in values:
                return
            else:
                values.append(value)
        msg = 'No unique value after %d iterations.' % (iterations)
        self.fail(msg)

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
