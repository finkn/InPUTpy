"""
:copyright: (c) 2013 by Christoffer Fink.
:license: MIT. See LICENSE for details.
"""
import unittest
from inputpy.designspace import DesignSpace
from inputpy.mapping import DUMMY_MAPPING
from inputpy.param import *
from inputpy.q import *
from test.factories import PresetCodeMappingFactory

class TestParam(unittest.TestCase):

    EXPRESSION_TESTS = {
        'A+B': ('A', 'B',),
        'A + B': ('A', 'B',),
        'A + B-C/ D *E': ('A', 'B', 'C', 'D', 'E',),
        'Math.log(A)': ('A',),
        'A+ Math.sqrt( B / C )': ('A', 'B', 'C',),
        ' 2 * ( (( A+B ) - (C) ) ) + A': ('A', 'B', 'C',),
        ' SomeParam + AnotherParam ': ('SomeParam', 'AnotherParam',),
        'A * -.3': ('A',),
        '1 + 2 - Math.cos(0.0)': (),
        'A.X + B.Y': ('A.X', 'B.Y',),
        'Math.sqrt(A.X + Math.log(B.Y))': ('A.X', 'B.Y',),
    }

    def testGetId(self):
        param = NParam('A', INTEGER)
        result = param.getId()
        expected = 'A'
        msg = 'The parameter ID should be "A"'
        self.assertEqual(expected, result, msg=msg)

    def testGetType(self):
        param = NParam('A', INTEGER)
        result = param.getType()
        expected = INTEGER
        msg = 'Parameter should be "%s"' % (expected)
        self.assertEqual(expected, result, msg=msg)

    def testGetTag(self):
        param = NParam('A', INTEGER)
        result = param.getTag()
        expected = NPARAM
        msg = 'Parameter should be "%s"' % (expected)
        self.assertEqual(expected, result, msg=msg)

    def testCreateParamWithMultipleRanges(self):
        NParam('A', 'integer', inclMin=(1,5), inclMax=(2,7))
        NParam('A', 'integer', inclMin=('1','5','-5'), inclMax=(2,7,5))
        NParam('A', 'float', exclMin=('.5','5.0','-5'), exclMax=(.9,7,5))
        NParam('A', 'float',
            inclMin=('Math.cos(Math.pi)','.5/2 + B'),
            inclMax=(.9,'Math.sqrt(16) + B'))

    def testParamLimits(self):
        # No limits.
        self.checkLimits()
        # Try setting only one of the limits to inclusive and exclusive.
        self.checkLimits(iMin=1)
        self.checkLimits(eMin=1)
        self.checkLimits(iMax=1)
        self.checkLimits(eMax=1)
        # Try setting both limits, using all combinations of incl/excl.
        self.checkLimits(iMin=1, iMax=10)
        self.checkLimits(eMin=1, eMax=10)
        self.checkLimits(iMin=1, eMax=10)
        self.checkLimits(eMin=1, iMax=10)
        # Setting multiple ranges.
        self.checkLimits(iMin=(1), eMax=(10))
        self.checkLimits(eMin=(1,2), iMax=(3,10))
        # Multiple ranges with mismatching end points.
        self.checkLimits(eMin=(1,2), iMax=(3,10,5))
        self.checkLimits(eMin=(1,2,-5), iMax=(3,10))

    def testCreatingParamWithSingleLimitStillReturnsMultiLimit(self):
        param = NParam('A', INTEGER, inclMin=1, inclMax=2)
        self.assertIsNotNone(iter(param.getMin()))

    def testGetIntervalsWithSingleInterval(self):
        param = NParam('A', INTEGER, inclMin=1, inclMax=3)
        self.assertEqual(1, len(param.getIntervals()))

    def testgetIntervalsWithMultipleIntervals(self):
        param = NParam('A', INTEGER, inclMin=(1,1,2), inclMax=(3,4))
        self.assertEqual(3, len(param.getIntervals()))

    def testNoneIdShouldNotRaiseError(self):
        param = NParam(None, INTEGER)
        self.assertIsNotNone(param.getId())

    def testNoneTypeShouldRaiseError(self):
        with self.assertRaises(ValueError):
            param = NParam('A', None)

    def testMultipleMinLimitsShouldRaiseError(self):
        with self.assertRaises(ValueError):
            param = NParam('A', INTEGER, inclMin=1, exclMin=10)

    def testMultipleMaxLimitsShouldRaiseError(self):
        with self.assertRaises(ValueError):
            param = NParam('A', INTEGER, inclMax=1, exclMax=10)

    def testParamWithoutLimitsIsNotDependent(self):
        param = NParam('A', INTEGER)
        self.assertFalse(param.isDependent())

    def testParamWithIntegerLimitIsNotDependent(self):
        param = NParam('A', INTEGER, inclMin=1, exclMax=3)
        self.assertFalse(param.isDependent())

    def testParamWithParameterReferenceIsDependent(self):
        param = NParam('A', INTEGER, inclMin='B', exclMax='B + C')
        self.assertTrue(param.isDependent())

    def testDependencies(self):
        import random
        # The tests map an expression to a sequence of referenced parameters.
        # This means that the values are the expected dependees for a
        # parameter that was created with the expression as a limit.
        tests = self.EXPRESSION_TESTS
        keys = tests.keys()
        keyList = list(keys)
        for key in keys:
            minExp = key
            maxExp = random.choice(keyList)
            expected = tests[minExp] + tests[maxExp]
            param = NParam('A', INTEGER, inclMin=minExp, inclMax=maxExp)
            dependees = param.getDependees()
            self.assertCountEqual(expected, dependees)

    def testIndependentParameterWithExpressionShouldBeEvaluated(self):
        param = NParam('A', INTEGER, inclMin='1', exclMax='1 + 2')
        self.assertFalse(param.isDependent())
        self.assertEqual((1,), param.getMin())
        self.assertEqual((3,), param.getMax())

    def testIdenpendentParameterWithMoreComplexExpression(self):
        # 2.0
        eMin = 'Math.sqrt(Math.ceil(2.1) + Math.cos(0.0))'
        # 5.0
        iMax = 'Math.log(Math.exp(10)) / Math.floor(2.9)'
        param = NParam('A', INTEGER, exclMin=eMin, inclMax=iMax)
        self.assertFalse(param.isDependent())
        # Should probably really expect 2 and 5 here.
        self.assertEqual((2.0,), param.getMin())
        self.assertEqual((5.0,), param.getMax())

    def testDependentParameterWithSimpleDependency(self):
        param = NParam('A', INTEGER, inclMin='B')
        self.assertTrue(param.isDependent())

    def testCreatingFixedParameter(self):
        param = NParam('A', INTEGER, fixed=3)
        self.assertTrue(param.isFixed())

    def testUnfixParameter(self):
        param = NParam('A', INTEGER, fixed=3)
        param.setFixed(None)
        self.assertFalse(param.isFixed())

    def testFixAndUnfixExistingParameter(self):
        param = NParam('A', INTEGER)
        self.assertFalse(param.isFixed())
        param.setFixed(3)
        self.assertTrue(param.isFixed())
        param.setFixed(None)
        self.assertFalse(param.isFixed())

    def testIsArray(self):
        params = (
            getParameter('A', NPARAM, SHORT),
            getParameter('A', NPARAM, INTEGER),
            getParameter('A', NPARAM, BOOLEAN),
            getParameter('A', NPARAM, FLOAT),
        )
        arrays = (
            getParameter('A', NPARAM, SHORT + '[]'),
            getParameter('A', NPARAM, INTEGER + '[2]'),
            getParameter('A', NPARAM, BOOLEAN + '[][2]'),
            getParameter('A', NPARAM, FLOAT + '[2][]'),
            getParameter('A', NPARAM, LONG + '[2][1][3]'),
        )
        for p in params:
            self.assertNotEqual(ARRAY, p.getType())
        for p in arrays:
            self.assertEqual(ARRAY, p.getType())
            self.assertIsNotNone(p.getParameter())
            self.assertIsNotNone(p.getSize())

    def testGetParam(self):
        reference = NParam('A', INTEGER, inclMin=3, fixed=4)
        param = getParameter('A', NPARAM, INTEGER, inclMin=3, fixed=4)
        self.compareParameters(reference, param)

        t = INTEGER + '[2]'
        arrayParam = getParameter('A', NPARAM, t, inclMin=3, fixed=4)
        self.assertEqual(2, arrayParam.getSize())
        self.compareParameters(param, arrayParam.getParameter())

        t = INTEGER + '[2][2]'
        arrayParam2 = getParameter('A', NPARAM, t, inclMin=3, fixed=4)
        self.compareParameters(arrayParam, arrayParam2.getParameter())

    def testEqual(self):
        param1 = getParameter('A', NPARAM, INTEGER)
        param2 = getParameter('A', NPARAM, INTEGER)
        self.assertEqual(param1, param2)
        param2 = getParameter('A', NPARAM, INTEGER, inclMin=3)
        self.assertNotEqual(param1, param2)
        param1 = getParameter('A', NPARAM, INTEGER, inclMin=3)
        self.assertEqual(param1, param2)

    def testEqualArrays(self):
        param1 = getParameter('A', NPARAM, INTEGER + '[2]')
        param2 = getParameter('A', NPARAM, INTEGER + '[2]')
        self.assertEqual(param1, param2)
        param2 = getParameter('A', NPARAM, INTEGER + '[3]')
        self.assertNotEqual(param1, param2)
        param1 = getParameter('A', NPARAM, INTEGER + '[3]', inclMax=3)
        self.assertNotEqual(param1, param2)
        param2 = getParameter('A', NPARAM, INTEGER + '[3]', inclMax=3)
        self.assertEqual(param1, param2)

    def testSParamWithoutNestedParameters(self):
        m = DUMMY_MAPPING
        param = getParameter('A', SPARAM, nested=(), mapping=m)
        self.assertEqual('A', param.getId())
        self.assertEqual(SPARAM, param.getTag())
        self.assertEqual((), param.getNestedParameters())

    def testSParamWithNestedParameters(self):
        # A could be a Point object for example, with X and Y
        # NParam nested parameters.
        m = DUMMY_MAPPING
        x = getParameter('X', NPARAM, INTEGER, parentId='A')
        y = getParameter('Y', NPARAM, INTEGER, parentId='A')
        param = getParameter('A', SPARAM, nested=(x, y), mapping=m)
        self.assertEqual('A', param.getId())
        self.assertEqual(SPARAM, param.getTag())
        self.assertEqual((x, y), param.getNestedParameters())
        self.assertCountEqual(('X', 'Y'), param.getDependees())

    def testSParamWithMultipleNestingLevels(self):
        m = DUMMY_MAPPING
        x = getParameter('X', NPARAM, INTEGER, parentId='B.A')
        y1 = getParameter('Y', NPARAM, INTEGER, parentId='B.A')
        y2 = getParameter('Y', NPARAM, INTEGER, parentId='B')
        a = getParameter('A', SPARAM, nested=(x, y1), parentId='B', mapping=m)
        b = getParameter('B', SPARAM, nested=(a, y2), mapping=m)
        self.assertCountEqual(('A', 'Y'), b.getDependees())

    def testAbsolutePath(self):
        x = getParameter('X', NPARAM, INTEGER, parentId='A.B')
        y = getParameter('Y', NPARAM, INTEGER, parentId='A.B')
        self.assertEqual('A.B.X', x.getId())
        self.assertEqual('A.B.Y', y.getId())

    def testParamFactory(self):
        paramArgs = {
            'X': {ID_ATTR: 'X', TYPE_ATTR: INTEGER, INCL_MIN: '0', },
            'Y': {ID_ATTR: 'Y', TYPE_ATTR: INTEGER, INCL_MAX: '1', },
            'P1': {ID_ATTR: 'P1', TYPE_ATTR: SPARAM, NESTED: (
                    {ID_ATTR: 'X', TYPE_ATTR: INTEGER, EXCL_MIN: '2', },
                    {ID_ATTR: 'Y', TYPE_ATTR: INTEGER, EXCL_MAX: '3', },
                ),
            },
        }
        m = PresetCodeMappingFactory.getCodeMapping('triangleMapping.xml')
        results = {k: paramFactory(v, m) for (k,v) in paramArgs.items()}
        self.assertCountEqual(paramArgs.keys(), results.keys())
        p = results['P1']
        self.assertEqual(2, len(p.getNestedParameters()))

    def compareParameters(self, reference, param):
        self.assertEqual(reference.getId(), param.getId())
        self.assertEqual(reference.getType(), param.getType())
        self.assertEqual(reference.getMin(), param.getMin())
        self.assertEqual(reference.getMax(), param.getMax())
        self.assertEqual(reference.getFixedValue(), param.getFixedValue())
        if param.getType() == ARRAY:
            refChild = reference.getParameter()
            paramChild = param.getParameter()
            self.compareParameters(refChild, paramChild)

    def checkLimits(self, pa=None, iMin=None, eMin=None, iMax=None, eMax=None):
        args = pa or ('A', INTEGER, NPARAM)
        kwargs = {}
        if iMin is not None:
            kwargs[INCL_MIN] = iMin
        if eMin is not None:
            kwargs[EXCL_MIN] = eMin
        if iMax is not None:
            kwargs[INCL_MAX] = iMax
        if eMax is not None:
            kwargs[EXCL_MAX] = eMax

        # Create the parameter based on the arguments.
        param = NParam(*args, **kwargs)

        # Check that the ranges were padded.
        self.assertEqual(len(param.getMin()), len(param.getMax()))

        if eMin is not None:
            self.assertTrue(param.isMinExclusive())
        if eMax is not None:
            self.assertTrue(param.isMaxExclusive())


if __name__ == '__main__':
    unittest.main()
