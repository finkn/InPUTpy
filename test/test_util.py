import unittest
from inputpy.util import Evaluator
from inputpy.util import depLen
from inputpy.util import initOrder

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
