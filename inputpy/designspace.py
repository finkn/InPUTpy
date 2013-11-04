"""
inputpy.designspace

:copyright: (c) 2013 by Christoffer Fink.
:license: MIT. See LICENSE for details.
"""
import inputpy.generators as generator
import inputpy.util as util
import inputpy.mapping as mapping
import inputpy.param as param
from inputpy.design import Design
from inputpy.param import Identifiable
from inputpy.paramstore import ParamStore
from inputpy.util import Identifiable
from inputpy.q import *

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

    # fileName is currently ignored.
    def __init__(self, paramStore=None, spaceId=None, fileName=None):
        """
        An instance is always created using a ParamStore. A file name (if
        specified) only indicates which file the DesignSpace is based on.
        It will not be processed in any way.

        To import a DesignSpace from a file, use the getDesignSpace
        function.
        """
        Identifiable.__init__(self, spaceId)
        self.fileName = fileName
        self.params = paramStore or ParamStore()
        self.params.finalize()

    def getSupportedParamIds(self):
        return self.params.getSupportedParamIds()

    # All three keyword arguments are currently ignored.
    def next(self, paramId, dimensions=None, subParams=None, actualParams=None):
        """
        Return a freshly generated value for the parameter ID. Any
        referenced parameters will be initialized as well, and nothing will
        be cached. However, each parameter is guaranteed to only be
        initialized once for each call to next.

        This method isn't used while generating a design. It exists mostly
        for API compatibility with InPUT4j.
        """
        param = self.params.getParam(paramId)
        if param is None:
            return None
        if param.getTag() == SCHOICE:
            parentId = param.getParentId()
            relativeId = param.getRelativeId()
            parent = self.params.getParam(parentId)
            param = parent.getChoice(relativeId)
        return self.__initParam(param, {})[paramId]

    # readOnly is currently ignored.
    def nextDesign(self, designId=None, readOnly=False):
        """
        Return a new design with freshly initialized parameters.
        """
        params = {}
        for p in self.params.getTopLevelParameters():
            params = self.__initParam(p, params)
        return Design(params, self, designId)

    def __initParam(self, param, init):
        """
        Return a dictionary mapping parameter ID to initialized value for
        the specified parameter and any parameters it depends on. The init
        argument is a dictionary containing a subset of the result.
        """
        paramId = param.getId()
        if paramId in init:
            return init
        param = generator.getChoice(param)

        # When initializing dependent parameters, find the absolute ID of the
        # dependencies. Then use the appropriate values for those IDs when
        # resolving dependencies. (map the relative ID to the proper value)
        dependencies = {}
        ids = self.params.getSupportedParamIds()
        for d in param.getDependees():
            absolute = util.findAbsoluteParameter(paramId, d, ids)
            init = self.__initParam(self.params.getParam(absolute), init)
            dependencies[d] = init[absolute]

        init[paramId] = generator.nextValue(param, dependencies)
        return init

    def setFixed(self, paramId, value):
        """
        Set the parameter to a fixed value. The value may be any expression
        that does not reference other parameters.
        """
        self.params.setFixed(paramId, value)

    def isFile(self):
        return self.fileName is not None

    def getFileName(self):
        return self.fileName

    def nextEmptyDesign(self, designId=None):
        paramIds = self.params.getSupportedParamIds()
        return Design({p: None for p in paramIds}, self, designId)

    # -------------------------------------------------------------------------
    # This is a dummy implementation, taken from the first version of
    # DesignSpace.
    # -------------------------------------------------------------------------
    def impOrt(self, importer):
        return Design({})
    # -------------------------------------------------------------------------

    def __eq__(self, other):
        if not isinstance(other, DesignSpace):
            return False
        if self.getId() != other.getId():
            return False
        if self.getFileName() != other.getFileName():
            return False
        paramKeys1 = self.getSupportedParamIds()
        paramKeys2 = other.getSupportedParamIds()
        if paramKeys1 != paramKeys2:
            return False
        for key in paramKeys1:
            if self.params.getParam(key) != other.params.getParam(key):
                return False
        return True
