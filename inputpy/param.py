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
    def __init__(self, pId, pType, fixed=None,
            inclMin=None, exclMin=None, inclMax=None, exclMax=None):

        # Check arguments.
        if pId is None:
            raise ValueError('The parameter id was None')
        if pType is None:
            raise ValueError('The parameter type was None')
        if inclMin is not None and exclMin is not None:
            raise ValueError('Defined both inclusive and exclusive limits')
        if inclMax is not None and exclMax is not None:
            raise ValueError('Defined both inclusive and exclusive limits')

        minLimit = inclMin or exclMin
        maxLimit = inclMax or exclMax
        minLimit = minLimit or -2**32
        maxLimit = maxLimit or 2**32-1
        # Are max/min exclusive?
        minIsExcl = exclMin is not None
        maxIsExcl = exclMax is not None

        # Initialize fields.
        Identifiable.__init__(self, pId)
        self.type = pType
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

        # Check valid ranges.
        # Depending on the type that is generated (different sizes of int
        # for compatibility with Java), even a single limit may be out of
        # range. For example, inclMax=70000 would be out of range for a
        # short, even though it doesn't collide with the min limit.
        minLimit = self.min
        maxLimit = self.max
        if not self.isDependent():
            valueRange = abs(minLimit - maxLimit) + 1
            if minIsExcl:
                valueRange -= 1
            if maxIsExcl:
                valueRange -= 1
            if valueRange <= 0:
                raise ValueError('Empty value range')

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
        self.params = {}            # ID-to-Param mapping.
        self.dep = {}               # ID-to-IDs mapping.
        self.initOrder = None
        if params is not None:
            self.addParam(params)

    # Assumes that params is a sequence of parameters. If it turns out to be
    # a single parameter it is placed in a sequence before processing.
    def addParam(self, params):
        """
        Add one or more parameters to this ParamStore. The params argument
        can be a sequence of parameters or just a single parameter.
        """
        if isinstance(params, Param):
            params = (params,)
        for p in params:
            paramId = p.getId()
            self.params[paramId] = p
            self.dep[paramId] = p.getDependees()

    def getParam(self, paramId):
        return self.params[paramId]

    def setFixed(self, paramId, value):
        self.params[paramId].setFixed(value)

    def finalize(self):
        self.initOrder = initOrder(self.dep)


class DesignSpace(Identifiable):
    def __init__(self, paramStore, dId=None):
        Identifiable.__init__(self, dId)
        self.params = paramStore

    def getSupportedParamIds(self):
        return self.params.params.keys()

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

    def nextDesign(self, dId=None):
        """
        Return a new design with freshly initialized parameters.
        """
        params = {}
        if self.params.initOrder is None:
            self.params.finalize()
        top = sorted(self.params.initOrder.keys())[-1]
        top = self.params.initOrder[top]

        for paramId in top:
            params = self.__initParam(paramId, params)
        return Design(params, dId)

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

    def setFixed(self, pId, value):
        self.params.setFixed(pId, value)


class Design(Identifiable):
    def __init__(self, params, dId=None):
        Identifiable.__init__(self, dId)
        self.params = params

    def getValue(self, pId):
        return self.params[pId]

