import unittest
from inputpy.param import Param
from inputpy.param import ParamStore
from inputpy.param import DesignSpace
from inputpy.param import Design

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

    def testGenerateValueForParameter(self):
        param1 = Param('A', 'integer', inclMin=1, inclMax=1)
        param2 = Param('B', 'integer', exclMin=1, exclMax=3)
        ps = ParamStore()
        ps.addParam(param1)
        ps.addParam(param2)
        space = DesignSpace(ps)
        value = space.next(param1.getId())
        self.assertEqual(1, value)
        value = space.next(param2.getId())
        self.assertEqual(2, value)

    def testNext(self):
        param1 = Param('A', 'integer', inclMin=1, inclMax=1)
        param2 = Param('B', 'integer', exclMin=1, exclMax=3)
        ps = ParamStore()
        ps.addParam(param1)
        ps.addParam(param2)
        space = DesignSpace(ps)
        self.assertEqual(1, space.next(param1.getId()))
        self.assertEqual(2, space.next(param2.getId()))

    def testSetFixed(self):
        paramId = 'Y'
        param = Param(paramId, 'integer')
        ps = ParamStore()
        ps.addParam(param)
        space = DesignSpace(ps)
        self.assertFalse(param.isFixed())
        space.setFixed(paramId, 3)
        self.assertTrue(param.isFixed())

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
        self.checkLimits(iMax=1, eMin=10)
        self.checkLimits(eMax=1, iMin=10)

    def testNoneIdShouldRaiseError(self):
        with self.assertRaises(ValueError):
            param = Param(None, 'integer')

    def testNoneTypeShouldRaiseError(self):
        with self.assertRaises(ValueError):
            param = Param('A', None)

    def testMultipleMinLimitsShouldRaiseError(self):
        with self.assertRaises(ValueError):
            param = Param('A', 'integer', inclMin=1, exclMin=10)

    def testMultipleMaxLimitsShouldRaiseError(self):
        with self.assertRaises(ValueError):
            param = Param('A', 'integer', inclMax=1, exclMax=10)

    def testNonEmptyRangeShouldSucceed(self):
        Param('A', 'integer', inclMin=1, inclMax=1)
        Param('A', 'integer', exclMin=1, exclMax=3)

    def testEmptyRangeShouldRaiseError(self):
        self.checkRangeErrors({'inclMin':1, 'exclMax':1})
        self.checkRangeErrors({'exclMin':1, 'inclMax':1})
        self.checkRangeErrors({'exclMin':1, 'exclMax':2})
        self.checkRangeErrors({'exclMin':1, 'exclMax':2})

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
        self.assertEqual(1, param.getMin())
        self.assertEqual(3, param.getMax())

    def testIdenpendentParameterWithMoreComplexExpression(self):
        # 2.0
        eMin = 'Math.sqrt(Math.ceil(2.1) + Math.cos(0.0))'
        # 5.0
        iMax = 'Math.log(Math.exp(10)) / Math.floor(2.9)'
        param = Param('A', 'integer', exclMin=eMin, inclMax=iMax)
        self.assertFalse(param.isDependent())
        # Should probably really expect 2 and 5 here.
        self.assertEqual(2.0, param.getMin())
        self.assertEqual(5.0, param.getMax())

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

    def checkRangeErrors(self, kwargs, pa=None):
        args = pa or ('A', 'integer')
        with self.assertRaises(ValueError):
            Param(*args, **kwargs)

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

        minLimit = iMin or eMin
        maxLimit = iMax or eMax
        self.assertEqual(minLimit, param.getMin())
        self.assertEqual(maxLimit, param.getMax())

        if eMin is not None:
            self.assertTrue(param.isMinExclusive())
        elif iMin is not None:
            self.assertTrue(param.isMinInclusive())
        if eMax is not None:
            self.assertTrue(param.isMaxExclusive())
        elif iMax is not None:
            self.assertTrue(param.isMaxInclusive())

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

    def checkForParametersInParamStore(self, params, ps):
        for p in params:
            self.assertIs(p, ps.getParam(p.getId()))

if __name__ == '__main__':
    unittest.main()
