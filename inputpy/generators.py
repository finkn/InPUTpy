"""
This module primarily exports two functions:
    - isValid
    - nextValue

It also exports value generators, but these are probably best accessed
using the two main functions of this module.

:copyright: (c) 2013 by Christoffer Fink.
:license: MIT. See LICENSE for details.
"""
import random
from inputpy.exceptions import InPUTException
from inputpy.util import Evaluator
from inputpy import mapping
from inputpy.q import SHORT, INTEGER, LONG
from inputpy.q import FLOAT, DOUBLE, DECIMAL
from inputpy.q import BOOLEAN, ARRAY, SPARAM

__all__ = (
    'isValid', 'nextValue',
    'IntGenerator', 'FloatGenerator', 'ArrayGenerator', 'SParamGenerator',
)

# Maps the string description to a range.
RANGE_MAP = {
    # Integer types.
    SHORT: (-2**16, 2**16-1),
    INTEGER: (-2**32, 2**32-1),
    LONG: (-2**64, 2**64-1),
    # Floating point types.
    FLOAT: (-2**32, 2**32-1),
    DOUBLE: (-2**64, 2**64-1),
    DECIMAL: (-2**128, 2**128-1), # Not 100% about this.
}

INT_TYPES = (SHORT, INTEGER, LONG,)
FLOAT_TYPES = (FLOAT, DOUBLE, DECIMAL,)

class ValueGenerator:
    rng = random

    @classmethod
    def nextValue(cls, param, dep={}):
        if param.isFixed():
            return param.getFixedValue()
        else:
            return None

    @classmethod
    def isValid(cls, param, dep={}):
        raise NotImplementedError

    @classmethod
    def __getMinMax__(cls, param, dep={}):
        minVal = param.getMin()
        maxVal = param.getMax()
        minMaxPairs = list(zip(minVal, maxVal))
        (minVal, maxVal) = cls.rng.choice(minMaxPairs)

        if param.isMinDependent() and isinstance(minVal, str):
            minVal = Evaluator.evaluate(minVal, dep)
        if param.isMaxDependent() and isinstance(maxVal, str):
            maxVal = Evaluator.evaluate(maxVal, dep)
        if minVal is None:
            minVal = RANGE_MAP[param.getType()][0]
        if maxVal is None:
            maxVal = RANGE_MAP[param.getType()][1]
        return (minVal, maxVal)

class IntGenerator(ValueGenerator):
    @classmethod
    def nextValue(cls, param, dep={}):
        result = ValueGenerator.nextValue(param, dep)
        if result is not None:
            return result

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
        result = ValueGenerator.nextValue(param, dep)
        if result is not None:
            return result

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
        result = ValueGenerator.nextValue(param, dep)
        if result is not None:
            return result

        return bool(cls.rng.randint(0, 1))

    @classmethod
    def isValid(cls, param, dep={}):
        return True

class ArrayGenerator(ValueGenerator):
    @classmethod
    def nextValue(cls, param, dep={}):
        size = param.getSize() or 1
        param = param.getParameter()
        return [nextValue(param, dep) for i in range(size)]

    @classmethod
    def isValid(cls, param, dep={}):
        return True

class SParamGenerator(ValueGenerator):
    @classmethod
    def nextValue(cls, param, dep={}):
        args = []
        paramMapping = param.getMapping()
        for d in paramMapping.getDependencies():
            args.append(dep[d])

        # TODO:
        # Update Mapping to make getType return the actual type.
        t = mapping.getType(paramMapping.getTypeName())

        # Create instance with any constructor arguments.
        tmp = t(*args)
        # Now set any remaining nested parameters with setters.
        dependencies = paramMapping.getDependencies()
        for p in param.getNestedParameters():
            if p.getRelativeId() in dependencies:
                continue
            depMapping = p.getMapping()
            setter = tmp.__getattribute__(depMapping.getSetter())
            setter(dep[p.getRelativeId()])
        return tmp

    @classmethod
    def isValid(cls, param, dep={}):
        return True    # Is it?


GENERATORS = {}
for k in INT_TYPES:
    GENERATORS[k] = IntGenerator
for k in FLOAT_TYPES:
    GENERATORS[k] = FloatGenerator
GENERATORS[BOOLEAN] = BoolGenerator
GENERATORS[ARRAY] = ArrayGenerator
GENERATORS[SPARAM] = SParamGenerator

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

def nextArray(param, sizes=(0,), dep={}):
    """
    Return an array of values initialized using the parameter.
    The default size of the array is 1. By passing in a list of sizes, the
    array can have any dimensions. Any size that is 0 will default back
    to 1.
    A dictionary of parameter ID to value mappings can be supplied to
    resolve dependencies.
    """
    values = sizes[0] or 1
    sizes = sizes[1:]
    if len(sizes) > 0:
        return [nextArray(param, sizes, dep) for i in range(values)]
    else:
        return [nextValue(param, dep) for i in range(values)]
