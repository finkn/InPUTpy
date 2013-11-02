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
from inputpy.util import initOrder, Evaluator
import inputpy.generators as generator
import inputpy.util as util
from inputpy.q import *
# Only needed by Design.
from inputpy.exceptions import InPUTException

__all__ = (
    'Identifiable', 'NParam', 'SParam',
    'getParameter', 'paramFactory', 'Design',
)

NPARAM_TYPES = (SHORT, INTEGER, LONG, FLOAT, DOUBLE, DECIMAL, BOOLEAN)

class Identifiable:
    """
    This class is a mixin. It provides all subclasses with a getId() method.
    An instance can be initialized using an id argument. If none is
    provided, then a unique id will be constructed automatically.
    """
    def __init__(self, objId=None):
        self.__id = objId or str(id(self))

    def getId(self):
        return self.__id


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

        assert type in NPARAM_TYPES

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
        # A string is also a sequence, but it always represents a single limit.
        if isinstance(limit, str):
            return (limit,)
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
        kwargs[MAPPING_ATTR] = mappings.getInherited(absoluteId, parentId)

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

    # TODO:
    # This shouldn't be needed anymore.
    def getType(self):
        """
        Always returns inputpy.q.ARRAY.
        """
        return ARRAY

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

    def __eq__(self, other):
        if not isinstance(other, ParamArray):
            return False
        if self.getSize() != other.getSize():
            return False
        return self.getParameter() == other.getParameter()


def transformParameters(paramDict):
    return {k: choiceFactory(v) for (k,v) in paramDict.items()}

def getTopLevelParameters(parameters):
    return list(filter(lambda p: p.getParentId() is None, parameters))


class ParamStore:
    def __init__(self, params=()):
        """
        The params argument is optional. It can be a single parameter or a
        sequence of multiple parameters. Parameters can be added until the
        ParamStore is finalized.
        """
        self.__params = {}            # ID-to-Param mapping.
        self.__dep = {}               # ID-to-IDs mapping.
        self.__finalized = False
        self.addParam(params)

    # Assumes that params is a sequence of parameters. If it turns out to be
    # a single parameter it is placed in a sequence before processing.
    def addParam(self, param):
        """
        Add one or more parameters to this ParamStore. The params argument
        can be a sequence of parameters or just a single parameter.

        Raises NotImplementedError if this ParamStore has been finalized.
        """
        if self.__finalized:
            msg = 'Cannot add parameters to store once finalized.'
            raise NotImplementedError(msg)

        try:
            for p in param:
                self.addParam(p)
        except TypeError:
            msg = 'Parameter %s already exists' % (param.getId())
            assert not param.getId() in self.__params, msg

            self.__params[param.getId()] = param
            self.__dep[param.getId()] = param.getDependees()
            self.addParam(param.getNestedParameters())

    def getParam(self, paramId):
        """
        Returns the parameter with the given ID.
        """
        return self.__params[paramId]

    def setFixed(self, paramId, value):
        self.__params[paramId].setFixed(value)

    def finalize(self):
        """
        Do any final processing and make the parameter store effectively
        read-only. No more parameters can be added later. Multiple calls
        will have no effect.

        Raises ValueError if:
        - There are unmet dependencies. (A referenced parameter is missing.)
        - There are circular dependencies.
        - Any independent parameters have invalid ranges.
        """
        if self.__finalized:
            return
        self.__params = transformParameters(self.__params)
        self.__topLevel = getTopLevelParameters(self.__params.values())
        # Update dependencies so that all are absolute.
        self.__dep = util.getAbsoluteDependencies(self.__params)#, self.__dep)

        # The order of these two calls (__validateParamters and initOrder)
        # is significant.
        self.__validateParameters()
        self.initOrder = initOrder(self.__dep)
        self.__finalized = True

    def getInitializationOrder(self):
        """
        Return a dictionary that maps the initialization order to the
        matching parameter IDs.

        Example:
        A return value of {0: ['A', 'B'], 1: ['C']} means that A and B must
        be initialized before C (because C depends on one or more of (A,B)).

        The method requires that this parameter store is finalized. Calling
        this method will force finalization if not already done.
        """
        if not self.__finalized:
            self.finalize()
        return self.initOrder

    def getParameters(self):
        """
        Return a dictionary mapping parameter IDs to Param objects.
        """
        return self.__params

    def getSupportedParamIds(self):
        """
        Return the parameter IDs for all parameters stored here.
        """
        return self.__params.keys()

    def getTopLevelParameters(self):
        return self.__topLevel

    def __validateParameters(self):
        """
        Check that all parameters are valid.
        - All independent ranges are valid.
        - All dependencies can be met (referenced parameters exist).
        """
        # Check ranges.
        for (paramId, param) in self.__params.items():
            if not self.__validRange(param):
                raise ValueError('Empty value range')

        # Check for unmet dependencies.
        for (paramId, param) in self.__params.items():
            if not param.isDependent():
                continue
            d = self.__missingDep(param)
            if d:
                msg = '%s referencing nonexistent parameter %s' % (paramId, d)
                raise ValueError(msg)

    # This test isn't as thorough as it could be. It only checks completely
    # independent parameters.
    def __validRange(self, param):
        if param.isDependent():
            return True     # Don't know that it's invalid at least.
        return generator.isValid(param)

    # Is this function superfluous now?
    def __missingDep(self, param):
        """
        Return any unmet dependency. That is, any referenced parameter that
        doesn't exist.
        """
        dependees = param.getDependees()
        context = param.getId()
        ids = self.__params.keys()
        for d in dependees:
            d = util.findAbsoluteParameter(context, d, ids)
            if d is None:
                return d
        return None


class Design(Identifiable):
    def __init__(self, params, designSpace=None, designId=None, readOnly=False):
        Identifiable.__init__(self, designId)
        self.params = params
        self.__readOnly = readOnly
        self.__ext = [self]
        self.space = designSpace

    def getValue(self, paramId):
        result = None
        for d in self.__ext:
            result = util.getValue(paramId, d.params)
            if result is not None:
                return result

    def setValue(self, paramId, value):
        if self.__readOnly:
            raise InPUTException('Cannot set value on a read-only Design')
        util.setValue(paramId, self.params, value)

    def setReadOnly(self):
        self.__readOnly = True

    # Not sure if these special cases should raise an exception or if the
    # operation should simply be ignored.
    def extendScope(self, design):
        if design is None:
            raise InPUTException('Cannot extend design with None')
        # This case is automatically handled by the next one, but checking
        # this explicitly allows for a more informative error message.
        if design is self:
            raise InPUTException('Cannot extend design with itself')
        if design in self.__ext:
            raise InPUTException('The design is already extending this design')
        self.__ext.append(design)

    def getSpace(self):
        return self.space

    def getSupportedParamIds(self):
        return self.params.keys()

    # -------------------------------------------------------------------------
    # These are dummy implementations, taken from the first version of Design.
    # -------------------------------------------------------------------------
    def export(self, exporter):
        pass

    # Unsure of what exactly same does.
    def same(self, design):
        pass
    # -------------------------------------------------------------------------
