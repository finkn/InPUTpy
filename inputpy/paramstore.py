"""
inputpy.paramstore

:copyright: (c) 2013 by Christoffer Fink.
:license: MIT. See LICENSE for details.
"""
import inputpy.generators as generator
import inputpy.util as util
from inputpy.param import choiceFactory

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
        return self.__params.get(paramId)

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
        self.initOrder = util.initOrder(self.__dep)
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
