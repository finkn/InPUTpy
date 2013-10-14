import unittest
from inputpy.util import Evaluator
from inputpy.util import depLen
from inputpy.util import initOrder
import inputpy.util as util

class TestEvaluator(unittest.TestCase):

    DEPENDENCY_TESTS = {
        'A+B': ('A', 'B',),
        'A + B': ('A', 'B',),
        'A + B-C/ D *E': ('A', 'B', 'C', 'D', 'E',),
        'Math.log(A)': ('A',),
        'A+ Math.sqr( B / C )': ('A', 'B', 'C',),
        ' 2 * ( (( A+B ) - (C) ) ) + A': ('A', 'B', 'C',),
        ' SomeParam + AnotherParam ': ('SomeParam', 'AnotherParam',),
        'A * -.3': ('A',),
        '1 + 2 - Math.cos(0.0)': (),
        'A.1.2+B.C.1.D': ('A.1.2', 'B.C.1.D',),
    }

    RANGE_TESTS = {
        # Looks trivial now, but might want to support arbitrary expressions.
        '1,5,-3': ('1', '5', '-3',),
    }

    PARAMS = {'A': 2, 'B': 1, 'C': 3}
    EXPRESSION_TESTS_WITHOUT_PARAMS = {
        'Math.log(Math.e * Math.cos(Math.sin(Math.pi/2)-1)) + 1': 2.0,
    }
    EXPRESSION_TESTS_WITH_PARAMS = {
        'Math.log(Math.e * Math.cos(Math.sin(Math.pi/2)-1)) + 1': 2.0,
        'Math.log(Math.e * Math.cos(Math.sin(Math.pi/A)-B)) + C': 4.0,
    }

    # Check for the correct version of math in other tests.
    def testSafeNamespaceShouldOnlyHaveBuiltinsAndOneMoreItem(self):
        ns = Evaluator.getSafeNamespace()
        self.assertEqual({}, ns['__builtins__'])
        self.assertEqual(2, len(ns.items()))

    def testGetSaveNamespaceWithDefaultModeShouldUseJs(self):
        self.assertIn('Math', Evaluator.getSafeNamespace())

    def testGetSafeNamespaceWithPyMode(self):
        self.assertIn('math', Evaluator.getSafeNamespace(mode=Evaluator.PY))

    def testGetSafeNamespaceWithInvalidModeShouldRaiseError(self):
        with self.assertRaises(ValueError):
            Evaluator.getSafeNamespace(mode='some invalid mode')

    def testParseDependenciesWithInvalidModeShouldRaiseError(self):
        with self.assertRaises(ValueError):
            Evaluator.parseDependencies('A+B', mode='some invalid mode')

    def testEvaluateWithoutParameters(self):
        for (k, v) in self.EXPRESSION_TESTS_WITHOUT_PARAMS.items():
            self.assertEqual(v, Evaluator.evaluate(k))

    def testEvaluateWithParameters(self):
        for (k, v) in self.EXPRESSION_TESTS_WITH_PARAMS.items():
            self.assertEqual(v, Evaluator.evaluate(k, self.PARAMS))

    def testParseDependencies(self):
        tests = self.DEPENDENCY_TESTS
        for (exp, value) in tests.items():
            dep = Evaluator.parseDependencies(exp)
            self.assertCountEqual(value, dep)

    def testParseRange(self):
        tests = self.DEPENDENCY_TESTS
        for (exp, value) in tests.items():
            self.assertEqual(1, len(Evaluator.parseRange(exp)))

        tests = self.RANGE_TESTS
        for (exp, value) in tests.items():
            self.assertCountEqual(value, Evaluator.parseRange(exp))

    def testGetRemapping(self):
        tests = (
            ((('A',), ('A',)), {}),
            ((('A.B',), ('A.B',)), {'A.B': '__A_B__0'}),
            ((('A.B',), ('A.B', '__A_B__1')), {'A.B': '__A_B__0'}),
            ((('A.B',), ('A.B', '__A_B__0')), {'A.B': '__A_B__1'}),
        )

        for (args, expected) in tests:
            self.assertEqual(expected, Evaluator.getRemapping(*args))

    def testRemapExpression(self):
        tests = (
            (('A + B', {}), 'A + B'),
            (('A + B', {'A': 'C'}), 'C + B'),
            (('A.X + B.X', {'A.X': 'A', 'B.X': 'B'}), 'A + B'),
            (('A.B.X + B.X', {'A.B.X': 'A', 'B.X': 'B'}), 'A + B'),
            (('A.X + B.A.X', {'A.X': 'A', 'B.A.X': 'B'}), 'A + B'),
        )

        for (args, expected) in tests:
            self.assertEqual(expected, Evaluator.remapExpression(*args))


class TestMiscUtil(unittest.TestCase):

    DEPENDENCIES = (
        (
            {'A': (), 'B': (), 'C': (), },
            {'A': 0, 'B': 0, 'C': 0, },
        ),
        (
            {'A': ('B'), 'B': ('C'), 'C': (), },
            {'A': 2, 'B': 1, 'C': 0, },
        ),
        (
            {'A': ('B', 'C'), 'B': ('C'), 'C': (), },
            {'A': 2, 'B': 1, 'C': 0, },
        ),
    )

    def testCalculateDependencies(self):
        for d in self.DEPENDENCIES:
            self.checkDependencyLength(d)

    def testInitOrder(self):
        for d in self.DEPENDENCIES:
            self.checkInitOrder(d)

    def testGetValue(self):
        tests = (
            (
                {'A': 'a', 'B': 43, },          # Parameters.
                {'A': 'a', 'B': 43, },          # Expected key-value mappings.
            ),
            (
                {'A.1': 'a', 'B.2.3': 43, },    # Parameters.
                {'A.1': 'a', 'B.2.3': 43, },    # Expected key-value mappings.
            ),
            (
                {'A': ['a', 'b', 'c', ], },     # Parameters.
                {
                    'A': ['a', 'b', 'c', ],     # Expected key-value mappings.
                    'A.1': 'a',
                    'A.3': 'c',
                },
            ),
            (
                {'A': [[1, 2, 3], ['a', 'b', 'c']], 'A.1.1': 'ignored',},
                {
                    'A': [[1, 2, 3], ['a', 'b', 'c']],
                    'A.1': [1, 2, 3],
                    'A.2': ['a', 'b', 'c'],
                    'A.1.1': 1,
                    'A.2.3': 'c',
                },
            ),
        )

        # Check that a missing parameter is None.
        self.assertIsNone(util.getValue('NonExistent', tests[0][0]))

        for (params, expected) in tests:
            for (key, value) in expected.items():
                self.assertEqual(value, util.getValue(key, params))

    def testSetValue(self):
        tests = (
            (
                {'A': 'a', 'B': 43, },          # Parameters.
                {'A': -99, 'B': 43, },          # Expected key-value mappings.
            ),
            (
                {'A.1': 'a', 'B.2.3': 43, },    # Parameters.
                {'A.1': -99, 'B.2.3': 43, },    # Expected key-value mappings.
            ),
            (
                {'A': ['a', 'b', 'c', ], },     # Parameters.
                {
                    'A': [1, 2, 3],     # Expected key-value mappings.
                    'A.1': -99,
                    'A.3': 99,
                },
            ),
            (
                {'A': [[1, 2, 3], ['a', 'b', 'c']], 'A.1.1': 'ignored',},
                {
                    'A': [[1, 2, 3], ['a', 'b', 'c']],
                    'A.1': [1, 2, 3],
                    'A.2': ['c', 'b', 'a'],
                    'A.1.1': 0,
                    'A.2.3': 'z',
                },
            ),
        )
        with self.assertRaises(KeyError):
            util.setValue('NonExistent', {}, 3)
        with self.assertRaises(KeyError):
            util.setValue('A.1', {}, 3)
        with self.assertRaises(KeyError):
            util.setValue('A.1.1', {'A': [1,2,3]}, 3)

        for (params, expected) in tests:
            for (key, value) in expected.items():
                util.setValue(key, params, value)
                self.assertEqual(value, util.getValue(key, params))

    def testParseDimensions(self):
        tests = (
            {'integer': []},
            {'integer[2]': [2,]},
            {'integer[]': [0,]},
            {'integer[1][2]': [1, 2,]},
            {'integer[][]': [0, 0,]},
            {'integer[1][][1]': [1, 0, 1]},
            {'integer[][1][]': [0, 1, 0]},
            {'boolean[][][]': [0, 0, 0]},
        )
        for t in tests:
            for (key, expected) in t.items():
                result = util.parseDimensions(key)
                self.assertEqual(expected, result)

    def testExpandParameterScope(self):
        tests = (
            ('T1.P1.X', 'T1.P1'),
            ('P1.X', 'P1'),
            ('P1', None),
        )
        for t in tests:
            self.assertEqual(t[1], util.expandParameterScope(t[0]))

    def testFindAbsoluteParameter(self):
        ids = [
            'X', 'Y', 'P1', 'P4', 'T1', 'T2',
            'P1.X', 'P1.Y', 'P4.X', 'P4.Y',
            'T1.P1', 'T1.P2', 'T1.P3', 'T2.P1', 'T2.P2', 'T2.P3',
            'T1.P1.X', 'T1.P1.Y', 'T1.P2.X', 'T1.P2.Y', 'T1.P3.X', 'T1.P3.Y',
            'T2.P1.X', 'T2.P1.Y', 'T2.P2.X', 'T2.P2.Y', 'T2.P3.X', 'T2.P3.Y',
        ]
        tests = (
            # Using relative names when possible.
            (('P1', 'X'), 'P1.X'),
            (('T1.P1', 'X'), 'T1.P1.X'),
            (('T1', 'P1'), 'T1.P1'),
            (('T1', 'P4'), 'P4'),
            (('T1', 'T2.P1'), 'T2.P1'), # Relative name not possible here.
            (('T1', 'X'), 'X'),
            # Using absolute names even when not required.
            (('T1', 'T1.P1.X'), 'T1.P1.X'),
            # Referring to a nested scope.
            (('T1.P1', 'P2'), 'T1.P2'),
            (('T1.P1.Y', 'P2.X'), 'T1.P2.X'),
            (('T1.P1.Y', 'X'), 'T1.P1.X'),
        )
        for t in tests:
            args = (t[0][0], t[0][1], ids)
            self.assertEqual(t[1], util.findAbsoluteParameter(*args))


    def checkInitOrder(self, dep):
        dependencies = dep[0]
        lengths = dep[1]
        order = initOrder(dependencies)
        for (k, v) in lengths.items():
            self.assertIn(k, order[v])

    def checkDependencyLength(self, dep):
        dependencies = dep[0]
        lengths = dep[1]
        for k in dependencies.keys():
            val = depLen(dependencies, k)
            self.assertEqual(val, lengths[k])

if __name__ == '__main__':
    unittest.main()
