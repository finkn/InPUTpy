"""
:copyright: (c) 2013 by Christoffer Fink.
:license: MIT. See LICENSE for details.
"""
import unittest
from inputpy.param import Param, ParamStore, getParameter

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

    def testAddSParams(self):
        x = getParameter('X', 'integer', parentId='A.B')
        y = getParameter('Y', 'integer', parentId='A.B')
        b = getParameter('B', 'SParam', nested=(x, y), parentId='A')
        a = getParameter('A', 'SParam', nested=(b,))
        ps = ParamStore([a, b])
        initOrder = ps.getInitializationOrder()
        self.assertCountEqual(('A.B.X', 'A.B.Y'), initOrder[0])

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
