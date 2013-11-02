"""
:copyright: (c) 2013 by Christoffer Fink.
:license: MIT. See LICENSE for details.
"""
import unittest
from inputpy import mapping
from test import SomeStructural
from test.types.simple import EmptyClass
from test.types.geo import Point, Triangle
from test.factories import PresetCodeMappingFactory, PresetDesignSpaceFactory
from inputpy.mapping import Mapping, CodeMapping, NULL_CODE_MAPPING

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
        self.assertEqual(typeString, m.getTypeName())
        self.assertEqual(('X', 'Y'), m.getDependencies())

    def testCreateSimplMapping(self):
        typeString = 'test.types.simple.EmptyClass'
        paramId = 'ParamId'
        m = Mapping(paramId, typeString)
        self.assertEqual(paramId, m.getId())
        self.assertEqual(typeString, m.getTypeName())
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
            'getX': Mapping('X', 'builtin.str'),
            'getY': Mapping('A.B.Y', 'builtin.str'),
            'customGetter': Mapping('X', 'builtin.str', get='customGetter'),
        }
        setter = {
            'setX': Mapping('X', 'builtin.str'),
            'setY': Mapping('A.B.Y', 'builtin.str'),
            'customSetter': Mapping('X', 'builtin.str', set='customSetter'),
        }
        for (k,v) in getter.items():
            self.assertEqual(k, v.getGetter())
        for (k,v) in setter.items():
            self.assertEqual(k, v.getSetter())

    def testDifferentTriangleInitializations(self):
        dsConfig = 'simpleTriangleSpace.xml'
        mappingConfigs = (
            'triangleMapping.xml',
            'triangleCustomAccessorMapping.xml',
            'triangleDefaultAccessorMapping.xml',
        )
        cmFactory = PresetCodeMappingFactory.getCodeMapping
        dsFactory = PresetDesignSpaceFactory.getDesignSpace

        for config in mappingConfigs:
            mapping = cmFactory(config)
            space = dsFactory(dsConfig, codeMappingFactory=lambda x: mapping)
            result = space.next('T1')
            expected = Triangle(Point(1,1), Point(3,2), Point(5,1))
            self.assertEqual(expected, result)

    def testMappingEquality(self):
        unequal = (
            Mapping('M1', 'builtin.str'),
            Mapping('M2', 'builtin.str'),
            Mapping('M1', 'builtin.int'),
            Mapping('M1', 'builtin.str', 'X Y'),
            Mapping('M1', 'builtin.str', 'Y X'),
            Mapping('M1', 'builtin.str', 'X Y', 'setM1'),
            Mapping('M1', 'builtin.str', 'X Y', 'M1setter'),
            Mapping('M1', 'builtin.str', 'X Y', 'M1setter', 'getM1'),
            Mapping('M1', 'builtin.str', 'X Y', 'M1setter', 'M1getter'),
        )
        for m in unequal:
            self.assertNotEqual(m, None)
            for n in unequal:
                if m is n: continue
                self.assertNotEqual(m, n)

        equal = (
            (
                Mapping('M1', 'builtin.str', 'X Y', 'M1setter', 'M1getter'),
                Mapping('M1', 'builtin.str', 'X Y', 'M1setter', 'M1getter'),
            ),
            (
                Mapping('M1', 'builtin.str'),
                Mapping('M1', 'builtin.str'),
            ),
        )
        for (m, n) in equal:
            self.assertEqual(m, n)

    # This isn't very thorough, but it should be good enough.
    def testCodeMappingEquality(self):
        m1 = Mapping('M1', 'builtin.str')
        m2 = Mapping('M2', 'builtin.str')

        cm1 = CodeMapping([m1], ())
        cm2 = CodeMapping([m1], ())
        cm3 = CodeMapping([m2], ())
        self.assertEqual(cm1, cm2)
        self.assertNotEqual(cm1, cm3)

        cm1 = CodeMapping((), [m1])
        cm2 = CodeMapping((), [m1, m2])
        cm3 = CodeMapping((), [m2])
        self.assertNotEqual(cm1, cm2)
        self.assertNotEqual(cm1, cm3)

    def testNullCodeMapping(self):
        tests = ('X', 'hello', None, 3, '', 1.2, True, False,)
        expected = Mapping(None, None)
        for t in tests:
            #self.assertIsNone(NULL_CODE_MAPPING.getMapping(t))
            self.assertEqual(expected, NULL_CODE_MAPPING.getMapping(t))

if __name__ == '__main__':
    unittest.main()
