"""
This module primarily exports two functions:
    - isValid
    - nextValue

The generators have to be compatible with the Java version. While Python
only has one int and one float type, capable of representing arbitrary
precision, Java has 4 integer types (3 of which are supported by InPUT)
and 3 floating point types. Therefore, this module exports constants
defining the min and max ranges for those types.
"""
import random
from inputpy.exceptions import InPUTException
from inputpy.util import Evaluator

# Constants for type names.
SHORT = 'short'
INTEGER = 'integer'
LONG = 'long'
FLOAT = 'float'
DOUBLE = 'double'
NUMERIC = 'numeric'
BOOLEAN = 'boolean'

# Maps the string description to a range.
RANGE_MAP = {
    # Integer types.
    SHORT: (-2**16, 2**16-1),
    INTEGER: (-2**32, 2**32-1),
    LONG: (-2**64, 2**64-1),
    # Floating point types.
    FLOAT: (-2**32, 2**32-1),
    DOUBLE: (-2**64, 2**64-1),
    NUMERIC: (-2**128, 2**128-1), # Not 100% about this.
}

INT_TYPES = (SHORT, INTEGER, LONG,)
FLOAT_TYPES = (FLOAT, DOUBLE, NUMERIC,)

class ValueGenerator:
    rng = random

    @classmethod
    def nextValue(cls, param, dep={}):
        raise NotImplementedError

    @classmethod
    def isValid(cls, param, dep={}):
        raise NotImplementedError

    @classmethod
    def __getMinMax__(cls, param, dep={}):
        minVal = param.getMin()
        if param.isMinDependent():
            minVal = Evaluator.evaluate(minVal, dep)
        maxVal = param.getMax()
        if param.isMaxDependent():
            maxVal = Evaluator.evaluate(maxVal, dep)
        if minVal is None:
            minVal = RANGE_MAP[param.getType()][0]
        if maxVal is None:
            maxVal = RANGE_MAP[param.getType()][1]
        return (minVal, maxVal)

class IntGenerator(ValueGenerator):
    @classmethod
    def nextValue(cls, param, dep={}):
        (minVal, maxVal) = cls.__getMinMax__(param, dep)
        if not cls.__isValid(minVal, maxVal):
            raise ValueError('Invalid range')
        return cls.rng.randint(minVal, maxVal)

    @classmethod
    def isValid(cls, param, dep={}):
        (minVal, maxVal) = cls.__getMinMax__(param, dep)
        return cls.__isValid(minVal, maxVal)

    @classmethod
    def __getMinMax__(cls, param, dep={}):
        (minVal, maxVal) = ValueGenerator.__getMinMax__(param, dep)
        if param.isMinExclusive():
            minVal += 1
        if param.isMaxExclusive():
            maxVal -= 1
        return (minVal, maxVal)

    # A helper that is specific to this class.
    @classmethod
    def __isValid(cls, minVal, maxVal):
        return maxVal >= minVal


class FloatGenerator(ValueGenerator):
    @classmethod
    def nextValue(cls, param, dep={}):
        (minVal, maxVal) = cls.__getMinMax__(param, dep)
        if not cls.isValid(param, dep):
            raise ValueError('Invalid range')
        return cls.rng.uniform(minVal, maxVal)

    @classmethod
    def isValid(cls, param, dep={}):
        (minVal, maxVal) = cls.__getMinMax__(param, dep)
        return cls.__isValid(param, minVal, maxVal)

    # A helper that is specific to this class.
    @classmethod
    def __isValid(cls, param, minVal, maxVal):
        excl = param.isMinExclusive() or param.isMaxExclusive()
        return (maxVal > minVal) or (maxVal >= minVal and not excl)


class BoolGenerator(ValueGenerator):
    @classmethod
    def nextValue(cls, param, dep={}):
        return bool(cls.rng.randint(0, 1))

    @classmethod
    def isValid(cls, param, dep={}):
        return True


GENERATORS = {}
for k in INT_TYPES:
    GENERATORS[k] = IntGenerator
for k in FLOAT_TYPES:
    GENERATORS[k] = FloatGenerator
GENERATORS[BOOLEAN] = BoolGenerator

def nextValue(param, dep={}):
    """
    Return a value for the parameter. Optionally, a dictionary of
    parameter ID to value mappings can be supplied to resolve dependencies.
    """
    return GENERATORS[param.getType()].nextValue(param, dep)

def isValid(param, dep={}):
    """
    Return whether the parameter is valid. Optionally, a dictionary of
    parameter ID to value mappings can be supplied to resolve dependencies.
    """
    return GENERATORS[param.getType()].isValid(param, dep)
