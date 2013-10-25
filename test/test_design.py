"""
:copyright: (c) 2013 by Christoffer Fink.
:license: MIT. See LICENSE for details.
"""
import unittest
from inputpy.param import ParamStore, Design, getParameter
from inputpy.designspace import DesignSpace
from inputpy.exceptions import InPUTException
from inputpy.q import *
from test.tools import PresetDesignSpaceFactory

class TestDesign(unittest.TestCase):
    def testCreateEmptyDesignWithoutId(self):
        design = Design({})
        self.assertIsNotNone(design.getId())

    def testCreateEmptyDesignWithId(self):
        design = Design({}, designId='Design')
        self.assertEqual('Design', design.getId())

    def testGetParameterValue(self):
        params = {'A': 43, 'B': 10}
        design = Design(params)
        for key in params.keys():
            value = params[key]
            self.assertEqual(value, design.getValue(key))

    def testCreateDesignFromDesignSpace(self):
        ps = ParamStore()
        ps.addParam(getParameter('A', NPARAM, INTEGER, inclMin=1, inclMax=1))
        ps.addParam(getParameter('B', NPARAM, INTEGER, exclMin=1, exclMax=3))
        space = DesignSpace(ps)
        design = space.nextDesign('Design')
        self.assertEqual(1, design.getValue('A'))
        self.assertEqual(2, design.getValue('B'))
        self.assertEqual('Design', design.getId())

    def testCreateDesignWithArray(self):
        t = INTEGER + '[2][][3]'
        param = getParameter('A', NPARAM, t, inclMin=2, inclMax=2)
        param2 = getParameter('A.1', NPARAM, FLOAT,
            inclMin=2, inclMax=2, fixed=0.5)
        space = DesignSpace(ParamStore((param, param2)))
        design = space.nextDesign('Design')
        expected = [
            [[2, 2, 2]],
            [[2, 2, 2]],
        ]
        result = design.getValue('A')
        self.assertEqual(expected, result)
        result[0][0][2] = 3     # Do we want this?
        self.assertEqual([[2, 2, 3]], design.getValue('A.1'))
        self.assertEqual([2, 2, 2], design.getValue('A.2.1'))
        self.assertEqual(2, design.getValue('A.2.1.3'))

    def testSetValue(self):
        t = INTEGER + '[2][][3]'
        param1 = getParameter('A', NPARAM, t)
        param2 = getParameter('B', NPARAM, FLOAT, inclMin=-1, inclMax=1)
        space = DesignSpace(ParamStore((param1, param2)))
        design = space.nextDesign('Design')

        oldB = design.getValue('B')
        design.setValue('B', 0)
        newB = design.getValue('B')
        self.assertNotEqual(oldB, newB) # Can fail, but extremely unlikely.
        self.assertEqual(0, newB)

        design.setValue('A.1', [0, 0, 0])
        design.setValue('A.2', [1, 1, 1])
        a = design.getValue('A')
        self.assertEqual([0,0,0], a[0])
        self.assertEqual([1,1,1], a[1])
        design.setValue('A.2.3', 2)
        a = design.getValue('A')
        self.assertEqual([1,1,2], a[1])
        self.assertEqual(2, a[1][2])

    def testSetReadOnly(self):
        design = Design({'A': 1})
        design.setValue('A', 2)
        design.setReadOnly()
        with self.assertRaises(InPUTException):
            design.setValue('A', 1)

    def testSetReadOnlyInConstructor(self):
        design = Design({'A': 1}, readOnly=True)
        with self.assertRaises(InPUTException):
            design.setValue('A', 2)

    def testExtendScope(self):
        design = Design({'A': 1})
        extending = Design({'B': 2})
        design.extendScope(extending)
        self.assertEqual(design.getValue('B'), extending.getValue('B'))

    def testExtendScopeWithNoneDesignShouldFail(self):
        design = Design({'A': 1})
        with self.assertRaises(InPUTException):
            design.extendScope(None)

    def testExtendScopeWithExistingDesignShouldFail(self):
        design = Design({'A': 1})
        extending = Design({'B': 2})
        design.extendScope(extending)
        with self.assertRaises(InPUTException):
            design.extendScope(extending)

    def testExtendScopeWithSelfShouldFail(self):
        design = Design({'A': 1})
        with self.assertRaises(InPUTException):
            design.extendScope(design)

    def testGetSpace(self):
        ps = ParamStore()
        ps.addParam(getParameter('A', NPARAM, INTEGER, inclMin=1, inclMax=1))
        ps.addParam(getParameter('B', NPARAM, INTEGER, exclMin=1, exclMax=3))
        space = DesignSpace(ps)
        design = Design({}, space, 'Design')
        self.assertEqual(space, design.getSpace())

    def testEmptySParamDesign(self):
        from inputpy.mapping import Mapping
        ps = ParamStore()
        emptyMapping = Mapping('Empty', 'test.types.simple.EmptyClass')
        emptyParam = getParameter('Empty', 'SParam', mapping=emptyMapping)
        ps.addParam(emptyParam)
        space = DesignSpace(ps)
        design = space.nextDesign('Design')
        self.assertIsNotNone(design.getValue('Empty'))

    def testPointSParamDesign(self):
        from inputpy.mapping import Mapping
        x = getParameter('X', NPARAM, INTEGER, inclMin=2, inclMax=2)
        y = getParameter('Y', NPARAM, INTEGER, inclMin=3, inclMax=3)
        ps = ParamStore([x, y])
        pointMapping = Mapping('Point', 'test.types.geo.Point', 'X Y')
        pointParam = getParameter('Point', 'SParam', nested=[x, y], mapping=pointMapping)
        ps.addParam(pointParam)
        space = DesignSpace(ps)
        design = space.nextDesign('Design')
        p = design.getValue('Point')
        self.assertEqual(2, p.getX())
        self.assertEqual(3, p.getY())

    # TODO:
    # It's about time this pattern with the dictionary is pulled out.
    def testSimpleTriangleDesign(self):
        config = 'simpleTriangleSpace.xml'
        factory = PresetDesignSpaceFactory.getDesignSpace
        space = factory(config)
        design = space.nextDesign('Design')

        expected = {
            'X': 0, 'Y': 1, 'P1.X': 2, 'P1.Y': 3, 'T1.P1.X': 1, 'T1.P1.Y': 1,
        }
        for (k, v) in expected.items():
            msg = 'wrong value for parameter %s' % (k)
            self.assertEqual(v, design.getValue(k), msg=msg)

    def testAdvancedTriangleDesign(self):
        config = 'advancedTriangleSpace.xml'
        factory = PresetDesignSpaceFactory.getDesignSpace
        space = factory(config)
        design = space.nextDesign('Design')

        expected = {
            'X': 0, 'Y': 1, 'P1.X': 4, 'P1.Y': 5, 'T1.P2.X': 3,
        }
        for (k, v) in expected.items():
            msg = 'wrong value for parameter %s' % (k)
            self.assertEqual(v, design.getValue(k), msg=msg)

if __name__ == '__main__':
    unittest.main()
