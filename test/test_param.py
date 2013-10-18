"""
:copyright: (c) 2013 by Christoffer Fink.
:license: MIT. See LICENSE for details.
"""
import unittest
from inputpy.designspace import DesignSpace
from inputpy.param import *
from inputpy.q import *
from test.tools import PresetCodeMappingFactory

class TestParam(unittest.TestCase):

    EXPRESSION_TESTS = {
        'A+B': ('A', 'B',),
        'A + B': ('A', 'B',),
        'A + B-C/ D *E': ('A', 'B', 'C', 'D', 'E',),
        'Math.log(A)': ('A',),
        'A+ Math.sqr( B / C )': ('A', 'B', 'C',),
        ' 2 * ( (( A+B ) - (C) ) ) + A': ('A', 'B', 'C',),
        ' SomeParam + AnotherParam ': ('SomeParam', 'AnotherParam',),
        'A * -.3': ('A',),
        '1 + 2 - Math.cos(0.0)': (),
    }

    def testCreateBasicParam(self):
        param = NParam('A', 'integer')

    def testGetId(self):
        param = NParam('A', 'integer')
        pId = param.getId()
        self.assertEqual('A', pId, msg='The parameter ID should be "A"')

    def testGetType(self):
        param = NParam('A', 'integer')
        pType = param.getType()
        self.assertEqual('integer', pType, msg='Parameter should be "integer"')

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
        param = NParam('A', 'integer', inclMin=1, inclMax=2)
        self.assertIsNotNone(iter(param.getMin()))

    def testNoneIdShouldNotRaiseError(self):
        param = NParam(None, 'integer')
        self.assertIsNotNone(param.getId())

    def testNoneTypeShouldRaiseError(self):
        with self.assertRaises(ValueError):
            param = NParam('A', None)

    def testMultipleMinLimitsShouldRaiseError(self):
        with self.assertRaises(ValueError):
            param = NParam('A', 'integer', inclMin=1, exclMin=10)

    def testMultipleMaxLimitsShouldRaiseError(self):
        with self.assertRaises(ValueError):
            param = NParam('A', 'integer', inclMax=1, exclMax=10)

    def testParamWithoutLimitsIsNotDependent(self):
        param = NParam('A', 'integer')
        self.assertFalse(param.isDependent())

    def testParamWithIntegerLimitIsNotDependent(self):
        param = NParam('A', 'integer', inclMin=1, exclMax=3)
        self.assertFalse(param.isDependent())

    def testParamWithParameterReferenceIsDependent(self):
        param = NParam('A', 'integer', inclMin='B', exclMax='B + C')
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
            param = NParam('A', 'integer', inclMin=minExp, inclMax=maxExp)
            dependees = param.getDependees()
            self.assertCountEqual(expected, dependees)

    def testIndependentParameterWithExpressionShouldBeEvaluated(self):
        param = NParam('A', 'integer', inclMin='1', exclMax='1 + 2')
        self.assertFalse(param.isDependent())
        self.assertEqual((1,), param.getMin())
        self.assertEqual((3,), param.getMax())

    def testIdenpendentParameterWithMoreComplexExpression(self):
        # 2.0
        eMin = 'Math.sqrt(Math.ceil(2.1) + Math.cos(0.0))'
        # 5.0
        iMax = 'Math.log(Math.exp(10)) / Math.floor(2.9)'
        param = NParam('A', 'integer', exclMin=eMin, inclMax=iMax)
        self.assertFalse(param.isDependent())
        # Should probably really expect 2 and 5 here.
        self.assertEqual((2.0,), param.getMin())
        self.assertEqual((5.0,), param.getMax())

    def testDependentParameterWithSimpleDependency(self):
        param = NParam('A', 'integer', inclMin='B')
        self.assertTrue(param.isDependent())

    def testCreatingFixedParameter(self):
        param = NParam('A', 'integer', fixed=3)
        self.assertTrue(param.isFixed())

    def testUnfixParameter(self):
        param = NParam('A', 'integer', fixed=3)
        param.setFixed(None)
        self.assertFalse(param.isFixed())

    def testFixAndUnfixExistingParameter(self):
        param = NParam('A', 'integer')
        self.assertFalse(param.isFixed())
        param.setFixed(3)
        self.assertTrue(param.isFixed())
        param.setFixed(None)
        self.assertFalse(param.isFixed())

    def testIsArray(self):
        params = (
            getParameter('A', 'short'),
            getParameter('A', 'integer'),
            getParameter('A', 'boolean'),
            getParameter('A', 'float'),
        )
        arrays = (
            getParameter('A', 'short[]'),
            getParameter('A', 'integer[2]'),
            getParameter('A', 'boolean[][2]'),
            getParameter('A', 'float[2][]'),
            getParameter('A', 'long[2][1][3]'),
        )
        for p in params:
            self.assertNotEqual('array', p.getType())
        for p in arrays:
            self.assertEqual('array', p.getType())
            self.assertIsNotNone((), p.getParameter())
            self.assertIsNotNone((), p.getSize())

    def testGetParam(self):
        reference = NParam('A', 'integer', inclMin=3, fixed=4)
        param = getParameter('A', 'integer', inclMin=3, fixed=4)
        self.compareParameters(reference, param)

        arrayParam = getParameter('A', 'integer[2]', inclMin=3, fixed=4)
        self.assertEqual(2, arrayParam.getSize())
        self.compareParameters(param, arrayParam.getParameter())

        arrayParam2 = getParameter('A', 'integer[2][2]', inclMin=3, fixed=4)
        self.compareParameters(arrayParam, arrayParam2.getParameter())

    def testEqual(self):
        param1 = getParameter('A', 'integer')
        param2 = getParameter('A', 'integer')
        self.assertEqual(param1, param2)
        param2 = getParameter('A', 'integer', inclMin=3)
        self.assertNotEqual(param1, param2)
        param1 = getParameter('A', 'integer', inclMin=3)
        self.assertEqual(param1, param2)

    def testEqualArrays(self):
        param1 = getParameter('A', 'integer[2]')
        param2 = getParameter('A', 'integer[2]')
        self.assertEqual(param1, param2)
        param2 = getParameter('A', 'integer[3]')
        self.assertNotEqual(param1, param2)
        param1 = getParameter('A', 'integer[3]', inclMax=3)
        self.assertNotEqual(param1, param2)
        param2 = getParameter('A', 'integer[3]', inclMax=3)
        self.assertEqual(param1, param2)

    def testSParamWithoutNestedParameters(self):
        m = 'dummy mapping' # Looks like I'm being very naughty.
        param = getParameter('A', 'SParam', nested=(), mapping=m)
        self.assertEqual('A', param.getId())
        self.assertEqual('SParam', param.getType())
        self.assertEqual((), param.getNestedParameters())

    def testSParamWithNestedParameters(self):
        # A could be a Point object for example, with X and Y
        # NParam nested parameters.
        m = 'dummy mapping'
        x = getParameter('X', 'integer', parentId='A')
        y = getParameter('Y', 'integer', parentId='A')
        param = getParameter('A', 'SParam', nested=(x, y), mapping=m)
        self.assertEqual('A', param.getId())
        self.assertEqual('SParam', param.getType())
        self.assertEqual((x, y), param.getNestedParameters())
        self.assertCountEqual(('X', 'Y'), param.getDependees())

    def testSParamWithMultipleNestingLevels(self):
        m = 'dummy mapping'
        x = getParameter('X', 'integer', parentId='B.A')
        y1 = getParameter('Y', 'integer', parentId='B.A')
        y2 = getParameter('Y', 'integer', parentId='B')
        a = getParameter('A', 'SParam', nested=(x, y1), parentId='B', mapping=m)
        b = getParameter('B', 'SParam', nested=(a, y2), mapping=m)
        self.assertCountEqual(('A', 'Y'), b.getDependees())

    def testAbsolutePath(self):
        x = getParameter('X', 'integer', parentId='A.B')
        y = getParameter('Y', 'integer', parentId='A.B')
        self.assertEqual('A.B.X', x.getId())
        self.assertEqual('A.B.Y', y.getId())

    # Note that this test does not include code mappings!
    def testParamFactory(self):
        paramArgs = {
            'X': {ID_ATTR: 'X', TYPE_ATTR: 'integer', INCL_MIN: '0', },
            'Y': {ID_ATTR: 'Y', TYPE_ATTR: 'integer', INCL_MAX: '1', },
            'P1': {ID_ATTR: 'P1', TYPE_ATTR: SPARAM, 'nested': (
                    {ID_ATTR: 'X', TYPE_ATTR: 'integer', EXCL_MIN: '2', },
                    {ID_ATTR: 'Y', TYPE_ATTR: 'integer', EXCL_MAX: '3', },
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
        if param.getType() == 'array':
            refChild = reference.getParameter()
            paramChild = param.getParameter()
            self.compareParameters(refChild, paramChild)

    def checkLimits(self, pa=None, iMin=None, eMin=None, iMax=None, eMax=None):
        args = pa or ('A', 'integer')
        kwargs = {}
        if iMin is not None:
            kwargs['inclMin'] = iMin
        if eMin is not None:
            kwargs['exclMin'] = eMin
        if iMax is not None:
            kwargs['inclMax'] = iMax
        if eMax is not None:
            kwargs['exclMax'] = eMax

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
