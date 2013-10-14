import unittest
from inputpy import mapping
from test import SomeStructural
from test.types.simple import EmptyClass
from test.types.geo import Point
from inputpy.mapping import Mapping
from inputpy.mapping import CodeMapping

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
            ('test.types.geo.Point', Point),
        ]
        for (name, result) in tests:
            self.assertIs(mapping.getType(name), result)

    def testCreateMapping(self):
        typeString = 'test.types.geo.Point'
        paramId = 'ParamId'
        m = Mapping(paramId, typeString, 'X Y')
        self.assertEqual(paramId, m.getId())
        self.assertEqual(typeString, m.getType())
        self.assertEqual(('X', 'Y'), m.getDependencies())

    def testCreateSimplMapping(self):
        typeString = 'test.types.simple.EmptyClass'
        paramId = 'ParamId'
        m = Mapping(paramId, typeString)
        self.assertEqual(paramId, m.getId())
        self.assertEqual(typeString, m.getType())
        self.assertEqual((), m.getDependencies())

    def testMakeDirectMapping(self):
        typeMapping = Mapping('PointType', 'test.types.geo.Point', 'X Y')
        pointMapping = Mapping.makeDirect('Point', typeMapping)
        self.assertEqual(pointMapping.getTypeName(), typeMapping.getTypeName())
        self.assertEqual(pointMapping.getConstructor(), typeMapping.getConstructor())
        self.assertEqual('Point', pointMapping.getId())

    def testGetMappingFromCodeMapping(self):
        # Note that we are dealing with two different 'Point' IDs.
        # One names a code mapping (a mapping type) and the other names
        # a parameter (a structured parameter).
        # There does not exist a direct mapping from parameter 'Point'
        # to type 'test.types.geo.Point'. Yet, when the full code mapping
        # object has been created, such a direct mapping will be returned.
        pointType = Mapping('Point', 'test.types.geo.Point', 'X Y')
        pointMapping = Mapping('Point', 'Point')
        emptyMapping = Mapping('Empty', 'test.types.simple.EmptyClass')
        mapping = CodeMapping([pointMapping, emptyMapping], [pointType])
        # The point of the test is that the difference of Mapping and
        # MappingType have been hidden and 'Empty' and 'Point' are treated
        # as if they were both defined with a Mapping.
        empty = mapping.getMapping('Empty')
        self.assertEqual('Empty', empty.getId())
        self.assertEqual('test.types.simple.EmptyClass', empty.getTypeName())
        point = mapping.getMapping('Point')
        self.assertEqual('Point', point.getId())
        self.assertEqual('test.types.geo.Point', point.getTypeName())

    # In the test above, the parameter name and the type name match ('Point').
    # Here the names are different to underscore that a transformation is
    # really occurring (pointType could just have been reused above).
    def testGetMappingFromCodeMappingWithDifferentNames(self):
        pointType = Mapping('PointType', 'test.types.geo.Point', 'X Y')
        pointMapping = Mapping('Point', 'PointType')
        mapping = CodeMapping([pointMapping], [pointType])
        point = mapping.getMapping('Point')
        self.assertEqual('Point', point.getId())
        self.assertEqual('test.types.geo.Point', point.getTypeName())

    def testGetDefaultAccessor(self):
        getter = {
            'abc': 'getabc',
            'Abc': 'getAbc',
            'ABC': 'getABC',
            'A.B.C': 'getC',
        }
        setter = {
            'abc': 'setabc',
            'Abc': 'setAbc',
            'ABC': 'setABC',
            'A.B.C': 'setC',
        }

        # I've done this quite a few times. It should be placed in a helper.
        for (k,v) in getter.items():
            self.assertEqual(v, mapping.getDefaultGetter(k))
        for (k,v) in setter.items():
            self.assertEqual(v, mapping.getDefaultSetter(k))

    def testAccessor(self):
        getter = {
            Mapping('X', 'builtin.str'): 'getX',
            Mapping('A.B.X', 'builtin.str'): 'getX',
            Mapping('X', 'builtin.str', get='customGetter'): 'customGetter',
        }
        setter = {
            Mapping('X', 'builtin.str'): 'setX',
            Mapping('A.B.X', 'builtin.str'): 'setX',
            Mapping('X', 'builtin.str', set='customSetter'): 'customSetter',
        }
        for (k,v) in getter.items():
            self.assertEqual(v, k.getGetter())
        for (k,v) in setter.items():
            self.assertEqual(v, k.getSetter())

if __name__ == '__main__':
    unittest.main()
