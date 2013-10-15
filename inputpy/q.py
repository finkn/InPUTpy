"""
inputpy.Q

A helper module that contains all the identifiers of objects and concepts used
in InPUT. References should all point here, and no String that are meaningful
for InPUT should be solely defined in another class.

This set of constants isn't complete, relative to the Q class in the original
Java version.

:copyright: (c) 2013 by Christoffer Fink.
:license: MIT. See LICENSE for details.
"""

from inputpy import config

# InPUTpy-specific additions.
XSD = '.xsd'
SHORT = 'short'
INTEGER = 'integer'
LONG = 'long'
FLOAT = 'float'
DOUBLE = 'double'
DECIMAL = 'decimal'
BOOLEAN = 'boolean'
ARRAY = 'array'

# XML elements.
DESIGN_ROOT = 'Design'
DESIGN_SPACE_ROOT = 'DesignSpace'
NVALUE = 'NValue'
SVALUE = 'SValue'
NPARAM = 'NParam'
SPARAM = 'SParam'
SCHOICE = 'SChoice'
SCHOICE_TYPE = 'SChoiceType'
MAPPING = 'Mapping'
MAPPING_TYPE = 'MappingType'
WRAPPER = 'Wrapper'

# XML attributes.
ADD_ATTR = 'add'
VALUE_ATTR = 'value'
TYPE_ATTR = 'type'
ID_ATTR = 'id'
EXCL_MIN = 'exclMin'
EXCL_MAX = 'exclMax'
INCL_MIN = 'inclMin'
INCL_MAX = 'inclMax'
GET_ATTR = 'get'
SET_ATTR = 'set'
CONSTR_ATTR = 'constructor'
FIXED_ATTR = 'fixed'
MAPPING_ATTR = 'mapping'
REF_ATTR = 'ref'

# Misc. XML.
SCHEMA_LOCATION_ATTR = 'schemaLocation'
MY_NAMESPACE_PREFIX = 'in'
NAMESPACE_ID = 'http://TheInPUT.org/'
DESIGN_NAMESPACE_ID = NAMESPACE_ID + DESIGN_ROOT;
XML = '.xml'

SETTER_PREFIX = "set"
GETTER_PREFIX = "get"
RNG = "rng"
SEED = "Seed"
ALGORITHM_DESIGN_SPACE = "algorithmSpace"
ALGORITHM_DESIGN_SPACE_XML = ALGORITHM_DESIGN_SPACE + XML
PROBLEM_FEATURES = "problemFeatures"
PROBLEM_FEATURE_SPACE = "problemSpace"
OUTPUT = "output"
CODE_MAPPING = "codeMapping"
RANDOM = "random"
LOGGING = "logging"
THREAD_SAFE = "threadSafe"
INJECTION = "injection"
SYSTEM = "System"
LANGUAGE = "Language"
JAVA = "java"
DEFAULT = "default"
COMPLEX = "complex"
EXP = ".exp"
INP = ".inp"
CONFIG_ID = "config"
CONFIG = CONFIG_ID + XML
SCHEMA_PATH = "schemaPath"
RUNTIME_VALIDATION = "runtimeValidation"
STRING = "String"
STRING_TYPE = "builtins.str"
BLANK = None                        # ??? This is Void.TYPE in InPUT4j.
EVALUATOR = "evaluator"
NULL = "null"
CACHE_DESIGNS = "cacheDesigns"

DESIGN_ELEMENT_IDS = (
    NVALUE, SVALUE, DESIGN_ROOT,
)
DESIGN_SPACE_ELEMENT_IDS = (
    NPARAM, SCHOICE, SCHOICE_TYPE, SPARAM, DESIGN_SPACE_ROOT,
)

def getSchemaLocation():
    s = DESIGN_NAMESPACE_ID + config.getValue(SCHEMA_PATH) + DESIGN_ROOT + XSD
    return s
