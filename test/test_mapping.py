import unittest
from inputpy import mapping
from test import SomeStructural
from test.types.simple import EmptyClass

class TestMapping(unittest.TestCase):
    def testGetBuiltinTypes(self):
        self.assertIs(mapping.getType('int'), int)
        self.assertIs(mapping.getType('float'), float)
        self.assertIs(mapping.getType('str'), str)
        self.assertIs(mapping.getType('bool'), bool)
        self.assertIs(mapping.getType('builtins.bool'), bool)
        self.assertIs(mapping.getType('builtins.complex'), complex)

    def testGetCustomTypes(self):
        tests = [
            ('test.SomeStructural', SomeStructural),
            ('test.types.simple.EmptyClass', EmptyClass),
        ]
        for (name, result) in tests:
            self.assertIs(mapping.getType(name), result)

if __name__ == '__main__':
    unittest.main()
