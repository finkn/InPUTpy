"""
:copyright: (c) 2013 by Christoffer Fink.
:license: MIT. See LICENSE for details.
"""
import unittest
from inputpy.param import ParamStore, getParameter
from inputpy.mapping import DUMMY_MAPPING
from inputpy.q import *

class TestParamStore(unittest.TestCase):
    param_A = getParameter('A', NPARAM, INTEGER)
    param_B = getParameter('B', NPARAM, INTEGER)

    def testAddMultipleParameters(self):
        param1 = TestParamStore.param_A
        param2 = TestParamStore.param_B
        params = (param1, param2)
        ps = ParamStore()
        ps.addParam(params)
        self.checkForParametersInParamStore(params, ps)

    def testCreateParamStoreWithMultipleParameters(self):
        param1 = TestParamStore.param_A
        param2 = TestParamStore.param_B
        params = (param1, param2)
        ps = ParamStore(params)
        self.checkForParametersInParamStore(params, ps)

    def testSetFixed(self):
        param = TestParamStore.param_A
        paramId = param.getId()
        ps = ParamStore()
        ps.addParam(param)
        self.assertFalse(param.isFixed())
        ps.setFixed(paramId, 3)
        self.assertTrue(param.isFixed())
        ps.setFixed(paramId, None)
        self.assertFalse(param.isFixed())

    def testGetInitializationOrderForUnfinalizedParamStore(self):
        param1 = TestParamStore.param_A
        param2 = getParameter('B', NPARAM, INTEGER, inclMin='A')
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
            ps.addParam(TestParamStore.param_A)

    def testParameterWithUnmetDependencies(self):
        ps = ParamStore(getParameter('A', NPARAM, INTEGER, inclMin='B + 1'))
        with self.assertRaises(ValueError):
            ps.finalize()

    # Move this test to test_param.
    def testNonEmptyRangeShouldSucceed(self):
        getParameter('A', NPARAM, INTEGER, inclMin=1, inclMax=1)
        getParameter('A', NPARAM, INTEGER, exclMin=1, exclMax=3)

    def testEmptyRangeShouldRaiseError(self):
        self.checkRangeErrors({INCL_MIN:1, EXCL_MAX:1})
        self.checkRangeErrors({EXCL_MIN:1, INCL_MAX:1})
        self.checkRangeErrors({EXCL_MIN:1, EXCL_MAX:2})
        self.checkRangeErrors({EXCL_MIN:1, EXCL_MAX:2})
        self.checkRangeErrors({'inclMin':1, 'exclMax':1})
        self.checkRangeErrors({'exclMin':1, 'inclMax':1})
        self.checkRangeErrors({'exclMin':1, 'exclMax':2})
        self.checkRangeErrors({'exclMin':1, 'exclMax':2})

    def testAddingParamWithCircularDependencyRaisesError(self):
        ps = ParamStore()
        with self.assertRaises(ValueError):
            ps.addParam(getParameter('A', NPARAM, INTEGER, inclMin='B'))
            ps.addParam(getParameter('B', NPARAM, INTEGER, inclMin='A'))
            ps.finalize()

    def testAddingParamWithIndirectCircularDependencyRaisesError(self):
        ps = ParamStore()
        with self.assertRaises(ValueError):
            ps.addParam(getParameter('A', NPARAM, INTEGER, inclMin='B'))
            ps.addParam(getParameter('B', NPARAM, INTEGER, inclMin='C'))
            ps.addParam(getParameter('C', NPARAM, INTEGER, inclMin='A'))
            ps.finalize()

    def testAddSParams(self):
        m = DUMMY_MAPPING
        x = getParameter('X', NPARAM, INTEGER, parentId='A.B')
        y = getParameter('Y', NPARAM, INTEGER, parentId='A.B')
        b = getParameter('B', SPARAM, nested=(x, y), parentId='A', mapping=m)
        a = getParameter('A', SPARAM, nested=(b,), mapping=m)
        ps = ParamStore(a)
        initOrder = ps.getInitializationOrder()
        self.assertCountEqual(('A.B.X', 'A.B.Y'), initOrder[0])

    def checkRangeErrors(self, kwargs, pa=None):
        args = pa or ('A', NPARAM, INTEGER)
        ps = ParamStore(getParameter(*args, **kwargs))
        msg = '%s should define an empty range' % (kwargs)
        with self.assertRaises(ValueError, msg=msg):
            ps.finalize()

    def checkForParametersInParamStore(self, params, ps):
        for p in params:
            self.assertIs(p, ps.getParam(p.getId()))


if __name__ == '__main__':
    unittest.main()
