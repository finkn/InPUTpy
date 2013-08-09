from inputpy.util import Evaluator
from inputpy.util import initOrder

class Identifiable:
    """
    This class is a mixin. It provides all subclasses with a getId() method.
    An instance can be initialized using an id argument. If none is provided,
    then a unique id will be constructed automatically.
    """
    def __init__(self, objId=None):
        self.__id = objId or str(id(self))

    def getId(self):
        return self.__id

class Param(Identifiable):
    # Make the ID argument optional. If none is provided, use the id function
    # to generate an id.
    def __init__(self, paramId, paramType, fixed=None,
            inclMin=None, exclMin=None, inclMax=None, exclMax=None):

        # Check arguments.
        if paramId is None:
            raise ValueError('The parameter id was None')
        if paramType is None:
            raise ValueError('The parameter type was None')
        if inclMin is not None and exclMin is not None:
            raise ValueError('Defined both inclusive and exclusive limits')
        if inclMax is not None and exclMax is not None:
            raise ValueError('Defined both inclusive and exclusive limits')

        minLimit = inclMin or exclMin
        maxLimit = inclMax or exclMax
        # Are max/min exclusive?
        minIsExcl = exclMin is not None
        maxIsExcl = exclMax is not None

        # Initialize fields.
        Identifiable.__init__(self, paramId)
        self.type = paramType
        self.min = minLimit         # Set to preliminary min limit.
        self.max = maxLimit         # Set to preliminary max limit.
        self.exclMin = minIsExcl
        self.exclMax = maxIsExcl
        self.minDependees = ()      # Referenced parameters in min expression.
        self.maxDependees = ()      # Referenced parameters in max expression.
        self.fixed = fixed          # Fixed value, if any.


        # If min/max are expressions, these will be parsed to find
        # dependencies. If the expression does not contain references to any
        # other parameters, then the expression is evaluated immediately.

        # The evaluation should use an empty namespace so that parameter names
        # don't match by accident. However, we still need some functions to be
        # available for use in the expression.

        # NameErrors are not expected and indicate a real error.
        if type(self.min) is str:
            self.minDependees = tuple(Evaluator.parseDependencies(self.min))
            if len(self.minDependees) == 0:
                self.min = Evaluator.evaluate(self.min)
        if type(self.max) is str:
            self.maxDependees = tuple(Evaluator.parseDependencies(self.max))
            if len(self.maxDependees) == 0:
                self.max = Evaluator.evaluate(self.max)
        self.setFixed(fixed)

    def isFixed(self):
        return self.fixed is not None

    def setFixed(self, value):
        """
        Sets this parameter to a fixed value. A parameter can also be un-fixed
        by passing None as the value.
        Not that setting the fixed value bypasses range checks, meaning that
        whatever min/max limits have been set are ignored.

        Currently, expressions are allowed as long as they do not reference
        other parameters. (InPUT4j supports neither)
        """

        if type(value) is str:
            self.fixed = Evaluator.evaluate(value)
        else:
            self.fixed = value

    def getFixedValue(self):
        return self.fixed

    def isDependent(self):
        return self.isMinDependent() or self.isMaxDependent()

    def isMinDependent(self):
        return len(self.minDependees) > 0

    def isMaxDependent(self):
        return len(self.maxDependees) > 0

    def getType(self):
        return self.type

    def getMin(self):
        return self.min

    def getMax(self):
        return self.max

    def isMinInclusive(self):
        return not self.exclMin

    def isMinExclusive(self):
        return self.exclMin

    def isMaxInclusive(self):
        return not self.exclMax

    def isMaxExclusive(self):
        return self.exclMax

    def getDependees(self):
        return tuple(self.getMinDependees() + self.getMaxDependees())

    def getMinDependees(self):
        return self.minDependees

    def getMaxDependees(self):
        return self.maxDependees

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
        """
        if self.__finalized:
            return
        self.__validateParameters()
        self.initOrder = initOrder(self.__dep)
        self.__finalized = True

    def getInitializationOrder(self):
        """
        Return a dictionary that maps the initialization order to the matching
        parameter IDs.

        Example:
        A return value of {0: ['A', 'B'], 1: ['C']} means that A and B must
        be initialized before C (because C depends on one or more of (A,B)).

        The method requires that this parameter store is finalized. Calling
        this method will force finalization if this hasn't already been done.
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
        - TODO: No circular dependencies.
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

    # TODO: This test is only preliminary. It should be more sophisticated.
    # Possibly outsource this to the generator.
    def __validRange(self, param):
        if param.isDependent():
            return True     # Well, we don't really know, but it's not invalid.

        minLimit = param.getMin() or -2**32     # eek
        maxLimit = param.getMax() or 2**32-1    # eek
        valueRange = maxLimit - minLimit + 1

        if param.isMinExclusive():
            valueRange -= 1
        if param.isMaxExclusive():
            valueRange -= 1
        return valueRange > 0

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
        import random
        minLimit = param.getMin()
        if param.isMinDependent():
            minLimit = Evaluator.evaluate(minLimit, initialized)
        maxLimit = param.getMax()
        if param.isMaxDependent():
            maxLimit = Evaluator.evaluate(maxLimit, initialized)

        if param.isMinExclusive():
            minLimit += 1
        if param.isMaxExclusive():
            maxLimit -= 1
        return random.randint(minLimit, maxLimit)

    def next(self, paramId):
        """
        Return a freshly generated value for the parameter ID. Any referenced
        parameters will be initialized as well, and nothing will be cached.
        However, each parameter is guaranteed to only be initialized once for
        each call to next.

        This method isn't used while generating a design. It exists mostly for
        API compatibility with InPUT4j.
        """
        init = self.__initParam(paramId, {})
        return init[paramId]

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

