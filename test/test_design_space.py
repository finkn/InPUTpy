import unittest
from inputpy.param import Param
from inputpy.param import ParamStore
from inputpy.param import DesignSpace
from inputpy.param import getParameter

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


if __name__ == '__main__':
    unittest.main()