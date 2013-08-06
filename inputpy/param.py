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
    def __init__(self, pId, pType,
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
        self.min = minLimit
        self.max = maxLimit
        self.exclMin = minIsExcl
        self.exclMax = maxIsExcl


        # min and max have been set to some value. If this parameter is not
        # dependent on any other parameter, then we're done. However, if it
        # was initialized with some expression, then we don't know yet if it is
        # dependent on another parameter or not. Either it's a simple
        # expression, in which case it can just be evaluated, or it involves
        # some other parameter, which will make the evaluation fail.
        # This seems like a crude test. Perhaps the expression could be parsed
        # so that it can be handled in a more sophisticated way.

        # The evaluation should use an empty namespace so that parameter names
        # don't match by accident. However, we still need some functions to be
        # available for use in the expression.
        import math
        namespace = {'Math': math, '__builtins__': {}}

        # Now try to evaluate. A dependency on a parameter will cause a
        # NameError. An expression that doesn't involve any other parameters
        # should evaluate without errors.
        if type(self.min) is str:
            try:
                self.min = eval(self.min, namespace)
            except NameError:
                pass
        if type(self.max) is str:
            try:
                self.max = eval(self.max, namespace)
            except NameError:
                pass

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


    def isDependent(self):
        minType = type(self.min)
        maxType = type(self.max)
        minIsPrimitive = minType is float or minType is int
        maxIsPrimitive = maxType is float or maxType is int
        return not (minIsPrimitive and maxIsPrimitive)

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

class DesignSpace(Identifiable):
    def __init__(self, dId=None):
        Identifiable.__init__(self, dId)
        self.params = {}

    def getParams(self):
        return self.params.items()

    def addParam(self, param):
        self.params[param.getId()] = param

    def getParameter(self, pId):
        return self.params[pId]

    # This method is more "dummy" than most, since it only works with
    # 'integer' parameters.
    def getValue(param):
        import random
        minLimit = param.getMin()
        maxLimit = param.getMax()
        if param.isMinExclusive():
            minLimit += 1
        if param.isMaxExclusive():
            maxLimit -= 1
        return random.randint(minLimit, maxLimit)

    def nextDesign(self, dId=None):
        params = {}
        for key in self.params.keys():
            params[key] = DesignSpace.getValue(self.params[key])
        return Design(params, dId)

class Design(Identifiable):
    def __init__(self, params, dId=None):
        Identifiable.__init__(self, dId)
        self.params = params

    def getValue(self, pId):
        return self.params[pId]

