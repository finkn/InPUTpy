"""
inputpy.design

This module exports two core interfaces:
- Design
- DesignSpace

:copyright: (c) 2013 by Christoffer Fink.
:license: MIT. See LICENSE for details.
"""
from inputpy.exceptions import InPUTException
import random
# Only needed by DummyParameterStore.
from test import *

rng = random.Random()

__all__ = ('Design', 'DesignSpace')

class Design:
    """
    A Design represents one set of instantiated parameters for a Design Space.
    """

    def __init__(self, fileName=None, document=None, designId=None):
        # If these aren't set, then expect a file.
        if (document is None and designId is None) or fileName is not None:
            try:
                f = open(fileName)
                f.close()
            except (IOError, TypeError):
                raise InPUTException("Couldn't open file: %s" % (fileName))

        self.parameters = {}
        self.fileName = fileName
        self.isReadOnly = False
        self.id = designId
        self.store = DummyParameterStore()  # Uses hard-coded test data.

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
        return self.store.getValue(paramId)

    # Perhaps the read-only flag check also belongs in some parameter store.
    def setValue(self, paramId, value):
        if self.isReadOnly:
            msg = "Cannot set '%s'. The design is read only!" % (paramId)
            raise InPUTException(msg)
        self.store.setValue(paramId, value)

    def same(self, design):
        return True

    # This method should be inherited.
    def getId(self):
        return self.id

    def setReadOnly(self):
        self.isReadOnly = True


# SomeLargePrimitiveArray, used in DummyParameterStore for initialization.
CACHED_ARRAY = [
    [
        [
            [
                a for a in range(42)
            ] for b in range(42)
        ] for c in range(42)
    ] for d in range(42)
]

# All of these parameters are normally imported from an XML document.
# Until all the XML parsing and parameter handling has been implemented,
# initialize the design with the expected parameters to make sure all the
# tests do what they are supposed to.
class DummyParameterStore:
    def __init__(self):
        params = {}
        params[SOME_BOOLEAN] = False
        params[SOME_LONG] = 1700584710333745153
        params[SOME_SHORT] = -7448
        params[SOME_DECIMAL] = -7889858943241994240.07228988965664218113715833169408142566680908203125
        params[SOME_FLOAT] = 0.73908234
        params[SOME_DOUBLE] = 0.12345778699671628
        params[SOME_INTEGER] = -1966342580
        params[A_SMALLER_LONG] = -3991818661248199656
        params[A_BIGGER_LONG] = 6671154699664551937
        params[A_STRANGE_LONG] = 5908891008213154534

        fixedArray = []
        for i in range(42):
            fixedArray.append(42)
        params[SOME_FIXED_ARRAY] = tuple(fixedArray)

        params[SOME_STRING_CUSTOMIZED_BY_THE_USER] = "SomeStringCustomizedByTheUser"
        params[SOME_STRUCTURAL] = SomeSecondChoice()
        # Initialize SomeStructuralParent.
        someStructuralParent = YetAnotherFirstChoice(1618927800)
        someStructuralParent.setAnotherSharedPrimitiveSub(5938400921453047807)
        someStructuralParent.someSharedStructuralSub = "testString"
        params[SOME_STRUCTURAL_PARENT] = someStructuralParent
        # Initialize SomeComplexStructural.
        complexStructural = SomeComplexStructural()
        complexStructural.addEntry(SingleComplexChoice())
        complexStructural.addEntry(SingleComplexChoice())
        complexStructural.addEntry(SingleComplexChoice())
        params[SOME_COMPLEX_STRUCTURAL] = complexStructural
        # Initialize SomeLargePrimitiveArray.
        # Note: This one is more of a cheat than the others since indexes
        # aren't handled properly at all.
        someLargePrimitiveArray = CACHED_ARRAY
        params[SOME_LARGE_PRIMITIVE_ARRAY] = someLargePrimitiveArray
        params[SOME_LARGE_PRIMITIVE_ARRAY] = someLargePrimitiveArray
        arrayId = SOME_LARGE_PRIMITIVE_ARRAY + ".1.1.1.1"
        params[arrayId] = someLargePrimitiveArray[0][0][0]
        arrayId = SOME_LARGE_PRIMITIVE_ARRAY + ".1.1.42"
        params[arrayId] = someLargePrimitiveArray[0][0][41]
        # Initialize WrappedPrimitive.
        expected = 0.9369297592420026
        wrapper = Wrapper(expected)
        customizableInputDemonstrator = SomeCommonStructural()
        customizableInputDemonstrator.setPrimitive(wrapper)
        wrapperId = CUSTOMIZABLE_INPUT_DEMONSTRATOR + "." + WRAPPED_PRIMITIVE
        params[wrapperId] = wrapper
        params[CUSTOMIZABLE_INPUT_DEMONSTRATOR] = customizableInputDemonstrator
        # Initialize SomeFixedArray.
        # Cheating with the indexes again.
        someFixedArray = tuple([42 for i in range(42)])
        params[SOME_FIXED_ARRAY] = someFixedArray
        params[SOME_FIXED_ARRAY + ".1"] = someFixedArray[0]
        params[SOME_FIXED_ARRAY + ".42"] = someFixedArray[41]

        self.parameters = params

    def setValue(self, paramId, value):
        params = self.parameters
        if value is None:
            raise InPUTException("Can't set parameter. Invalid value: None.")
        if not paramId in params:
            raise InPUTException("Can't set parameter. Invalid ID: " + paramId)
        else:
            params[paramId] = value

    def getValue(self, paramId):
        try:
            return self.parameters[paramId]
        except KeyError:
            return None

class DesignSpace:
    """
    A DesignSpace contains the set of parameters and their restrictions. It
    can generate a Design by setting values for each parameter.
    """

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

    def next(self, paramId,
            dimensions=None, subParams=None, actualParams=None):
        try:
            value = self.parameters[paramId]
        except KeyError:
            return 3    # Dummy value.

        if value is None:
            return rng.randint(0, 1000000)
        else:
            return value

    def nextDesign(self, designId, readOnly=False):
        design = Design(designId=designId)
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
        design = Design(designId=designId)
        design.id = designId
        return design
