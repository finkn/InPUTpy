import unittest
from inputpy.param import Param
from inputpy.param import ParamStore
from inputpy.param import DesignSpace
from inputpy.param import Design
from inputpy.param import getParameter

class TestDesign(unittest.TestCase):
    def testCreateEmptyDesignWithoutId(self):
        design = Design({})
        self.assertIsNotNone(design.getId())

    def testCreateEmptyDesignWithId(self):
        design = Design({}, 'Design')
        self.assertEqual('Design', design.getId())

    def testGetParameterValue(self):
        params = {'A': 43, 'B': 10}
        design = Design(params)
        for key in params.keys():
            value = params[key]
            self.assertEqual(value, design.getValue(key))

    def testCreateDesignFromDesignSpace(self):
        ps = ParamStore()
        ps.addParam(Param('A', 'integer', inclMin=1, inclMax=1))
        ps.addParam(Param('B', 'integer', exclMin=1, exclMax=3))
        space = DesignSpace(ps)
        design = space.nextDesign('Design')
        self.assertEqual(1, design.getValue('A'))
        self.assertEqual(2, design.getValue('B'))
        self.assertEqual('Design', design.getId())

class TestDesignSpace(unittest.TestCase):
    def testCreateEmptyDesignSpaceWithoutId(self):
        space = DesignSpace(None)
        self.assertIsNotNone(space.getId())

    def testCreateEmptyDesignWithId(self):
        space = DesignSpace(None, 'Design Space')
        self.assertEqual('Design Space', space.getId())

    def testGetParamsForEmptyDesign(self):
        space = DesignSpace(ParamStore())
        params = space.getSupportedParamIds()
        self.assertCountEqual(params, ())

    def testAddParams(self):
        param = Param('A', 'integer')
        ps = ParamStore()
        ps.addParam(param)
        ps.addParam(param)
        space = DesignSpace(ps)
        params = space.getSupportedParamIds()
        self.assertCountEqual(params, ('A'))

    def testNext(self):
        param1 = Param('A', 'integer', inclMin=1, inclMax=1)
        param2 = Param('B', 'integer', exclMin=1, exclMax=3)
        ps = ParamStore()
        ps.addParam(param1)
        ps.addParam(param2)
        space = DesignSpace(ps)
        self.assertEqual(1, space.next(param1.getId()))
        self.assertEqual(2, space.next(param2.getId()))

    def testSetFixedInteger(self):
        paramId = 'Y'
        param = Param(paramId, 'integer')
        ps = ParamStore()
        ps.addParam(param)
        space = DesignSpace(ps)
        self.assertFalse(param.isFixed())
        space.setFixed(paramId, 3)
        self.assertTrue(param.isFixed())

    def testSetFixedBoolean(self):
        paramId = 'A'
        param = Param(paramId, 'boolean')
        space = DesignSpace(ParamStore(param))
        self.assertFalse(param.isFixed())
        space.setFixed(paramId, 'true')
        self.assertTrue(param.isFixed())
        self.assertTrue(param.getFixedValue())
        space.setFixed(paramId, 'hello')
        self.assertFalse(param.getFixedValue())
        space.setFixed(paramId, 'false')
        self.assertFalse(param.getFixedValue())

    def testGenerateValueForFixedParameter(self):
        paramId = 'Z'
        param = Param(paramId, 'integer', inclMin=1, inclMax=1)
        ps = ParamStore()
        ps.addParam(param)
        space = DesignSpace(ps)
        self.assertEqual(1, space.next(paramId))
        space.setFixed(paramId, 3)
        self.assertEqual(3, space.next(paramId))
        space.setFixed(paramId, None)
        self.assertEqual(1, space.next(paramId))

    def testSetFixedToExpression(self):
        paramId = 'X'
        ps = ParamStore()
        ps.addParam(Param(paramId, 'integer'))
        space = DesignSpace(ps)
        # 2.0
        exp = 'Math.log(Math.e * Math.cos(Math.sin(Math.pi/2)-1)) + 1'
        space.setFixed(paramId, exp)
        self.assertEqual(2, space.next(paramId))

    def testNextValueForDependentParameter(self):
        ps = ParamStore()
        ps.addParam(Param('A', 'integer', inclMin=3, inclMax='B + C'))
        ps.addParam(Param('B', 'integer', inclMin='C - 5', inclMax=10))
        ps.addParam(Param('C', 'integer', inclMin=5, inclMax=7))
        space = DesignSpace(ps)
        self.assertTrue(3 <= space.next('A') <= 17)
        self.assertTrue(0 <= space.next('B') <= 10)
        self.assertTrue(5 <= space.next('C') <= 7)

    def testCreateDesignFromDesignSpaceWithDependentParameters(self):
        param1 = Param('A', 'integer', inclMin=3, inclMax='B + C')
        param2 = Param('B', 'integer', inclMin='C', inclMax=10)
        param3 = Param('C', 'integer', inclMin=5, inclMax=7)
        space = DesignSpace(ParamStore((param1, param2, param3)))
        design = space.nextDesign()
        a = design.getValue('A')
        b = design.getValue('B')
        c = design.getValue('C')
        self.assertTrue(3 <= design.getValue('A') <= b + c) # max 17
        self.assertTrue(c <= design.getValue('B') <= 10)    # min 5
        self.assertTrue(5 <= design.getValue('C') <= 7)

    def testCreateDesignWithArray(self):
        param = getParameter('A', 'integer[2][2]', fixed=1)
        self.assertEqual('array', param.getType())
        space = DesignSpace(ParamStore(param))
        expected = [[1,1], [1,1]]
        result = space.next('A')
        self.assertEqual(expected, result)


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
        param = Param('A', 'integer')

    def testGetId(self):
        param = Param('A', 'integer')
        pId = param.getId()
        self.assertEqual('A', pId, msg='The parameter ID should be "A"')

    def testGetType(self):
        param = Param('A', 'integer')
        pType = param.getType()
        self.assertEqual('integer', pType, msg='Parameter should be "integer"')

    def testCreateParamWithMultipleRanges(self):
        Param('A', 'integer', inclMin=(1,5), inclMax=(2,7))
        Param('A', 'integer', inclMin=('1','5','-5'), inclMax=(2,7,5))
        Param('A', 'float', exclMin=('.5','5.0','-5'), exclMax=(.9,7,5))
        Param('A', 'float',
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
        param = Param('A', 'integer', inclMin=1, inclMax=2)
        self.assertIsNotNone(iter(param.getMin()))

    def testNoneIdShouldNotRaiseError(self):
        param = Param(None, 'integer')
        self.assertIsNotNone(param.getId())

    def testNoneTypeShouldRaiseError(self):
        with self.assertRaises(ValueError):
            param = Param('A', None)

    def testMultipleMinLimitsShouldRaiseError(self):
        with self.assertRaises(ValueError):
            param = Param('A', 'integer', inclMin=1, exclMin=10)

    def testMultipleMaxLimitsShouldRaiseError(self):
        with self.assertRaises(ValueError):
            param = Param('A', 'integer', inclMax=1, exclMax=10)

    def testParamWithoutLimitsIsNotDependent(self):
        param = Param('A', 'integer')
        self.assertFalse(param.isDependent())

    def testParamWithIntegerLimitIsNotDependent(self):
        param = Param('A', 'integer', inclMin=1, exclMax=3)
        self.assertFalse(param.isDependent())

    def testParamWithParameterReferenceIsDependent(self):
        param = Param('A', 'integer', inclMin='B', exclMax='B + C')
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
            param = Param('A', 'integer', inclMin=minExp, inclMax=maxExp)
            dependees = param.getDependees()
            self.assertCountEqual(expected, dependees)

    def testIndependentParameterWithExpressionShouldBeEvaluated(self):
        param = Param('A', 'integer', inclMin='1', exclMax='1 + 2')
        self.assertFalse(param.isDependent())
        self.assertEqual((1,), param.getMin())
        self.assertEqual((3,), param.getMax())

    def testIdenpendentParameterWithMoreComplexExpression(self):
        # 2.0
        eMin = 'Math.sqrt(Math.ceil(2.1) + Math.cos(0.0))'
        # 5.0
        iMax = 'Math.log(Math.exp(10)) / Math.floor(2.9)'
        param = Param('A', 'integer', exclMin=eMin, inclMax=iMax)
        self.assertFalse(param.isDependent())
        # Should probably really expect 2 and 5 here.
        self.assertEqual((2.0,), param.getMin())
        self.assertEqual((5.0,), param.getMax())

    def testDependentParameterWithSimpleDependency(self):
        param = Param('A', 'integer', inclMin='B')
        self.assertTrue(param.isDependent())

    def testCreatingFixedParameter(self):
        param = Param('A', 'integer', fixed=3)
        self.assertTrue(param.isFixed())

    def testUnfixParameter(self):
        param = Param('A', 'integer', fixed=3)
        param.setFixed(None)
        self.assertFalse(param.isFixed())

    def testFixAndUnfixExistingParameter(self):
        param = Param('A', 'integer')
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
        reference = Param('A', 'integer', inclMin=3, fixed=4)
        param = getParameter('A', 'integer', inclMin=3, fixed=4)
        self.compareParameters(reference, param)

        arrayParam = getParameter('A', 'integer[2]', inclMin=3, fixed=4)
        self.assertEqual(2, arrayParam.getSize())
        self.compareParameters(param, arrayParam.getParameter())

        arrayParam2 = getParameter('A', 'integer[2][2]', inclMin=3, fixed=4)
        self.compareParameters(arrayParam, arrayParam2.getParameter())

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
        param = Param(*args, **kwargs)

        # Check that the ranges were padded.
        self.assertEqual(len(param.getMin()), len(param.getMax()))

        if eMin is not None:
            self.assertTrue(param.isMinExclusive())
        if eMax is not None:
            self.assertTrue(param.isMaxExclusive())


class TestParamStore(unittest.TestCase):
    def testAddMultipleParameters(self):
        param1 = Param('A', 'integer')
        param2 = Param('B', 'integer')
        params = (param1, param2)
        ps = ParamStore()
        ps.addParam(params)
        self.checkForParametersInParamStore(params, ps)

    def testCreateParamStoreWithMultipleParameters(self):
        param1 = Param('A', 'integer')
        param2 = Param('B', 'integer')
        params = (param1, param2)
        ps = ParamStore(params)
        self.checkForParametersInParamStore(params, ps)

    def testSetFixed(self):
        paramId = 'A'
        param = Param(paramId, 'integer')
        ps = ParamStore()
        ps.addParam(param)
        self.assertFalse(param.isFixed())
        ps.setFixed(paramId, 3)
        self.assertTrue(param.isFixed())
        ps.setFixed(paramId, None)
        self.assertFalse(param.isFixed())

    def testGetInitializationOrderForUnfinalizedParamStore(self):
        param1 = Param('A', 'integer')
        param2 = Param('B', 'integer', inclMin='A')
        ps = ParamStore((param1, param2))
        expected = {0: ['A'], 1: ['B']}
        self.assertEqual(expected, ps.getInitializationOrder())

    def testGetInitializationOrderForEmptyParamStore(self):
        ps = ParamStore()
        expected = {}
        self.assertEqual(expected, ps.getInitializationOrder())

    def testMultipleFinalizeHaveNoEffect(self):
        ps = ParamStore()
        # Should construct initialization order data.
        ps.finalize()
        # Already finalized, so this call should return the same data.
        first = ps.getInitializationOrder()
        # Another explicit finalize should have no effect.
        ps.finalize()
        # Fetch data again and make sure it's still the same.
        second = ps.getInitializationOrder()
        self.assertIs(first, second)

    def testFinalizeMakesParameterStoreReadOnly(self):
        ps = ParamStore()
        ps.finalize()
        with self.assertRaises(NotImplementedError):
            ps.addParam(Param('A', 'integer'))

    def testParameterWithUnmetDependencies(self):
        ps = ParamStore(Param('A', 'integer', inclMin='B + 1'))
        with self.assertRaises(ValueError):
            ps.finalize()

    def testNonEmptyRangeShouldSucceed(self):
        Param('A', 'integer', inclMin=1, inclMax=1)
        Param('A', 'integer', exclMin=1, exclMax=3)

    def testEmptyRangeShouldRaiseError(self):
        self.checkRangeErrors({'inclMin':1, 'exclMax':1})
        self.checkRangeErrors({'exclMin':1, 'inclMax':1})
        self.checkRangeErrors({'exclMin':1, 'exclMax':2})
        self.checkRangeErrors({'exclMin':1, 'exclMax':2})

    def testAddingParamWithCircularDependencyRaisesError(self):
        ps = ParamStore()
        with self.assertRaises(ValueError):
            ps.addParam(Param('A', 'integer', inclMin='B'))
            ps.addParam(Param('B', 'integer', inclMin='A'))
            ps.finalize()

    def testAddingParamWithIndirectCircularDependencyRaisesError(self):
        ps = ParamStore()
        with self.assertRaises(ValueError):
            ps.addParam(Param('A', 'integer', inclMin='B'))
            ps.addParam(Param('B', 'integer', inclMin='C'))
            ps.addParam(Param('C', 'integer', inclMin='A'))
            ps.finalize()

    def checkRangeErrors(self, kwargs, pa=None):
        args = pa or ('A', 'integer')
        ps = ParamStore(Param(*args, **kwargs))
        with self.assertRaises(ValueError):
            ps.finalize()

    def checkForParametersInParamStore(self, params, ps):
        for p in params:
            self.assertIs(p, ps.getParam(p.getId()))

if __name__ == '__main__':
    unittest.main()
