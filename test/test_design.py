import unittest
from inputpy.param import Param
from inputpy.param import ParamStore
from inputpy.param import Design
from inputpy.param import getParameter
from inputpy.designspace import DesignSpace
from inputpy.exceptions import InPUTException

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

    def testCreateDesignWithArray(self):
        param = getParameter('A', 'integer[2][][3]', inclMin=2, inclMax=2)
        param2 = getParameter('A.1', 'float', inclMin=2, inclMax=2, fixed=0.5)
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
        param1 = getParameter('A', 'integer[2][3]')
        param2 = getParameter('B', 'float', inclMin=-1, inclMax=1)
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


if __name__ == '__main__':
    unittest.main()
