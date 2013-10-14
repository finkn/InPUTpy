import unittest
from inputpy.factories import XMLFactory
from test.tools import PresetCodeMappingFactory
from test.tools import PresetDesignSpaceFactory

class TestFactories(unittest.TestCase):
    def testPresetCodeMappingFactory(self):
        config = 'triangleMapping.xml'
        factories = (
            XMLFactory.getCodeMapping,
            PresetCodeMappingFactory.getCodeMapping,
        )

        for factory in factories:
            mapping = factory(config)

            outerP1 = mapping.getMapping('P1')
            nestedP1 = mapping.getMapping('T1.P1')
            triangle = mapping.getMapping('T1')

            self.assertEqual('P1', outerP1.getId())
            self.assertEqual('test.types.geo.Point', outerP1.getTypeName())
            self.assertEqual('T1.P1', nestedP1.getId())
            self.assertEqual('test.types.geo.Point', nestedP1.getTypeName())
            self.assertEqual('T1', triangle.getId())
            self.assertEqual('test.types.geo.Triangle', triangle.getTypeName())
            self.assertEqual('P1 P2 P3', triangle.getConstructor())

            self.assertCountEqual(('X', 'Y'), outerP1.getDependencies())

    # This test is pretty crude, but maybe it's good enough?
    # Should it test design space/param store/code mapping for equality?
    def testDesignSpaceFactory(self):
        configs = (
            'simpleTriangleSpace.xml',
            'advancedTriangleSpace.xml',
        )
        factories = (
            XMLFactory.getDesignSpace,
            PresetDesignSpaceFactory.getDesignSpace,
        )
        expectedParamIds = ('X', 'Y', 'P1', 'P4', 'T1', 'T1.P1', 'T1.P1.X',)
        # Make sure nested parameters don't "leak" out.
        nonexistentParamIds = ('P2', 'T1.P4',)

        for config in configs:
            for factory in factories:
                space = factory(config)
                ids = space.getSupportedParamIds()
                for p in expectedParamIds:
                    self.assertIn(p, ids)
                for p in nonexistentParamIds:
                    self.assertNotIn(p, ids)
