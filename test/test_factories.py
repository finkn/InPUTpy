import unittest
from inputpy.factories import XMLFactory
from test.tools import PresetCodeMappingFactory, PresetDesignSpaceFactory

class TestFactories(unittest.TestCase):
    def testPresetCodeMappingFactory(self):
        configs = (
            'triangleMapping.xml',
            'triangleCustomAccessorMapping.xml',
            'triangleDefaultAccessorMapping.xml',
        )
        factories = (
            XMLFactory.getCodeMapping,
            PresetCodeMappingFactory.getCodeMapping,
        )

        results = []
        for factory in factories:
            results.append({config: factory(config) for config in configs})

        first = results[0]
        for result in results[1:]:
            for (k,v) in result.items():
                msg = 'Import did not match for %s' % (k)
                self.assertEqual(v, first[k], msg=msg)


    # This test is pretty crude, but maybe it's good enough?
    # Should it test design space/param store/code mapping for equality?
    def testDesignSpaceFactory(self):
        configs = (
            'simpleIntegerParameterSpace.xml',
            'advancedIntegerParameterSpace.xml',
            'simpleTriangleSpace.xml',
            'advancedTriangleSpace.xml',
        )
        factories = (
            XMLFactory.getDesignSpace,
            PresetDesignSpaceFactory.getDesignSpace,
        )
        results = []
        for factory in factories:
            results.append({config: factory(config) for config in configs})

        first = results[0]
        for result in results[1:]:
            for (k,v) in result.items():
                msg = 'Import did not match for %s' % (k)
                self.assertEqual(v, first[k], msg=msg)
