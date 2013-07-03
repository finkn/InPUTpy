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

SCHEMA_LOCATION_ATTR = "schemaLocation"
MY_NAMESPACE_PREFIX = "in"
NAMESPACE_ID = "http://TheInPUT.org/"
XML = ".xml"
XSD = ".xsd"        # Specific to InPUTpy
DESIGN_ROOT = "Design"
DESIGN_SPACE_ROOT = "DesignSpace"
DESIGN_NAMESPACE_ID = NAMESPACE_ID + DESIGN_ROOT;
NVALUE = "NValue"
SVALUE = "SValue"
NPARAM = "NParam"
SPARAM = "SParam"
SCHOICE = "SChoice"
SCHOICE_TYPE = "SChoiceType"
VALUE_ATTR = "value"
TYPE_ATTR = "type"
ID_ATTR = "id"
MAPPING = "Mapping"
MAPPING_TYPE = "MappingType"
SETTER_PREFIX = "set"
GETTER_PREFIX = "get"
RNG = "rng"
SEED = "Seed"
EXCL_MIN = "exclMin"
EXCL_MAX = "exclMax"
INCL_MIN = "inclMin"
INCL_MAX = "inclMax"
GET_ATTR = "get"
SET_ATTR = "set"
CONSTR_ATTR = "constructor"
WRAPPER = "Wrapper"
ALGORITHM_DESIGN_SPACE = "algorithmSpace"
ALGORITHM_DESIGN_SPACE_XML = ALGORITHM_DESIGN_SPACE + XML
PROBLEM_FEATURES = "problemFeatures"
PROBLEM_FEATURE_SPACE = "problemSpace"
OUTPUT = "output"
CODE_MAPPING = "codeMapping"
RANDOM = "random"
FIXED_ATTR = "fixed"
MAPPING_ATTR = "mapping"
LOGGING = "logging"
THREAD_SAFE = "threadSafe"
INJECTION = "injection"
REF_ATTR = "ref"
SYSTEM = "System"
LANGUAGE = "Language"
JAVA = "java"
DEFAULT = "default"
COMPLEX = "complex"
ADD_ATTR = "add"
EXP = ".exp"
INP = ".inp"
CONFIG_ID = "config"
CONFIG = CONFIG_ID + XML
SCHEMA_PATH = "schemaPath"
RUNTIME_VALIDATION = "runtimeValidation"
STRING = "String"
STRING_TYPE = "java.lang.String"    # ??? How will this work in InPUTpy?
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
