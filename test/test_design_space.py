"""
:copyright: (c) 2013 by Christoffer Fink.
:license: MIT. See LICENSE for details.
"""
import unittest
from inputpy.param import getParameter
from inputpy.paramstore import ParamStore
from inputpy.designspace import DesignSpace
from test.factories import PresetDesignSpaceFactory
from inputpy.q import *

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
        ps = ParamStore()
        param = getParameter('A', NPARAM, INTEGER)
        ps.addParam(param)
        param = getParameter('B', NPARAM, INTEGER)
        ps.addParam(param)
        space = DesignSpace(ps)
        params = space.getSupportedParamIds()
        self.assertCountEqual(params, ('A', 'B'))

    def testNext(self):
        param1 = getParameter('A', NPARAM, INTEGER, inclMin=1, inclMax=1)
        param2 = getParameter('B', NPARAM, INTEGER, exclMin=1, exclMax=3)
        ps = ParamStore()
        ps.addParam(param1)
        ps.addParam(param2)
        space = DesignSpace(ps)
        self.assertEqual(1, space.next(param1.getId()))
        self.assertEqual(2, space.next(param2.getId()))

    def testSetFixedInteger(self):
        paramId = 'Y'
        param = getParameter(paramId, NPARAM, INTEGER)
        ps = ParamStore()
        ps.addParam(param)
        space = DesignSpace(ps)
        self.assertFalse(param.isFixed())
        space.setFixed(paramId, 3)
        self.assertTrue(param.isFixed())

    def testSetFixedBoolean(self):
        paramId = 'A'
        param = getParameter(paramId, NPARAM, BOOLEAN)
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
        param = getParameter(paramId, NPARAM, INTEGER, inclMin=1, inclMax=1)
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
        ps.addParam(getParameter(paramId, NPARAM, INTEGER))
        space = DesignSpace(ps)
        # 2.0
        exp = 'Math.log(Math.e * Math.cos(Math.sin(Math.pi/2)-1)) + 1'
        space.setFixed(paramId, exp)
        self.assertEqual(2, space.next(paramId))

    def testNextValueForDependentParameter(self):
        ps = ParamStore()
        ps.addParam(getParameter('A', NPARAM, INTEGER,
            inclMin=3, inclMax='B + C'))
        ps.addParam(getParameter('B', NPARAM, INTEGER,
            inclMin='C - 5', inclMax=10))
        ps.addParam(getParameter('C', NPARAM, INTEGER, inclMin=5, inclMax=7))
        space = DesignSpace(ps)
        self.assertTrue(3 <= space.next('A') <= 17)
        self.assertTrue(0 <= space.next('B') <= 10)
        self.assertTrue(5 <= space.next('C') <= 7)

    def testCreateDesignFromDesignSpaceWithDependentParameters(self):
        param1 = getParameter('A', NPARAM, INTEGER, inclMin=3, inclMax='B + C')
        param2 = getParameter('B', NPARAM, INTEGER, inclMin='C', inclMax=10)
        param3 = getParameter('C', NPARAM, INTEGER, inclMin=5, inclMax=7)
        space = DesignSpace(ParamStore((param1, param2, param3)))
        design = space.nextDesign()
        a = design.getValue('A')
        b = design.getValue('B')
        c = design.getValue('C')
        self.assertTrue(3 <= design.getValue('A') <= b + c) # max 17
        self.assertTrue(c <= design.getValue('B') <= 10)    # min 5
        self.assertTrue(5 <= design.getValue('C') <= 7)

    def testCreateDesignSpaceWithArray(self):
        t = INTEGER + '[2][2]'
        param = getParameter('A', NPARAM, t, fixed=1)
        self.assertEqual(ARRAY, param.getType())
        space = DesignSpace(ParamStore(param))
        expected = [[1,1], [1,1]]
        result = space.next('A')
        self.assertEqual(expected, result)

    def testEqual(self):
        param1 = getParameter('A', NPARAM, INTEGER)
        param2 = getParameter('B', NPARAM, INTEGER)
        param3 = getParameter('C', NPARAM, INTEGER, inclMin=1)
        ps1 = ParamStore((param1, param2))
        ps2 = ParamStore((param1, param2, param3))
        ps3 = ParamStore((param1, param2, param3))  # Same as ps2
        space1 = DesignSpace(ps1, 'space 1')
        space2 = DesignSpace(ps1, 'space 2')
        space3 = DesignSpace(ps1, 'space 1')
        self.assertNotEqual(space1, space2)
        self.assertEqual(space1, space3)
        space4 = DesignSpace(ps1, 'space')
        space5 = DesignSpace(ps2, 'space')
        space6 = DesignSpace(ps3, 'space')
        self.assertNotEqual(space4, space5)
        self.assertEqual(space5, space6)

    def testIsFileShouldBeFalseWhenNoFileWasGiven(self):
        space = DesignSpace(ParamStore())
        self.assertFalse(space.isFile())

    def testIsFileShouldBeTrueWhenFileWasGiven(self):
        space = DesignSpace(ParamStore(), fileName='something.xml')
        self.assertTrue(space.isFile())

    def testIsFileShouldBeTrueWhenImportingFromAFile(self):
        factory = PresetDesignSpaceFactory.getDesignSpace
        space = factory('simpleIntegerParameterSpace.xml')
        self.assertTrue(space.isFile())

    def testGetFile(self):
        space = DesignSpace(ParamStore(), fileName='something.xml')
        self.assertEqual(space.getFileName(), 'something.xml')

    def testNextEmptyDesign(self):
        factory = PresetDesignSpaceFactory.getDesignSpace
        space = factory('simpleIntegerParameterSpace.xml')
        design = space.nextEmptyDesign('some design ID')
        self.assertEqual(design.getId(), 'some design ID')
        # The new design should support exactly the same parameters
        # (as determined by ID). If all of them map to a None value, that
        # means that the design is indeed uninitialized.
        paramIds = design.getSupportedParamIds()
        self.assertCountEqual(space.getSupportedParamIds(), paramIds)
        self.assertTrue(all([design.getValue(p) is None for p in paramIds]))

    def testGetSupportedParamIds(self):
        space = PresetDesignSpaceFactory.getDesignSpace('arraySpace.xml')
        expected = [
            'IntArray1', 'IntArray2', 'StringArray1', 'EmptyChoiceArray',
            'PointChoiceArray.NoConstructor',
        ]
        supportedIds = space.getSupportedParamIds()
        for paramId in expected:
            self.assertIn(paramId, supportedIds)
        self.assertNotIn('IntArray1.1', supportedIds)


if __name__ == '__main__':
    unittest.main()
