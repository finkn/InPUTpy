"""
test

This package contains all the test code for the InPUTpy project.
The package exports various test classes used during testing for verifying
parameter configuration.

:copyright: (c) 2013 by Christoffer Fink.
:license: MIT. See LICENSE for details.
"""
class SomeStructural:
    pass


class SomeCommonStructural(SomeStructural):
    def __init__(self):
        self.wrapper = None

    def setPrimitive(self, wrapper):
        self.wrapper = wrapper

    def getPrimitive(self):
        return self.wrapper


class SomeFirstChoice(SomeCommonStructural):
    pass


class SomeSecondChoice(SomeCommonStructural):
    pass


class SomeStructuralParent:
    def __init__(self, someSharedPrimitiveSub):
        self.someSharedPrimitiveSub = someSharedPrimitiveSub
        # To copy the InPUT4j tests as closely as possible, initialize
        # this data the way Java would do.
        self.anotherSharedPrimitiveSub = 0  # long would be initialized to 0.
        self.someSharedStructuralSub = None # String would be null.

    def getSomeSharedPrimitiveSub(self):
        return self.someSharedPrimitiveSub

    def getAnotherSharedPrimitiveSub(self):
        return self.anotherSharedPrimitiveSub

    def getSomeSharedStructuralSub(self):
        return self.someSharedStructuralSub

    def setSomeSharedPrimitiveSub(self, someSharedPrimitiveSub):
        self.someSharedPrimitiveSub = someSharedPrimitiveSub

    def setAnotherSharedPrimitiveSub(self, anotherSharedPrimitiveSub):
        self.anotherSharedPrimitiveSub = anotherSharedPrimitiveSub

    def setSomeSharedStructuralSub(self, someSharedStructuralSub):
        self.someSharedStructuralSub = someSharedStructuralSub


class YetAnotherThirdChoice(SomeStructuralParent):
    def __init__(self, someSharedPrimitiveSub, someChoiceSpecificPrimitiveSub):
        SomeStructuralParent.__init__(self, someSharedPrimitiveSub)
        self.someChoiceSpecificPrimitiveSub = someChoiceSpecificPrimitiveSub

    def getSomeChoiceSpecificPrimitiveSub(self):
        return self.someChoiceSpecificPrimitiveSub


class YetAnotherFirstChoice(SomeStructuralParent):
    def __init__(self, someSharedPrimitiveSub):
        SomeStructuralParent.__init__(self, someSharedPrimitiveSub)


class YetAnotherSecondChoice(YetAnotherFirstChoice):
    def __init__(self):
        YetAnotherFirstChoice.__init__(self, 42)


class SomeSharedStructuralSub:
    pass


class SomeSubChoice(SomeSharedStructuralSub):
    pass


class AnotherSubChoice(SomeSharedStructuralSub):
    pass


class AnotherStructuralParent:
    def __init__(self, sub):
        self.sub = sub

    def getSomeSharedStructuralSub(self):
        return self.sub


class SomeAbstractComplexStructural:
    pass


class SomeComplexStructural(SomeAbstractComplexStructural):
    def __init__(self):
        self.items = []

    def addEntry(self, item):
        self.items.append(item)

    def getEntry(self, index):
        return self.items[index]

    def size(self):
        return len(self.items)


class SingleComplexChoice(SomeAbstractComplexStructural):
    def __init__(self, a=0.0):
        self.a = a

    def getA(self):
        return self.a


class SecondSingleComplexChoice(SingleComplexChoice):
    pass


class Wrapper:
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        if isinstance(other, Wrapper):
            return self.value == other.value
        else:
            return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        else:
            return result

    def toValue(self):
        return self.value

# Parameter IDs and some values used in tests.
# This little section works similar to Q.
aBiggerLong = "ABiggerLong"
andYetAnotherSecondChoice = "AndYetAnotherSecondChoice"
anotherFile = "anotherFile.xml"
anotherInteger = "AnotherInteger"
anotherRestrictedPrimitive = "AnotherRestrictedPrimitive"
anotherSharedPrimitiveSub = "AnotherSharedPrimitiveSub"
anotherStringCustomizedByTheUser = "AnotherStringCustomizedByTheUser"
anotherStructural = "AnotherStructural"
anotherStructuralParent = "AnotherStructuralParent"
anotherTestDesign = "anotherTestDesign.xml"
aSmallerLong = "ASmallerLong"
aStrangeLong = "AStrangeLong"
customizableInputDemonstrator = "CustomizableInputDemonstrator"
customizableSetGetPrimitive = "CustomizableSetGetPrimitive"
someBoolean = "SomeBoolean"
someComplexStructural = "SomeComplexStructural"
someDecimal = "SomeDecimal"
someDouble = "SomeDouble"
someFixedArray = "SomeFixedArray"
someFixed = "SomeFixed"
someFloat = "SomeFloat"
someInteger = "SomeInteger"
someLargePrimitiveArray = "SomeLargePrimitiveArray"
someLong = "SomeLong"
someMultiDimensionalArrayOfSpecifiedSize = "SomeMultidimensionalArrayOfSpecifiedSize"
someMultidimensionalArrayOfUnspecifiedSize = "SomeMultidimensionalArrayOfUnspecifiedSize"
someOtherTestDesign = "someOtherTestDesign.xml"
somePrimitiveArrayOfSpecifiedSize = "SomePrimitiveArrayOfSpecifiedSize"
somePrimitiveArrayOfUnspecifiedSize = "SomePrimitiveArrayOfUnspecifiedSize"
someRestrictedPrimitive = "SomeRestrictedPrimitive"
someSharedPrimitiveSub = "SomeSharedPrimitiveSub"
someSharedStructuralSub = "SomeSharedStructuralSub"
someShort = "SomeShort"
someStringArrayCustomizedByTheUser = "SomeStringArrayCustomizedByTheUser"
someStringCustomizedByTheUser = "SomeStringCustomizedByTheUser"
someStructuralParent = "SomeStructuralParent"
someStructural = "SomeStructural"
someVeryRestrictedPrimitive = "SomeVeryRestrictedPrimitive"
wrappedPrimitive = "WrappedPrimitive"
