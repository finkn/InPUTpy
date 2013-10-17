import unittest
from test.test_design import TestDesign
from test.test_design_space import TestDesignSpace
from test.test_factories import TestFactories
from test.test_generators import TestGenerators
from test.test_mapping import TestMapping
from test.test_param import TestParam
from test.test_param_store import TestParamStore
from test.test_types import TestTypes
from test.test_util import TestEvaluator, TestMiscUtil

__all__ = (
    'TestDesign', 'TestDesignSpace', 'TestParam', 'TestParamStore',
    'TestEvaluator', 'TestMiscUtil', 'TestGenerators', 'TestMapping',
    'TestTypes', 'TestFactories',
)

if __name__ == '__main__':
    unittest.main()
