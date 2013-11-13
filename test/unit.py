"""
:copyright: (c) 2013 by Christoffer Fink.
:license: MIT. See LICENSE for details.
"""
import unittest
from test.test_design import TestDesign
from test.test_design_space import TestDesignSpace
from test.test_factories import TestFactories
from test.test_generators import TestGenerators
from test.test_mapping import TestMapping
from test.test_param import TestParam
from test.test_param_store import TestParamStore
from test.test_types import TestTypes
from test.test_util import TestEvaluator, TestMiscUtil, TestInterval
from test.test_array_space import TestArraySpace
from test.test_tools import TestTools
from test.test_choice import TestChoice

__all__ = (
    'TestDesign', 'TestDesignSpace', 'TestParam', 'TestParamStore',
    'TestEvaluator', 'TestMiscUtil', 'TestGenerators', 'TestMapping',
    'TestTypes', 'TestFactories', 'TestArraySpace', 'TestChoice',
    'TestTools', 'TestInterval',
)

if __name__ == '__main__':
    unittest.main()
