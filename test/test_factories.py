"""
:copyright: (c) 2013 by Christoffer Fink.
:license: MIT. See LICENSE for details.
"""
import unittest
from inputpy.factories import XMLFactory
from test.factories import PresetCodeMappingFactory, PresetDesignSpaceFactory
from test.factories import PresetDesignFactory
#from test.factories import *

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
            'simpleIntegerSpace.xml',
            'advancedIntegerParameterSpace.xml',
            'simpleTriangleSpace.xml',
            'advancedTriangleSpace.xml',
            'choiceSpace.xml',
            'arraySpace.xml',
            'simpleStructuredSpace.xml',
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
                # v is from a preset factory, first[k] is from an XML factory
                self.assertEqual(v, first[k], msg=msg)


    def testDesignFactory(self):
        configs = (
            'simpleIntegerDesign.xml',
            'simpleStructuredDesign.xml',
            'choiceDesign.xml',
            'arrayDesign.xml',
        )
        factories = (
            XMLFactory.getDesign,
            PresetDesignFactory.getDesign,
        )

        results = []
        for factory in factories:
            results.append({config: factory(config) for config in configs})

        first = results[0]
        for result in results[1:]:
            for (k,v) in result.items():
                msg = 'Import did not match for %s' % (k)
                self.assertEqual(v, first[k], msg=msg)


if __name__ == '__main__':
    unittest.main()
