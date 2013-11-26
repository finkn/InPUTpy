"""
inputpy.param

This module exports four main classes:
    - NParam
    - SParam
    - ParamStore
    - Design
and two different factory functions for creating parameters:
    - getParameter
    - paramFactory

getParameter is low-level and picky about arguments. paramFactory is more
high-level and can infer arguments and fill in some blanks.

The module also contains a few supporting classes:
    - Identifiable
    - Param
    - ArrayParam

:copyright: (c) 2013 by Christoffer Fink.
:license: MIT. See LICENSE for details.
"""
from inputpy.util import Evaluator
import inputpy.util as util
from inputpy.util import Identifiable
from inputpy.q import *

__all__ = (
    'NParam', 'SParam', 'getParameter', 'paramFactory',
)

NPARAM_TYPES = (SHORT, INTEGER, LONG, FLOAT, DOUBLE, DECIMAL, BOOLEAN)


class Param(Identifiable):
    """
    The definition of a parameter. A parameter only knows the information
    that was used to define it. It will never have a value (with the
    exception of fixed values), and does not know how to generate
    appropriate values or even which ones would be valid.
    """
    def __init__(self, id, type, tag,
        fixed=None, parentId=None, mapping=None, dependees=[]):
        """
        - ID is always relative.
        - parent ID is always absolute.
        - dependees is a sequence of parameter IDs.
        """
        Identifiable.__init__(self, util.absolute(parentId, id))
        self.type = type
        self.fixed = fixed
        self.dependees = tuple(dependees)
        self.parentId = parentId
        self.mapping = mapping
        self.relativeId = id
        self.tag = tag

    def getDependees(self):
        """
        Return a tuple containing the IDs of any parameters that this
        parameter depends on.
        """
        return self.dependees

    def getFixedValue(self):
        """
        Return the value this parameter was fixed to, if any.
        """
        return self.fixed

    def getMapping(self):
        """
        Return any code mapping for this parameter.
        """
        return self.mapping

    def getRelativeId(self):
        """
        Return the relative ID of this parameter.
        """
        return self.relativeId

    def getType(self):
        """
        Return a string representing the type of this parameter.
        """
        return self.type

    def isDependent(self):
        """
        Return whether this parameter depends on any others.
        """
        return len(self.dependees) > 0

    def isFixed(self):
        """
        Return whether this parameter has been set to a fixed value.
        """
        return self.fixed is not None

    def setFixed(self, fixed):
        """
        Set this parameter to a fixed value. A parameter can also be
        un-fixed by passing None as the value.
        """
        self.fixed = fixed

    def __eq__(self, other):
        if other is None:
            return False
        if self.getId() != other.getId():
            return False
        if self.getType() != other.getType():
            return False
        selfDep = self.getDependees()
        otherDep = other.getDependees()
        if len(selfDep) != len(otherDep):
            return False
        for d in selfDep:
            if selfDep.count(d) != otherDep.count(d):
                return False
        if self.getFixedValue() != other.getFixedValue():
            return False
        if self.getMapping() != other.getMapping():
           return False

        return True

    def getTag(self):
        return self.tag

    def getParentId(self):
        return self.parentId

    def getNestedParameters(self):
        return ()


class NParam(Param):
    """
    This class represents numeric parameters.
    """
    def __init__(self, id, type,
            tag=NPARAM, fixed=None, parentId=None, mapping=None,
            inclMin=None, exclMin=None, inclMax=None, exclMax=None):
        """
        Raises ValueError if:
        - type is None
        - inclusive and exclusive limits are specified at the same time.

        Each of the limits can be either a single value, an expression or
        a sequence of values or expressions.
        """
        # Check arguments.
        if type is None:
            raise ValueError('The parameter type was None')
        if inclMin is not None and exclMin is not None:
            raise ValueError('Defined both inclusive and exclusive limits')
        if inclMax is not None and exclMax is not None:
            raise ValueError('Defined both inclusive and exclusive limits')

        assert type in NPARAM_TYPES, 'Invalid NParam type: %s' % (type)

        if inclMin is None:
            minTmp = exclMin
        else:
            minTmp = inclMin
        if inclMax is None:
            maxTmp = exclMax
        else:
            maxTmp = inclMax

        minTmp = self.__transformLimit(minTmp)
        maxTmp = self.__transformLimit(maxTmp)
        # Are max/min exclusive?
        minIsExcl = exclMin is not None
        maxIsExcl = exclMax is not None

        # Initialize fields.
        self.exclMin = minIsExcl
        self.exclMax = maxIsExcl
        self.minDependees = []      # Referenced parameters in min expression.
        self.maxDependees = []      # Referenced parameters in max expression.
        self.min = []
        self.max = []

        # Initialize min/max limits and dependencies.
        self.__initMinMax(self.min, self.minDependees, minTmp)
        self.__initMinMax(self.max, self.maxDependees, maxTmp)

        self.__padLimits(self.min, self.max)
        self.min = tuple(self.min)
        self.max = tuple(self.max)

        # Make intervals.
        intervals = []
        intervalTypes = {
            'short': int, 'integer': int, 'long': int,
            'float': float, 'double': float, 'decimal': float,
        }
        intervalType = intervalTypes.get(type)
        for (left, right) in zip(self.min, self.max):
            if self.exclMin:
                inclMin = None
                exclMin = left
            else:
                inclMin = left
                exclMin = None
            if self.exclMax:
                inclMax = None
                exclMax = right
            else:
                inclMax = right
                exclMax = None
            intervals.append(util.Interval(inclMin=inclMin, exclMin=exclMin,
                inclMax=inclMax, exclMax=exclMax, type=intervalType))
        self.intervals = tuple(intervals)

        self.minDependees = tuple(self.minDependees)
        self.maxDependees = tuple(self.maxDependees)

        tmp = self.minDependees + self.maxDependees
        fixed = self.__evaluateFixed(type, fixed)
        Param.__init__(self, id, type, tag, fixed, parentId, mapping, tmp)

    # Fill in missing limits with None to make all end points match.
    @staticmethod
    def __padLimits(minLimits, maxLimits):
        minLen = len(minLimits)
        maxLen = len(maxLimits)
        if minLen < maxLen:
            limits = minLimits
        else:
            limits = maxLimits
        for i in range(abs(minLen - maxLen)):
            limits.append(None)

    # Is this the best way to check whether limit is already a sequence?
    # Make sure limits are always a sequence.
    @staticmethod
    def __transformLimit(limit):
        if limit is None:
            return (None,)
        # A string is also a sequence, but it may represent one or more limits.
        if isinstance(limit, str):
            return NParam.__transformLimit(limit.split(','))
        try:
            iter(limit)
        except TypeError:
            return (limit,)
        else:
            return limit

    # Return a tuple with a single limit and multiple dependencies.
    @staticmethod
    def __getLimitAndDependencies(limit):
        dependencies = ()
        if isinstance(limit, str):
            dependencies = Evaluator.parseDependencies(limit)
            if len(dependencies) == 0:
                limit = Evaluator.evaluate(limit)
        return (limit, dependencies)

    # Updates limits and dependees.
    @staticmethod
    def __initMinMax(limits, dependees, unprocessedLimits):
        for limit in unprocessedLimits:
            result = NParam.__getLimitAndDependencies(limit)
            limits.append(result[0])
            dependees.extend(result[1])

    @staticmethod
    def __evaluateFixed(type, value):
        if isinstance(value, str):
            if type == BOOLEAN:
                return value.lower() == TRUE
            else:
                return Evaluator.evaluate(value)
        else:
            return value

    def getIntervals(self):
        return self.intervals

    def isValid(self, value, dep={}):
        for interval in self.intervals:
            if not interval.isFullyEvaluated():
                minVal = interval.getMin()
                maxVal = interval.getMax()
                if isinstance(minVal, str):
                    minVal = Evaluator.evaluate(minVal, dep)
                if isinstance(maxVal, str):
                    maxVal = Evaluator.evaluate(maxVal, dep)
                interval = interval.getUpdated((minVal, maxVal))
            if interval.contains(value):
                return True
        return False

    def setFixed(self, value):
        """
        Sets this parameter to a fixed value. A parameter can also be
        un-fixed by passing None as the value.
        Note that setting the fixed value bypasses range checks, meaning
        that whatever min/max limits have been set are completely ignored.

        Currently, expressions are allowed for numeric parameters as long
        as they do not reference other parameters.
        (InPUT4j supports neither)

        Boolean parameters do not evaluate expressions. When set to a
        string value, only 'true' (ignoring case) is True. Any other string
        is interpreted as False.

        Extends Param.setFixed.
        """
        Param.setFixed(self, self.__evaluateFixed(Param.getType(self), value))

    def isMinDependent(self):
        """
        Return whether this parameter depends on any others for defining its
        minimum value.
        """
        return len(self.minDependees) > 0

    def isMaxDependent(self):
        """
        Return whether this parameter depends on any others for defining its
        maximum value.
        """
        return len(self.maxDependees) > 0

    def getMin(self):
        """
        Return a sequence of values and/or expressions that define the lower
        limits. For any limit that depends on other parameters, the value
        will be an expression. Otherwise it will be a concrete value.
        The sequence is guaranteed to always contain at least one item. If
        the parameter does not define any lower limits at all, then the
        one and only item will be None.
        The sequence of min and max limits are guaranteed to be the same
        length. In other words, min and max are always paired up.
        """
        return self.min

    def getMax(self):
        """
        Return a sequence of values and/or expressions that define the upper
        limits. For any limit that depends on other parameters, the value
        will be an expression. Otherwise it will be a concrete value.
        The sequence is guaranteed to always contain at least one item. If
        the parameter does not define any upper limits at all, then the
        one and only item will be None.
        The sequence of min and max limits are guaranteed to be the same
        length. In other words, min and max are always paired up.
        """
        return self.max

    def isMinExclusive(self):
        """
        Return whether the lower limit is exclusive.
        """
        return self.exclMin

    def isMaxExclusive(self):
        """
        Return whether the upper limit is exclusive.
        """
        return self.exclMax

    def __eq__(self, other):
        if not Param.__eq__(self, other):
            return False
        if self.getMin() != other.getMin():
            return False
        if self.getMax() != other.getMax():
            return False
        if self.isMinExclusive() != other.isMinExclusive():
            return False
        if self.isMaxExclusive() != other.isMaxExclusive():
            return False

        return True


class SParam(Param):
    def __init__(self, id, type=None, tag=SPARAM,
            fixed=None, parentId=None, mapping=None, nested=[]):
        # Strings are a special case and don't require a mapping.
        if mapping is None and type != STRING:
            msg = 'Cannot create SParam "%s" with None mapping' % (id)
            raise ValueError(msg)
        self.nested = nested
        self.schoices = []
        self.nonchoices = []

        for p in nested:
            if p.getTag() == SCHOICE:
                self.schoices.append(p)
            else:
                self.nonchoices.append(p)

        dep = [p.getRelativeId() for p in self.nested]
        # Hack: Children inherit constructor, so they inherit dependencies.
        if len(self.schoices) == 0:
            # Hack: String type parameters have no mapping.
            if type != STRING:
                dep = dep + list(mapping.getDependencies())
        Param.__init__(self, id, type, tag, fixed, parentId, mapping, dep)

    # It is not yet clear what constitutes a valid value for SParams.
    # In particular, to what extent can the dynamic typing of Python be
    # extended to InPUTpy?
    # For now, SParams consider any value valid.
    def isValid(self, value, dep={}):
        return True

    def getNestedParameters(self):
        return self.nested

    def hasChoice(self):
        return len(self.schoices) > 0

    def getSChoices(self):
        return self.schoices

    def getRealNested(self):
        return self.nonchoices

    def __eq__(self, other):
        if not Param.__eq__(self, other):
            return False
        selfNest = self.getNestedParameters()
        otherNest = other.getNestedParameters()
        if len(selfNest) != len(otherNest):
            return False
        for p in selfNest:
            if selfNest.count(p) != otherNest.count(p):
                return False
        return True

class SChoice(SParam):
    def __init__(self, id, type=None, tag=SCHOICE, parentId=None,
            mapping=None, nested=[]):
        SParam.__init__(self, id, type, tag, parentId=parentId,
            mapping=mapping, nested=nested)


# Factory.
def getParameter(id, tag, type=None, **kwargs):
    """
    Return a parameter object that matches the arguments.
    The id may not be None. A None tag is legal but discouraged. The type
    is optional for SParams but mandatory for NParams.
    """
    paramClasses = {NPARAM: NParam, SPARAM: SParam, SCHOICE: SChoice}

    assert id is not None
    # May or may not be an array. Check the base type.
    assert util.getBaseType(type) in NPARAM_TYPES or tag != NPARAM

    # This is an array parameter.
    if type is not None and type.find('[') != -1:
        (size, type) = util.stripFirstArrayDimension(type)
        return ParamArray(id, type, tag, size, **kwargs)

    return paramClasses[tag](id, type, **kwargs)


def paramFactory(kwargs, mappings=None):
    """
    Return a parameter created from the arguments in the dictionary and
    optionally combined with a code mapping object.
    This factory is fairly flexible. Any nested parameters are expected
    to be listed recursively as dictionaries and will be properly
    created as needed. Parent IDs are inferred if missing. If the optional
    code mapping argument is provided, then any mappings that are not
    already in the dictionary will be added.

    Note: Any existing parent ID or mapping will not be replaced.
    """
    kwargs = dict(kwargs)

    paramId = kwargs[ID_ATTR]
    del kwargs[ID_ATTR]
    parentId = kwargs.get(PARENT_ID)
    absoluteId = util.absolute(parentId, paramId)

    # Infer tag if necessary.
    tag = kwargs.get(TAG)
    baseType = util.getBaseType(kwargs.get(TYPE_ATTR))
    if tag is None and baseType in NPARAM_TYPES:
        tag = NPARAM
    elif tag is None:
        tag = SPARAM
    kwargs[TAG] = tag

    # Create nested parameters recursively.
    nested = kwargs.get(NESTED)
    if nested is not None:
        for param in nested:
            param[PARENT_ID] = absoluteId
        kwargs[NESTED] = [paramFactory(args, mappings) for args in nested]

    # Make sure that existing mappings are not replaced.
    if MAPPING_ATTR not in kwargs:
        kwargs[MAPPING_ATTR] = mappings.getMapping(absoluteId)

    if tag == SCHOICE:
        # Another hack:
        # String SParams have no mapping for SChoice children to inherit.
        parentMapping = mappings.getMapping(parentId)
        if parentMapping is not None:
            kwargs[MAPPING_ATTR] = mappings.getInherited(absoluteId, parentId)
        # Assume a missing mapping means string type.
        else:
            kwargs[TYPE_ATTR] = STRING

    return getParameter(paramId, **kwargs)


def choiceFactory(sparam):
    # Any non-choice sparam are returned unchanged.
    if sparam.getTag() != SPARAM:
        return sparam
    elif not sparam.hasChoice():
        return sparam

    realParams = []
    choiceParams = []
    for p in sparam.getNestedParameters():
        if p.getTag() == SCHOICE:
            choiceParams.append(p)
        else:
            realParams.append(p)

    choices = []
    paramId = sparam.getId()
    parentId = util.parent(paramId)
    for p in choiceParams:
        nested = list(realParams) + [p]

        kwargs = {
            ID_ATTR: paramId, TAG: SPARAM, TYPE_ATTR: sparam.getType(),
            PARENT_ID: parentId, MAPPING_ATTR: sparam.getMapping(),
            NESTED: nested,
        }
        choices.append(SParam(**kwargs))

    return Choice(sparam, choices)


class Choice():
    def __init__(self, sparam, choices):
        self.choices = choices
        self.original = sparam
        dep = []
        for p in choices:
            for d in p.getDependees():
                dep.append(d)
        self.dep = tuple(set(dep))

    def getChoices(self):
        return self.choices

    def getChoice(self, paramId):
        for c in self.choices:
            for n in c.getSChoices():
                if n.getRelativeId() == paramId:
                    return c
        assert False, 'Unable to find choice %s in %s' % (paramId, self.getId())

    def getId(self):
        return self.original.getId()

    def getTag(self):
        return CHOICE

    def getType(self):
        return self.original.getType()

    def getDependees(self):
        return self.dep

    def getParentId(self):
        return self.original.getParentId()

    def getFixedValue(self):
        return self.original.getFixedValue()

    def getMapping(self):
        return self.original.getMapping()

    def getNestedParameters(self):
        return self.original.getNestedParameters()

    def isDependent(self):
        return len(self.dep) > 0

    def getOriginal(self):
        return self.original

    def isFixed(self):
        return self.original.isFixed()

    def isValid(self, value, dep={}):
        return self.original.isValid(value, dep)

    def __eq__(self, other):
        if not isinstance(other, Choice):
            return False
        if self.getId() != other.getId():
            return False
        if self.original != other.original:
            return False
        if self.choices != other.choices:
            return False
        return True


class ParamArray():
    """
    This is a special kind of parameter. It is a kind of wrapper that
    adds the quality of being an array to any parameter.
    Multidimensional arrays are handled by wrapping multiple parameters
    recursively.

    Almost all method calls end up at the actual parameter. This class
    only adds two new methods:
    - getSize
    - getParameter
    And overrides one method:
    - getType
    """
    def __init__(self, paramId, paramType, tag, size, **kwargs):
        # Convert to choice on the fly as needed.
        self.__param = choiceFactory(getParameter(paramId, tag, paramType, **kwargs))
        self.__size = size
        assert self.__param is not None

    def __getattr__(self, attr):
        return getattr(self.__param, attr)

    def getTag(self):
        return ARRAY

    def getSize(self):
        """
        Return the size of this array. A size of 0 means that the size is
        unspecified.
        """
        return self.__size

    def getParameter(self):
        """
        Return the parameter that this array should have elements of.
        """
        return self.__param

    # Array validation is a little tricky.
    # There is no spec for this. Additionally, the "original" InPUT4j that
    # I started porting did no validation.
    def isValid(self, value, dep={}):
        return True

        if len(value) != self.__size and self.__size != 0:
            return False
        for element in value:
            if not self.__param.isValid(element, dep):
                return False
        return True

    def __eq__(self, other):
        if not isinstance(other, ParamArray):
            return False
        if self.getSize() != other.getSize():
            return False
        return self.getParameter() == other.getParameter()
