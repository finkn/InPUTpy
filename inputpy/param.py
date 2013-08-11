from inputpy.util import Evaluator
from inputpy.util import initOrder
import inputpy.generators as generator

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
    The parameter class is pretty dumb. It represents the definition of a
    parameter as opposed to an actual parameter. This means that it knows
    only the information that was used to define it. It will never have a
    value (with the exception of fixed values), and does not know how to
    generate appropriate values or even which ones would be valid.
    """
    def __init__(self, paramId, paramType, fixed=None,
            inclMin=None, exclMin=None, inclMax=None, exclMax=None):

        # Check arguments.
        if paramType is None:
            raise ValueError('The parameter type was None')
        if inclMin is not None and exclMin is not None:
            raise ValueError('Defined both inclusive and exclusive limits')
        if inclMax is not None and exclMax is not None:
            raise ValueError('Defined both inclusive and exclusive limits')

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
        Identifiable.__init__(self, paramId)
        self.type = paramType
        self.exclMin = minIsExcl
        self.exclMax = maxIsExcl
        self.minDependees = []      # Referenced parameters in min expression.
        self.maxDependees = []      # Referenced parameters in max expression.
        self.min = []
        self.max = []

        for minLimit in minTmp:
            self.__initMinMax(self.min, self.minDependees, minLimit)
        for maxLimit in maxTmp:
            self.__initMinMax(self.max, self.maxDependees, maxLimit)

        self.__padLimits(self.min, self.max)
        self.min = tuple(self.min)
        self.max = tuple(self.max)
        self.minDependees = tuple(self.minDependees)
        self.maxDependees = tuple(self.maxDependees)

        # Set fixed value, if any.
        self.setFixed(fixed)

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

    @staticmethod
    def __initMinMax(limits, dependees, limit):
        # If min/max are expressions, these will be parsed to find
        # dependencies. If the expression does not contain references to any
        # other parameters, then the expression is evaluated immediately.
        # Any dependencies are recorded.

        if type(limit) is str:
            dependees.extend(Evaluator.parseDependencies(limit))
            if len(dependees) == 0:
                limit = Evaluator.evaluate(limit)
        limits.append(limit)

    def isFixed(self):
        """
        Return whether this parameter has been set to a fixed value.
        """
        return self.fixed is not None

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
        """
        if type(value) is str:
            if self.type == 'boolean':
                self.fixed = value.lower() == 'true'
                return
            self.fixed = Evaluator.evaluate(value)
        else:
            self.fixed = value

    def getFixedValue(self):
        """
        Return the value this parameter was fixed to, if any.
        """
        return self.fixed

    def isDependent(self):
        """
        Return whether this parameter depends on any others.
        """
        return self.isMinDependent() or self.isMaxDependent()

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

    def getType(self):
        """
        Return a string containing the type this parameter was defined with.
        For example, for an integer parameter (defined with type='integer')
        the return value will be 'integer'.
        """
        return self.type

    def getMin(self):
        """
        Return the value or expression that is the lower limit.
        If this parameter depends on others, then the returned value will be
        an expression. Otherwise it will be a concrete value.
        """
        return self.min

    def getMax(self):
        """
        Return the value or expression that is the upper limit.
        If this parameter depends on others, then the returned value will be
        an expression. Otherwise it will be a concrete value.
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

    def getDependees(self):
        """
        Return a tuple containing the IDs of any parameters that this
        parameter depends on.
        """
        return tuple(self.minDependees + self.maxDependees)

class ParamStore:
    def __init__(self, params=None):
        """
        The params argument is optional. It can be a single parameter or a
        sequence of multiple parameters. Parameters can be added until the
        ParamStore is finalized.
        """
        self.__params = {}            # ID-to-Param mapping.
        self.__dep = {}               # ID-to-IDs mapping.
        self.__finalized = False
        if params is not None:
            self.addParam(params)

    # Assumes that params is a sequence of parameters. If it turns out to be
    # a single parameter it is placed in a sequence before processing.
    def addParam(self, params):
        """
        Add one or more parameters to this ParamStore. The params argument
        can be a sequence of parameters or just a single parameter.

        Raises NotImplementedError if this ParamStore has been finalized.
        """
        if self.__finalized:
            msg = 'Cannot add parameters to store once finalized.'
            raise NotImplementedError(msg)
        if isinstance(params, Param):
            params = (params,)
        for p in params:
            paramId = p.getId()
            self.__params[paramId] = p
            # Update dependencies as new parameters are added.
            self.__dep[paramId] = p.getDependees()

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

    def __missingDep(self, param):
        """
        Return any unmet dependency. That is, any referenced parameter that
        doesn't exist.
        """
        dependees = param.getDependees()
        for d in dependees:
            if not d in self.__params:
                return d
        return False


class DesignSpace(Identifiable):
    """
    The design space contains a set of parameters and is capable of
    generating designs by initializing these parameters.

    A design space is mostly immutable(*):
    - No parameters can be added to an existing design space.
    - Parameters cannot be removed from the design space.
    - Parameters cannot be modified(*).
    - No internal state exists, apart from the set of parameters.
      This means that, initializing parameters (whether single parameters,
      using next(), or the full set, using nextDesign()), does not have side
      effects.

    * Parameters can be set to a fixed value though. That's the only
      mutability exception.
    """

    def __init__(self, paramStore, spaceId=None):
        Identifiable.__init__(self, spaceId)
        self.params = paramStore or ParamStore()
        self.params.finalize()

    def getSupportedParamIds(self):
        return self.params.getSupportedParamIds()

    # This method is more "dummy" than most, since it only works with
    # 'integer' parameters.
    @classmethod
    def __getValue(cls, param, initialized={}):
        if param.isFixed():
            return param.getFixedValue()
        return generator.nextValue(param, initialized)

    def next(self, paramId):
        """
        Return a freshly generated value for the parameter ID. Any
        referenced parameters will be initialized as well, and nothing will
        be cached. However, each parameter is guaranteed to only be
        initialized once for each call to next.

        This method isn't used while generating a design. It exists mostly
        for API compatibility with InPUT4j.
        """
        return self.__initParam(paramId, {})[paramId]

    def nextDesign(self, designId=None):
        """
        Return a new design with freshly initialized parameters.
        """
        params = {}
        initOrder = self.params.getInitializationOrder()

        # Initialize all the top-level parameters. Their dependencies will
        # be resolved recursively by __initParam.
        top = sorted(initOrder.keys())[-1]
        top = initOrder[top]

        for paramId in top:
            params = self.__initParam(paramId, params)
        return Design(params, designId)

    def __initParam(self, paramId, init):
        """
        Return a dictionary mapping parameter ID to initialized value for
        the specified parameter and any parameters it depends on. The init
        argument is a dictionary containing a subset of the result.
        """
        if paramId in init:
            return init
        param = self.params.getParam(paramId)
        if param.isDependent():
            for d in param.getDependees():
                init = self.__initParam(d, init)
        init[paramId] = self.__getValue(param, init)
        return init

    def setFixed(self, paramId, value):
        """
        Set the parameter to a fixed value. The value may be any expression
        that does not reference other parameters.
        """
        self.params.setFixed(paramId, value)


class Design(Identifiable):
    def __init__(self, params, designId=None):
        Identifiable.__init__(self, designId)
        self.params = params

    def getValue(self, paramId):
        return self.params[paramId]

