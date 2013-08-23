import unittest
from test.test_design_space import TestDesignSpace
from test.test_param import TestParam
from test.test_param_store import TestParamStore
from test.test_design import TestDesign
from test.test_util import TestEvaluator
from test.test_util import TestMiscUtil
from test.test_generators import TestGenerators
from test.test_mapping import TestMapping

__all__ = (
    'TestDesign', 'TestDesignSpace', 'TestParam', 'TestParamStore',
    'TestEvaluator', 'TestMiscUtil', 'TestGenerators', 'TestMapping',
)

if __name__ == '__main__':
    unittest.main()
