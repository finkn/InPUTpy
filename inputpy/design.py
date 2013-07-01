from inputpy.exceptions import InPUTException
import random

rng = random.Random()

class Design:
    """\
    A Design represents the parameters for a Design Space.
    """

    def __init__(self, fileName=None):
        self.parameters = {}
        self.fileName = fileName
        self.isReadOnly = False
        self.id = None

    def impOrt(self, importer):
        pass

    def export(self, exporter):
        pass

    def getSpace(self):
        return DesignSpace()

    def extendSpace(self, designSpace):
        pass

    # Automatically raises KeyError if paramId is invalid. It should raise an
    # InPUTException instead, but this is probably not the place for it, since
    # some sort of parameter store will be used in the background.
    def getValue(self, paramId, actualParam=None):
        #raise InPUTException('invalid parameter')
        return self.parameters[paramId]

    # Perhaps the read-only flag and check also belongs in some parameter store.
    def setValue(self, paramId, value):
        if self.isReadOnly:
            msg = "Cannot set '%s'. The design is read only!" % (paramId)
            raise InPUTException(msg)
        self.parameters[paramId] = value

    def same(self, design):
        return True

    # This method should be inherited.
    def getId(self):
        return self.id

    def setReadOnly(self):
        self.isReadOnly = True

class DesignSpace:
    def __init__(self, fileName=None):
        self.parameters = {}
        self.fileName = fileName

    def impOrt(self, importer):
        return Design(None)

    def isFile(self):
        return True

    # This method should be inherited.
    def getId(self):
        return None

    def next(self, paramId, dimensions=None):
        try:
            value = self.parameters[paramId]
        except KeyError:
            return 3    # Dummy value.

        if value is None:
            return rng.randint(0, 1000000)
        else:
            return value

    def nextDesign(self, designId, readOnly=False):
        design = Design()
        design.setReadOnly()
        return design

    def setFixed(self, paramId, value):
        self.parameters[paramId] = value

    def getSupportedParamIds(self):
        return []

    def getId(self):
        return "testSpace"

    def getFileName(self):
        return self.fileName

    def nextEmptyDesign(self, designId):
        design = Design()
        design.id = designId
        return design
