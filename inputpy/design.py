"""
inputpy.design

:copyright: (c) 2013 by Christoffer Fink.
:license: MIT. See LICENSE for details.
"""
import inputpy.util as util
from inputpy.exceptions import InPUTException
from inputpy.util import Identifiable

class Design(Identifiable):
    def __init__(self, params, designSpace=None, designId=None, readOnly=False):
        Identifiable.__init__(self, designId)
        self.params = params
        self.__readOnly = readOnly
        self.__ext = [self]
        self.space = designSpace
        self.__updateSupportedIds()

    def getValue(self, paramId):
        result = None
        for d in self.__ext:
            result = util.getValue(paramId, d.params)
            if result is not None:
                return result

    def setValue(self, paramId, value):
        if self.__readOnly:
            raise InPUTException('Cannot set value on a read-only Design')

        if self.__checkValidity(paramId, value):
            util.setValue(paramId, self.params, value)
        self.__updateSupportedIds()

    def __checkValidity(self, paramId, value):
        # Hack: this should never happen. Fix old tests.
        if self.space is None:
            return True
        # Array elements are not part of the supported keys.
        if paramId not in self.params:
            paramId = util.root(paramId)
        param = self.space.params.getParam(paramId)
        return param.isValid(value)

    def __updateSupportedIds(self):
        self.supportedIds = set()
        for (paramId, value) in self.params.items():
            for id in util.getAllIds(paramId, value):
                self.supportedIds.add(id)

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
        #return self.params.keys()
        return self.supportedIds

    # -------------------------------------------------------------------------
    # These are dummy implementations, taken from the first version of Design.
    # -------------------------------------------------------------------------
    def export(self, exporter):
        pass

    # Unsure of what exactly same does.
    def same(self, design):
        pass
    # -------------------------------------------------------------------------
