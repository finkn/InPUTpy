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
        self.customizableSetGetPrimitive = 0

    def setPrimitive(self, wrapper):
        self.wrapper = wrapper

    def getPrimitive(self):
        return self.wrapper

    def customizableSetter(self, value):
        self.customizableSetGetPrimitive = value

    def andTheCustomizableGetter(self):
        return self.customizableSetGetPrimitive


class SomeFirstChoice(SomeCommonStructural):
    pass


class SomeSecondChoice(SomeCommonStructural):
    pass


class SomeThirdChoice(SomeSecondChoice):
    pass


class SomeChoiceSpecificStructuralSub:
    pass


class AlsoSingleChoicesAreValid(SomeChoiceSpecificStructuralSub):
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


class AndYetAnotherFirstChoice(AnotherStructuralParent):
    def __init__(self, sub):
        AnotherStructuralParent.__init__(self, sub)


class AndYetAnotherSecondChoice(AnotherStructuralParent):
    def __init__(self, sub, bar):
        AnotherStructuralParent.__init__(self, sub)
        self.bar = bar


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
            return not result

    def toValue(self):
        return self.value

# Parameter IDs and some values used in tests.
# This little section works similar to Q.
A_BIGGER_LONG = "ABiggerLong"
AND_YET_ANOTHER_SECOND_CHOICE = "AndYetAnotherSecondChoice"
ANOTHER_FILE = "anotherFile.xml"
ANOTHER_INTEGER = "AnotherInteger"
ANOTHER_RESTRICTED_PRIMITIVE = "AnotherRestrictedPrimitive"
ANOTHER_SHARED_PRIMITIVE_SUB = "AnotherSharedPrimitiveSub"
ANOTHER_STRING_CUSTOMIZED_BY_THE_USER = "AnotherStringCustomizedByTheUser"
ANOTHER_STRUCTURAL = "AnotherStructural"
ANOTHER_STRUCTURAL_PARENT = "AnotherStructuralParent"
ANOTHER_TEST_DESIGN = "anotherTestDesign.xml"
A_SMALLER_LONG = "ASmallerLong"
A_STRANGE_LONG = "AStrangeLong"
CUSTOMIZABLE_INPUT_DEMONSTRATOR = "CustomizableInputDemonstrator"
CUSTOMIZABLE_SET_GET_PRIMITIVE = "CustomizableSetGetPrimitive"
SOME_BOOLEAN = "SomeBoolean"
SOME_COMPLEX_STRUCTURAL = "SomeComplexStructural"
SOME_DECIMAL = "SomeDecimal"
SOME_DOUBLE = "SomeDouble"
SOME_FIXED_ARRAY = "SomeFixedArray"
SOME_FIXED = "SomeFixed"
SOME_FLOAT = "SomeFloat"
SOME_INTEGER = "SomeInteger"
SOME_LARGE_PRIMITIVE_ARRAY = "SomeLargePrimitiveArray"
SOME_LONG = "SomeLong"
SOME_MULTI_DIMENSIONAL_ARRAY_OF_SPECIFIED_SIZE = "SomeMultidimensionalArrayOfSpecifiedSize"
SOME_MULTIDIMENSIONAL_ARRAY_OF_UNSPECIFIED_SIZE = "SomeMultidimensionalArrayOfUnspecifiedSize"
SOME_OTHER_TEST_DESIGN = "someOtherTestDesign.xml"
SOME_PRIMITIVE_ARRAY_OF_SPECIFIED_SIZE = "SomePrimitiveArrayOfSpecifiedSize"
SOME_PRIMITIVE_ARRAY_OF_UNSPECIFIED_SIZE = "SomePrimitiveArrayOfUnspecifiedSize"
SOME_RESTRICTED_PRIMITIVE = "SomeRestrictedPrimitive"
SOME_SHARED_PRIMITIVE_SUB = "SomeSharedPrimitiveSub"
SOME_SHARED_STRUCTURAL_SUB = "SomeSharedStructuralSub"
SOME_SHORT = "SomeShort"
SOME_STRING_ARRAY_CUSTOMIZED_BY_THE_USER = "SomeStringArrayCustomizedByTheUser"
SOME_STRING_CUSTOMIZED_BY_THE_USER = "SomeStringCustomizedByTheUser"
SOME_STRUCTURAL_PARENT = "SomeStructuralParent"
SOME_STRUCTURAL = "SomeStructural"
SOME_VERY_RESTRICTED_PRIMITIVE = "SomeVeryRestrictedPrimitive"
WRAPPED_PRIMITIVE = "WrappedPrimitive"
