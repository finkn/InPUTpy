from inputpy.design import Design
from inputpy.exceptions import InPUTException
from inputpy.impexp import XMLFileImporter, XMLFileExporter
from test import SomeComplexStructural, SingleComplexChoice, Wrapper
from test import SomeCommonStructural, SomeStructural
from test import SomeFirstChoice, SomeSecondChoice
from test import SomeSubChoice, AnotherSubChoice
from test import AnotherStructuralParent
import unittest

DESIGN_FILE = "testDesign.xml"
PRECISION = 6

# Parameter IDs used in tests. This little section works similar to Q.
anotherInteger = "AnotherInteger"
someBoolean = "SomeBoolean"
someShort = "SomeShort"
someLong = "SomeLong"
someDouble = "SomeDouble"
someFloat = "SomeFloat"
someDecimal = "SomeDecimal"

anotherStructuralParent = "AnotherStructuralParent"
anotherStringCustomizedByTheUser = "AnotherStringCustomizedByTheUser"
anotherSharedPrimitiveSub = "AnotherSharedPrimitiveSub"
customizableInputDemonstrator = "CustomizableInputDemonstrator"
someStringCustomizedByTheUser = "SomeStringCustomizedByTheUser"
someStructuralParent = "SomeStructuralParent"
someComplexStructural = "SomeComplexStructural"
someFixedArray = "SomeFixedArray"
someLargePrimitiveArray = "SomeLargePrimitiveArray"
someSharedStructuralSub = "SomeSharedStructuralSub"
someLargePrimitiveArray = "SomeLargePrimitiveArray"

# Also a few values.
anotherTestDesign = "anotherTestDesign.xml"
someOtherTestDesign = "someOtherTestDesign.xml"

class TestDesign(unittest.TestCase):

    def setUp(self):
        self.design = Design(DESIGN_FILE)

    def testSetReadOnly(self):
        design = self.design    # Alias to save typing.
        paramId = "SomeBoolean"
        design.setReadOnly()
        with self.assertRaises(InPUTException):
            design.setValue(paramId, False)

    @unittest.skip("Not implemented yet.")
    def testGetSpace(self):
        space = self.design.getSpace()
        self.assertTrue(space.isFile())
        expected = "testSpace"
        value = space.getId()
        self.assertEquals(expected, value)

    @unittest.skip("Not implemented yet.")
    def testExtendScope(self):
        design = self.design    # Alias to save typing.
        anotherDesignFile = "anotherTestDesign.xml"
        paramId = "AnotherInteger"
        expected = 42

        # The 'AnotherInteger' parameter should not be present in the design.
        self.assertIsNone(design.getValue(paramId))
        # Now extend the current design with the new one.
        anotherDesign = Design(anotherDesignFile)
        design.extendScope(anotherDesign)
        # Now the parameter should be available.
        value = design.getValue(paramId)
        self.assertEquals(expected, value)
        # Check that the other design contains the same parameter.
        # For good measure.
        value = anotherDesign.getValue(paramId)
        self.assertEquals(expected, value)

    @unittest.skip("Not implemented yet.")
    def testGetId(self):
        self.assertEquals("testDesign", self.design.getId())

    @unittest.skip("Not implemented yet.")
    def testGetPrimitive(self):
        args = {
            "SomeBoolean": False,
            "SomeInteger": -1966342580,
            "SomeShort": -7448,
            "SomeLong": 1700584710333745153,
            "SomeDouble": 0.12345778699671628,
            "SomeFloat": 0.73908234,
            "SomeDecimal": -7889858943241994240.07228988965664218113715833169408142566680908203125,
        }
        for (key, value) in args.items():
            self.getAndCompare(key, value)

    def getAndCompare(self, paramId, expected):
        value = self.design.getValue(paramId)
        self.assertEquals(expected, value)

    @unittest.skip("Not implemented yet.")
    def testSetPrimitive(self):
        args = {
            "SomeBoolean": True,
            "SomeInteger": 1,
            "SomeShort": 42,
            "SomeLong": 1,
            "SomeDouble": 0.42,
            "SomeFloat": 0.84,
            "SomeDecimal": 42,
        }
        for (key, value) in args.items():
            self.setAndCompare(key, value)

    # The test requires the original value (if any) to be different from the
    # one that is set. That makes it easier to tell whether the parameter was
    # really set or if the expected value already existed.
    def setAndCompare(self, paramId, value):
        design = self.design    # Alias to save typing.
        before = design.getValue(paramId)
        self.assertNotEquals(value, before)
        design.setValue(paramId, value)
        after = design.getValue(paramId)
        self.assertEquals(value, after)

    @unittest.skip("Not implemented yet.")
    def testSettingPrimitivesOfWrongTypeShouldFail(self):
        args = {
            "SomeBoolean": True,
            "SomeInteger": 1,
            "SomeShort": 42,
            "SomeLong": 1,
            "SomeDouble": 0.42,
            "SomeFloat": 0.84,
            "SomeDecimal": 42,
        }
        for (key, value) in args.items():
            self.setValueShouldFail(key, value)

    def setValueShouldFail(self, paramId, value):
        with self.assertRaises(InPUTException):
            self.design.setValue(paramId, value)

    @unittest.skip("Not implemented yet.")
    def testGetEnum(self):
        self.fail("Need to figure out how to handle enums.")

    @unittest.skip("Not implemented yet.")
    def testSetEnum(self):
        self.fail("Need to figure out how to handle enums.")

    @unittest.skip("Not implemented yet.")
    def testGetStringParameter(self):
        firstParamId = "SomeStringCustomizedByTheUser"
        secondParamId = "AnotherStringCustomizedByTheUser"
        secondValue = "anotherFile.xml"
        self.setAndCompare(firstParamId, firstParamId)
        self.setAndCompare(secondValue, secondParamId)

    @unittest.skip("Not implemented yet.")
    def testGetInjectedPrimitive(self):
        design = self.design    # Alias to save typing.
        paramId = "SomeStructuralParent"
        childId = paramId + ".AnotherSharedPrimitiveSub"
        expected = 5938400921453047807
        parent = design.getValue(paramId)
        # Get child value by implicitly using the custom getter.
        child = design.getValue(childId)
        self.assertEquals(expected, child)
        # Get child value by explicitly using the custom getter on the parent.
        childValue = parent.getAnotherSharedPrimitiveSub()
        self.assertEquals(childValue, child)

    @unittest.skip("Not implemented yet.")
    def testSetRelativePrimitives(self):
        design = self.design    # Alias to save typing.
        someLongId = "SomeLong"
        biggerLongId = "ABiggerLong"

        someLong = design.getValue(someLongId)
        # someLong is just outside of (1 below) the range of allowed values
        # for the 'ABiggerLong' parameter.
        with self.assertRaises(InPUTException):
            design.setValue(biggerLongId, someLong)
        # Adding 1 should make the value valid.
        design.setValues(biggerLongId, someLong + 1)

    @unittest.skip("I don't know what this test is supposed to do.")
    def testGetInjectedStructural(self):
        design = self.design    # Alias to save typing.
        paramId = "AnotherStructuralParent"
        childId = paramId + ".SomeStructuralSub"
        parent = design.getValue(paramId)
        # Get child value by implicitly using the custom getter.
        child = design.getValue(childId)
        # Get child value by explicitly using the custom getter on the parent.
        childValue = parent.getSomeSharedStructuralSub()
        self.assertEquals(child, childValue)

    # The Java version has a case that is expected to fail because it tries to
    # set a parameter that was initialized by the constructor. That case is
    # handled separately in the next test below.
    @unittest.skip("Not implemented yet.")
    def testSetInjectedStructural(self):
        design = self.design    # Alias to save typing.
        parentId = "SomeStructuralParent"
        paramId = parentId + ".SomeSharedStructuralSub"
        value = "anotherString"
        # Because SomeSharedStructuralSub is initialized by injection, rather
        # than the constructor, setting the value should work.
        design.setValue(paramId, value)
        current = design.getValue(paramId)
        self.assertEquals(value, current)

        # Fetch the child value explicitly from the parent.
        parent = design.getValue(parentId)
        current = parent.getSomeSharedStructuralSub()
        self.assertEquals(value, current)

    # Handles the case of trying to set a constructor initialized parameter,
    # which is present in testSetInjectedStructural in the Java version.
    # The test also checks to make sure that trying to set the parameter
    # really didn't have any effect.
    @unittest.skip("Not implemented yet.")
    def testSettingConstructorInitializedParamWithInjectionShouldFail(self):
        design = self.design    # Alias to save typing.
        paramId = "AnotherStructuralParent.SomeSharedStructuralSub"
        value = SomeSubChoice()
        # value was created locally, so it shouldn't be identical to the
        # current parameter value. Check before and after trying to set the
        # parameter to be sure.
        before = design.getValue(paramId)
        self.assertIsNot(value, before)
        # Try to set the parameter. This should fail.
        with self.assertRaises(InPUTException):
            design.setValue(paramId, value)
        # Check again.
        after = design.getValue(paramId)
        self.assertIsNot(value, after)
        # This is a stronger claim. Not only wasn't the parameter set to the
        # locally created value, but the parameter still has the same value.
        self.assertIs(before, after)

    # This test should use a mock object to check that the expected method
    # calls are made.
    @unittest.skip("Not implemented yet.")
    def testGetCustomizableGetter(self):
        design = self.design    # Alias to save typing.
        parentId = "CustomizableInputDemonstrator"
        mutatorId = parentId + ".CustomizableSetGetPrimitive"
        value = 2.860933188245651E-4
        # Get the value by using the custom getter and by getting the parent
        # and then invoking the getter manually.
        implicit = design.getValue(mutatorId)
        parent = design.getValue(parentId)
        explicit = parent.andTheCustomizableGetter()
        # Then compare. Both should return the same value.
        self.assertAlmostEquals(value, implicit, PRECISION)
        self.assertAlmostEquals(value, explicit, PRECISION)

    # The CustomizableInputDemonstrator parameter is defined in the code
    # mapping configuration to use a custom setter and getter method. 
    # This test should use a mock object to check that the expected method
    # calls are made.
    @unittest.skip("Not implemented yet.")
    def testSetCustomizableGetter(self):
        design = self.design    # Alias to save typing.
        parentId = "CustomizableInputDemonstrator"
        mutatorId = parentId + ".CustomizableSetGetPrimitive"
        value = 0.5
        # Set the value that is wrapped by the parent by invoking the mutator.
        design.setValue(mutatorId, value)
        # Get parent and check the value by manually invoking the custom getter.
        parent = design.getValue(parentId)
        self.assertEquals(value, parent.andTheCustomizableGetter())

    @unittest.skip("Not implemented yet.")
    def testGetStructural(self):
        paramId = "SomeStructural"
        value = self.design.getValue(paramId)
        self.assertTrue(isinstance(value, SomeStructural))

    # This test is missing a case that is present in the Java version.
    # That case is handled separately in the following test.
    @unittest.skip("Not implemented yet.")
    def testSetStructural(self):
        paramId = "SomeStructural"
        # Set the parameter to one SomeStructural and check that it was set.
        choice = SomeFirstChoice()          # This is a SomeStructural.
        self.setStructural(paramId, choice)
        # Now set the parameter to another SomeStructural and check it again.
        choice = SomeSecondChoice()         # This is also a SomeStructural.
        self.setStructural(paramId, choice)

    def setStructural(self, paramId, expected):
        self.design.setValue(paramId, expected)
        value = self.design.getValue(paramId)
        self.assertEquals(expected, value)

    # This test handles the negative case that was part of the
    # testSetStructural test in the Java version.
    @unittest.skip("Not implemented yet.")
    def testSetStructuralWithWrongTypeShouldFail(self):
        paramId = "SomeStructural"
        choice = AnotherSubChoice()     # This is not a SomeStructural!
        with self.assertRaises(InPUTException):
            self.design.setValue(paramId, choice)

    @unittest.skip("Not implemented yet.")
    def testGetWrapper(self):
        design = self.design    # Alias to save typing.
        parentId = "CustomizableInputDemonstrator"
        wrapperId = parentId + ".WrappedPrimitive"
        expected = 0.9369297592420026
        value = design.getValue(wrapperId)
        self.assertAlmostEquals(expected, value.toValue(), PRECISION)
        parent = design.getValue(parentId)
        self.assertEquals(value, parent.getPrimitive())

    @unittest.skip("Not implemented yet.")
    def testSetWrapper(self):
        design = self.design    # Alias to save typing.
        parentId = "CustomizableInputDemonstrator"
        wrapperId = parentId + ".WrappedPrimitive"
        # Create a Wrapper object and set the parameter.
        value = Wrapper(.3)
        design.setValue(wrapperId, value)
        # Get the parameter back and compare it to the original value.
        current = design.getValue(wrapperId)
        self.assertEquals(value, current)

        # Check that the parent structural has the updated Wrapper as a child.
        parent = design.getValue(parentId)
        self.assertEquals(value, parent.getPrimitive())

    @unittest.skip("Not implemented yet.")
    def testGetArray(self):
        design = self.design    # Alias to save typing.
        paramId = "SomeFixedArray"
        elemValue = 42              # All elements are set to the value 42.
        length = 42                 # Total length of array, also last index.
        firstId = paramId + ".1"                        # First element.
        lastId = paramId + "." + str(length)            # Last element
        outsideId = paramId + "." + str(length + 1)     # Out of range.
        largeId = "SomeLargePrimitiveArray"

        # Get array and make sure it has the expected length.
        array = design.getValue(paramId)
        self.assertEquals(length, len(array))
        # Go through the array and check the values.
        for val in array:
            self.assertEquals(elemValue, val)
        # Fetching the first element explicitly should yield the same value.
        value = design.getValue(firstId)
        self.assertEquals(elemValue, value)
        # Fetching the last element explicitly should yield the same value.
        value = design.getValue(lastId)
        self.assertEquals(elemValue, value)
        # Fetching an element outside the range should yield a None.
        value = design.getValue(outsideId)
        self.assertIsNone(elemValue, value)

        largeArray = design.getValue(largeId)
        self.assertEquals(length, len(largeArray))
        self.assertEquals(length, len(largeArray[0][0]))

    def testSetArray(self):
        design = self.design    # Alias to save typing.
        elemId = "SomeLargePrimitiveArray.1.1.1.1"
        arrayId = "SomeLargePrimitiveArray.1.1.42"
        value = 13
        design.setValue(elemId, value)
        current = design.getValue(elemId)
        self.assertEquals(value, current)

        values = (1,2,3)
        design.setValue(arrayId, values)
        currentValues = design.getValue(arrayId)
        self.assertEquals(values, currentValues)

        # TODO:
        # Add a test that changes 1.1.42.2 and makes sure that the 42 array is
        # updated appropriately. (The dummy implementation passes the test.)
        # In other words, check that
        # setValue("X.1.1", [1,0,3]); setValue("X.1.1.2", 2)
        # has the same effect as
        # setValue("X.1.1", [1,2,3])

    # The Java version has a testSetArrayNegative with two cases.
    # These two tests replace that one.
    # Maybe the test using an out of range index should use a non-fixed array,
    # since such a parameter shouldn't be settable anyway?
    # The same fixed array is currently used for both.
    @unittest.skip("Not implemented yet.")
    def testSetValueForArrayElementWithOutOfRangeIndexShouldFail(self):
        paramId = "SomeFixedArray.43"   # 43 is out of range.
        with self.assertRaises(InPUTException):
            self.design.setValue(paramId, 42)   # The value is irrelevant.

    @unittest.skip("Not implemented yet.")
    def testSetValueForFixedArrayElementShouldFail(self):
        paramId = "SomeFixedArray.1"    # 1 is valid.
        with self.assertRaises(InPUTException):
            self.design.setValue(paramId, 42)   # The value is irrelevant.

    @unittest.skip("Not implemented yet.")
    def testGetComplex(self):
        design = self.design    # Alias to save typing.
        paramId = "SomeComplexStructural"
        value = design.getValue(paramId)
        self.assertTrue(isinstance(value, SomeComplexStructural))
        self.assertEquals(3, value.size())

    def testSetComplex(self):
        design = self.design    # Alias to save typing.
        paramId = "SomeComplexStructural"
        # Construct expected complex object.
        complexStructural = SomeComplexStructural()
        complexStructural.addEntry(SingleComplexChoice())
        complexStructural.addEntry(SingleComplexChoice())
        complexStructural.addEntry(SingleComplexChoice())

        # Set the value and get it back again.
        design.setValue(paramId, complexStructural)
        current = design.getValue(paramId)
        # Compare the manually constructed and the returned objects.
        # Use assertIsInstance.
        self.assertTrue(isinstance(current, type(complexStructural)))
        self.assertEquals(complexStructural.size(), current.size())

    @unittest.skip("Not implemented yet.")
    def testGetValueWithInvalidIdShouldFail(self):
        # This test corresponds to testGetNegative from the Java version.
        self.getNegative("IDoNotExist")
        self.getNegative(None)

    def getNegative(self, invalidId):
        design = self.design    # Alias to save typing.
        with self.assertRaises(InPUTException):
            design.getValue(invalidId)
        with self.assertRaises(InPUTException):
            design.getValue(invalidId, None)
        with self.assertRaises(InPUTException):
            design.getValue(invalidId, ())     # Empty tuple.

    # The Java version has a testSetNegative test which itself contains two
    # cases where a setValue call fails for different reasons.
    # Those cases are instead represented here in these two separate tests.
    @unittest.skip("Not implemented yet.")
    def testSetValueWithInvalidIdShouldFail(self):
        invalidId = "IDoNotExist"
        with self.assertRaises(InPUTException):
            self.design.setValue(invalidId, "some value")

    @unittest.skip("Not implemented yet.")
    def testSetValueWithNullValueShouldFail(self):
        design = self.design    # Alias to save typing.
        validId = "SomeStructuralParent"
        # Check that the parameter isn't None to begin with.
        self.assertNotNull(design.getValue(validId))
        with self.assertRaises(InPUTException):
            design.setValue(validId, None)
        # Check that the parameter is still not None (it wasn't set).
        self.assertNotNull(design.getValue(validId))

    @unittest.skip("Not implemented yet.")
    def testSetFixed(self):
        with self.assertRaises(InPUTException):
            self.design.setValue("SomeFixed", 43)

    @unittest.skip("Not implemented yet.")
    def testExport(self):
        design = self.design    # Alias to save typing.
        designSpace = design.getSpace()
        # Export to file.
        designName = "someOtherTestDesign.xml"
        exporter = XMLFileExporter(designName)
        design.export(exporter)
        # Import the same design to create a new object.
        importer = XMLFileImporter(designName)
        impDesign = designSpace.impOrt(importer)
        self.assertTrue(design.same(impDesign))

    @unittest.skip("Not implemented yet.")
    def testDesign(self):
        flawedFileNames = (None, "someNotExistent.xml")
        with self.assertRaises(InPUTException):
            for fileName in flawedFileNames:
                self.design = Design(fileName)

if __name__ == '__main__':
    unittest.main()
