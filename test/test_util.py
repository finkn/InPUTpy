import unittest
from inputpy.util import Evaluator

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

if __name__ == '__main__':
    unittest.main()
