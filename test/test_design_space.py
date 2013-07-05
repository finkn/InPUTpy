from inputpy.design import DesignSpace
from inputpy.exceptions import InPUTException
from test import *
from inputpy import q as Q
import unittest

DESIGN_SPACE_FILE = "testSpace.xml"
DESIGN_MAPPING_FILE = "testSpaceMapping.xml"

# Parameter IDs used in tests. This little section works similar to Q.
anotherInteger = "AnotherInteger"
aBiggerLong = "ABiggerLong"
aSmallerLong = "ASmallerLong"
aStrangeLong = "AStrangeLong"
someBoolean = "SomeBoolean"
someShort = "SomeShort"
someInteger = "SomeInteger"
someLong = "SomeLong"
someDouble = "SomeDouble"
someFloat = "SomeFloat"
someDecimal = "SomeDecimal"

anotherStructural = "AnotherStructural"
anotherStructuralParent = "AnotherStructuralParent"
anotherStringCustomizedByTheUser = "AnotherStringCustomizedByTheUser"
anotherSharedPrimitiveSub = "AnotherSharedPrimitiveSub"
anotherRestrictedPrimitive = "AnotherRestrictedPrimitive"
andYetAnotherSecondChoice = "AndYetAnotherSecondChoice"
customizableInputDemonstrator = "CustomizableInputDemonstrator"
customizableSetGetPrimitive = "CustomizableSetGetPrimitive"
someStructural = "SomeStructural"
someStringCustomizedByTheUser = "SomeStringCustomizedByTheUser"
someStructuralParent = "SomeStructuralParent"
someComplexStructural = "SomeComplexStructural"
someFixedArray = "SomeFixedArray"
someLargePrimitiveArray = "SomeLargePrimitiveArray"
someSharedPrimitiveSub = "SomeSharedPrimitiveSub"
someSharedStructuralSub = "SomeSharedStructuralSub"
someLargePrimitiveArray = "SomeLargePrimitiveArray"
someStringArrayCustomizedByTheUser = "SomeStringArrayCustomizedByTheUser"
somePrimitiveArrayOfUnspecifiedSize = "SomePrimitiveArrayOfUnspecifiedSize"
someRestrictedPrimitive = "SomeRestrictedPrimitive"
someVeryRestrictedPrimitive = "SomeVeryRestrictedPrimitive"
wrappedPrimitive = "WrappedPrimitive"
someFixed = "SomeFixed"

somePrimitiveArrayOfUnspecifiedSize = "SomePrimitiveArrayOfUnspecifiedSize"
somePrimitiveArrayOfSpecifiedSize = "SomePrimitiveArrayOfSpecifiedSize"
someMultidimensionalArrayOfUnspecifiedSize = "SomeMultidimensionalArrayOfUnspecifiedSize"
someMultiDimensionalArrayOfSpecifiedSize = "SomeMultidimensionalArrayOfSpecifiedSize"

# Also a few values.
anotherFile = "anotherFile.xml"
anotherTestDesign = "anotherTestDesign.xml"
someOtherTestDesign = "someOtherTestDesign.xml"

class TestDesignSpace(unittest.TestCase):

    def setUp(self):
        self.space = DesignSpace(DESIGN_SPACE_FILE)

    def tearDown(self):
        del self.space

    @unittest.skip("Not implemented yet.")
    def testDesignSpaceWithMappingAsInputStreams(self):
        self.fail("Not implemented yet.")

    @unittest.skip("Not implemented yet.")
    def testDesignSpaceFromFile(self):
        self.tearDown()
        self.space = DesignSpace(DESIGN_SPACE_FILE)

    @unittest.skip("Not implemented yet.")
    def testDesignSpaceFromInputStream(self):
        self.fail("Not implemented yet.")

    def testNextPrimitive(self):
        params = (
            someBoolean, someInteger, someShort, someLong,
            someDouble, someFloat, someDecimal,
        )
        for param in params:
            self.getNextAndCompare(param)

    @unittest.skip("Not implemented yet.")
    def testNextString(self):
        space = self.space      # Alias to save typing.
        paramId = someStringCustomizedByTheUser
        expected = paramId
        anotherParamId = anotherStringCustomizedByTheUser
        arrayParamId = someStringArrayCustomizedByTheUser 
        expectedAlternatives = (
            "someFile.xml", "someFile.txt", "anotherFile.xml"
        )
        # Test the first parameter.
        value = space.next(paramId)
        self.assertEquals(expected, value)
        # Test the next one. The value should be one of the alternatives.
        value = space.next(anotherParamId)
        self.assertTrue(value in expectedAlternatives)

        # Test an array of strings.
        values = space.next(arrayParamId)
        self.assertEquals("Expected an array of 10 arrays.", 10, len(values))
        self.assertEquals("Expected an array of 5 elements.", 5, len(values[0]))
        # Every element is expected to have the same value: same as the id.
        for array in values:
            for element in array:
                self.assertEquals(arrayParamId, element)

    def testNextStructural(self):
        space = self.space      # Alias to save typing.
        paramIds = (
            someStructural, anotherStructural,
            someStructuralParent, anotherStructuralParent,
        )
        for param in paramIds:
            self.getNextAndCompare(param)

    # The Java version has a single testNextArray test.
    # That test has been split into the individual cases below.
    @unittest.skip("This test has been superseded.")
    def testNextArray(self):
        self.fail("This test has been superseded.")

    # Replaces testNextArray.
    @unittest.skip("Not implemented yet.")
    def testNextPrimitiveArrayOfUnspecifiedSize(self):
        paramId = "SomePrimitiveArrayOfUnspecifiedSize"
        expectedLength = 1
        array = self.space.next(paramId)
        self.assertEquals(expectedLength, len(array))

    # Replaces testNextArray.
    @unittest.skip("Not implemented yet.")
    def testNextPrimitiveArrayOfSpecifiedSize(self):
        paramId = "SomePrimitiveArrayOfSpecifiedSize"
        expectedLength = 42
        array = self.space.next(paramId)
        self.assertEquals(expectedLength, len(array))
        self.assertEquals(expectedLength, len(array[0]))
        self.assertEquals(expectedLength, len(array[0][0]))

    # Replaces testNextArray.
    @unittest.skip("Not implemented yet.")
    def testNextStructuralMultidimensionalArrayOfUnspecifiedSize(self):
        paramId = "SomeMultidimensionalArrayOfUnspecifiedSize"
        expectedLength = 1
        array = self.space.next(paramId)
        self.assertEquals(expectedLength, len(array))

    # Replaces testNextArray.
    @unittest.skip("Not implemented yet.")
    def testNextPrimitiveMultidimensionalArrayOfSpecifiedSize(self):
        paramId = "SomeMultidimensionalArrayOfSpecifiedSize"
        expectedLengthD0 = 42
        expectedLengthD1 = 1
        expectedLengthD2 = 42
        expectedLengthD3 = 1
        array = self.space.next(paramId)
        self.assertEquals(expectedLengthD0, len(array))
        self.assertEquals(expectedLengthD1, len(array[0]))
        self.assertEquals(expectedLengthD2, len(array[0][0]))
        self.assertEquals(expectedLengthD3, len(array[0][0][0]))

    # The Java version has a single testNextNegative test.
    # That test has been split into the individual cases below.
    # However, the casting test has been skipped because Python is kewl.
    @unittest.skip("This test has been superseded.")
    def testNextNegative(self):
        self.fail("This test has been superseded.")

    # Replaces testNextNegative.
    @unittest.skip("Not implemented yet.")
    def testNextWithUnknownParameterShouldReturnNone(self):
        paramId = "ParamThatDoesNotExist"
        self.assertIsNone(self.space.next(paramId))

    # Replaces testNextNegative.
    @unittest.skip("Not implemented yet.")
    def testNextWithNoneParameterShouldReturnNone(self):
        self.assertIsNone(self.space.next(None))

    # The Java version has a single testNextSubParameter test.
    # That test has been split into the individual cases below.
    @unittest.skip("This test has been superseded.")
    def testNextSubParameter(self):
        self.fail("This test has been superseded.")

    # Replaces testNextSubParameter.
    def testNextPrimitiveSubParameter(self):
        paramId = someStructuralParent + "." + someSharedPrimitiveSub
        self.getNextAndCompare(self.space.next(paramId))

    # Replaces testNextSubParameter.
    def testNextStructuralSubParameter(self):
        paramId = anotherStructuralParent + "." + andYetAnotherSecondChoice
        self.getNextAndCompare(self.space.next(paramId))

    # Replaces testNextSubParameter.
    @unittest.skip("Not implemented yet.")
    def testNextChoiceParameter(self):
        paramId = anotherStructuralParent + "." + andYetAnotherSecondChoice
        self.getNextAndCompare(self.space.next(paramId))

    # Test test.
    @unittest.skip("Already verified, temporarily disabled.")
    def testCompareToRange(self):
        value = self.space.next("whatever")
        self.compareToRange(value, 2, 4)
        self.compareToRange(value, 2.9, 3.1)
        self.compareToRange(value, 3, 3)
        self.compareToRange(value, minLimit=3)
        self.compareToRange(value, maxLimit=3)

        with self.assertRaises(Exception):
            self.compareToRange(value, 4, 3)
        with self.assertRaises(Exception):
            self.compareToRange(value, 3.1, 3.0)
        with self.assertRaises(Exception):
            self.compareToRange(value, 3, 2)
        with self.assertRaises(Exception):
            self.compareToRange(value, 3.0, 2.9)
        with self.assertRaises(Exception):
            self.compareToRange(value, 3.1, 2.9)
        with self.assertRaises(Exception):
            self.compareToRange(value, 3, 3, True)

    @unittest.skip("This test has been superseded.")
    def testNextRestriction(self):
        self.fail("This test has been superseded.")

    # Replaces testNextRestriction.
    @unittest.skip("Not implemented yet.")
    def testNextRestrictedParemeterWithSingleInclusiveRange(self):
        paramId = someRestrictedPrimitive
        minLimit = -42
        maxLimit = 42
        iterations = 10
        for i in range(iterations):
            value = self.space.next(paramId)
            self.compareToRange(value, minLimit, maxLimit)

    # Replaces testNextRestriction.
    @unittest.skip("Not implemented yet.")
    def testNextRestrictedParameterWithMultipleExclusiveRanges(self):
        paramId = anotherRestrictedPrimitive
        firstMin = 0.1
        firstMax = 0.4
        secondMin = 0.8
        secondMax = 0.9
        iterations = 10
        for i in range(iterations):
            value = self.space.next(paramId)
            inFirstRange = inSecondRange = True
            # Check if the parameter is in
            try:
                self.compareToRange(value, firstMin, firstMax, True)
            except AssertionError:
                inFirstRange = False
            try:
                self.compareToRange(value, secondMin, secondMax, True)
            except AssertionError:
                inSecondRange = False
            self.assertTrue(inFirstRange or inSecondRange)

    # Replaces testNextRestriction.
    @unittest.skip("Not implemented yet.")
    def testNextRestrictedParameterWithSingleExclusiveRange(self):
        paramId = someVeryRestrictedPrimitive
        minLimit = 0.42222222222
        maxLimit = 0.422222222221
        iterations = 10
        for i in range(iterations):
            value = self.space.next(paramId)
            self.compareToRange(value, minLimit, maxLimit, True)

    @unittest.skip("This test has been superseded.")
    def testNextFixed(self):
        self.fail("This test has been superseded.")

    # Replaces testNextFixed.
    @unittest.skip("Not implemented yet.")
    def testNextFixedPrimitive(self):
        paramId = someFixed
        expected = 42
        value = self.space.next(paramId)
        self.assertEquals(expected, value)

    # Replaces testNextFixed.
    @unittest.skip("Not implemented yet.")
    def testNextFixedArray(self):
        paramId = someFixedArray
        expected = 42
        value = self.space.next(paramId)
        # Expecting array length and all element values to be 42.
        self.assertEquals(expected, len(value))
        for element in value:
            self.assertEquals(expected, element)

    def testNextEmptyDesign(self):
        designId = "designId"
        design = self.space.nextEmptyDesign(designId)
        self.assertEquals(designId, design.getId())

        for paramId in self.space.getSupportedParamIds():
            self.assertIsNone(design.getValue(paramId))

    def testNextReadOnlyDesign(self):
        designId = "designId"
        readOnly = True
        paramId = someBoolean
        design = self.space.nextDesign(designId, readOnly)
        # Trying to set a value for a read-only design should fail.
        with self.assertRaises(InPUTException):
            design.setValue(paramId, False)

    def compareLength(self, expected, data):
        self.assertEquals(expected, len(data))

    @unittest.skip("Not implemented yet.")
    def testNextWithDimensions(self):
        self.fail("Not implemented yet.")

    # Randomize lengths and/or number of dimensions in future versions.
    @unittest.skip("Not implemented yet.")
    def testNextWithMultidimensionalPrimitiveArray(self):
        paramId = someBoolean
        dimensions = (3, 4, 1)
        someBooleans = self.space.next(paramId, dimensions)
        self.compareDimensions(dimensions, someBooleans)

    @unittest.skip("Not implemented yet.")
    def testNextWithMultidimensionalStructuralArray(self):
        paramId = someStructural
        dimensions = (3, 4, 1)
        someStructural = self.space.next(paramId, dimensions)
        self.compareDimensions(dimensions, someStructural)

    @unittest.skip("Not implemented yet.")
    def testNegativeNextWithDimensions(self):
        self.fail("Not implemented yet.")

    @unittest.skip("Not implemented yet.")
    def testNextInjectCustomizedParameters(self):
        childId = anotherSharedPrimitiveSub
        parentId = someStructuralParent
        iterations = 20
        expected = 24
        subParams = {
            childId: expected,
            "SomeThingThatShouldNotHaveAnyImpact": "Foobar",
        }

        for i in range(iterations):
            parent = self.space.next(parentId, subParams)
            # This is slightly paranoid. The expected value is already known
            # because it was put into the subParams dictionary. Get it back
            # from the dictionary anyway to make sure that the dictionary
            # wasn't changed by the call to next().
            initialized = subParams[childId]
            self.assertEquals(expected, initialized)
            # Now check that the child parameter was initialized to the value
            # that was set in the dictionary.
            value = parent.getAnotherSharedPrimitiveSub()
            self.assertEquals(initialized, value)

    # This test, together with the previous one above, needs to be cleaned up.
    # They essentially do the same thing, so there should be a way to reduce
    # code duplication.
    @unittest.skip("Not implemented yet.")
    def testNextInjectCustomizedParametersAndConstructorOverwrite(self):
        childId = anotherSharedPrimitiveSub
        parentId = someStructuralParent
        iterations = 20
        expected = 24
        subParams = {
            childId: expected,
            "SomeThingThatShouldNotHaveAnyImpact": "Foobar",
        }
        actualParams = (14, 10.0)

        for i in range(iterations):
            parent = self.space.next(parentId, subParams, actualParams)
            # This is slightly paranoid. The expected value is already known
            # because it was put into the subParams dictionary. Get it back
            # from the dictionary anyway to make sure that the dictionary
            # wasn't changed by the call to next().
            initialized = subParams[childId]
            self.assertEquals(expected, initialized)
            # Now check that the child parameter was initialized to the value
            # that was set in the dictionary.
            value = parent.getAnotherSharedPrimitiveSub()
            self.assertEquals(initialized, value)

            # This part is unique compared with the previous test.
            value = parent.getSomeSharedPrimitiveSub()
            if isinstance(parent, YetAnotherSecondChoice):
                # This type uses a hard-coded argument to super().
                # It should ignore any extra parameters.
                self.assertEquals(42, value)
            else:
                # The other types use constructor arguments. They should be
                # overwritten by the values given in actualParams.
                self.assertEquals(actualParams[0], value)

    @unittest.skip("Not implemented yet.")
    def testNextInjectCustomizedParametersWithDimensions(self):
        self.fail("Not implemented yet.")

    @unittest.skip("Not implemented yet.")
    def testNextParameterConstructorOverwrite(self):
        actualParams = (14, 10.0)
        actualParamsWithBlank = (Q.BLANK, 10.0)
        iterations = 10
        paramId = someStructuralParent

        params = actualParams
        for i in range(iterations):
            param = self.space.next(paramId, params)
            self.firstParamTest(param, params)
            self.secondParamTest(param, params)

        params = actualParamsWithBlank
        for i in range(iterations):
            param = self.space.next(paramId, params)
            self.secondParamTest(param, params)

    def testIsFile(self):
        self.assertTrue(self.space.isFile())

    def testGetFileName(self):
        self.assertEquals(DESIGN_SPACE_FILE, self.space.getFileName())

    def testGetId(self):
        self.assertEquals("testSpace", self.space.getId())

    @unittest.skip("Not implemented yet.")
    def testGetSupportedParamIds(self):
        positive = (
            someStructural, someFloat, someDecimal,
        )
        negative = (
            "IDontExist", "somedecimal", None,
        )
        supported = self.space.getSupportedParamIds()
        for paramId in positive:
            self.assertTrue(paramId in supported)
        for paramId in negative:
            self.assertFalse(paramId in supported)

    @unittest.skip("Not implemented yet.")
    def testRelativeNumericConsistency(self):
        iterations = 10
        someLongId = someLong
        aBiggerLongId = aBiggerLong
        aSmallerLongId = aSmallerLong
        aStrangeLongId = aStrangeLong
        for i in range(iterations):
            design = self.space.nextDesign("someId")
            someLong = design.getValue(someLongId)
            aBiggerLong = design.getValue(aBiggerLongId)
            aSmallerLong = design.getValue(aSmallerLongId)
            aStrangeLong = design.getValue(aStrangeLongId)

            # ??? What do these comparisons mean?
            self.assertTrue(aBiggerLong > someLong)
            self.assertTrue(someLong >= aSmallerLong)
            value = someLong / aSmallerLong - aBiggerLong
            self.assertFalse(aStrangeLong >= value)

    @unittest.skip("Not implemented yet.")
    def testCustomizableInput(self):
        self.fail("Not implemented yet.")

    @unittest.skip("Not implemented yet.")
    def testComplexStructural(self):
        paramId = someComplexStructural
        value = self.space.next(paramId)
        cls = SecondSingleComplexChoice
        # The order of the choices has been fixed, so TheSecondSingleChoice
        # comes first, and then TheSingleChoice (which isn't the same type).
        self.assertTrue(isinstance(value.getEntry(0), cls))
        self.assertFalse(isinstance(value.getEntry(1), cls))

    @unittest.skip("Not implemented yet.")
    def testSetFixedNegative(self):
        self.fail("Not implemented yet.")

    def testSetFixedPrimitive(self):
        # Randomize the expected values in the future.
        params = {
            someInteger: 2,
            someBoolean: True,
        }

        for (paramId, expected) in params.items():
            self.checkFixed(paramId, expected)  # Use default iterations.

    def testSetFixedToNoneShouldTurnOffFixedStatus(self):
        params = (someInteger, someBoolean)
        for paramId in params:
            self.checkFixedOff(paramId)

    @unittest.skip("Not implemented yet.")
    def testSetFixedStructural(self):
        self.fail("Not implemented yet.")

    @unittest.skip("Not implemented yet.")
    def testSetFixedComplex(self):
        self.fail("Not implemented yet.")

    # ------------------------------------------------------------------------
    # Helper methods.
    # ------------------------------------------------------------------------

    # A value of None for expected is special. It means that we don't care
    # about the actual value, only that one could be retrieved. That means
    # that a literal None value can never be expected. This probably shouldn't
    # be a problem because (AFAIK?) None values aren't allowed.
    def getNextAndCompare(self, paramId, expected=None):
        value = self.space.next(paramId)
        if expected is None:
            self.assertIsNotNone(value)
        else:
            self.assertEquals(expected, value)

    # The comparisons are inclusive by default.
    def compareToRange(self, value, minLimit=None, maxLimit=None, excl=False):
        minLimit = minLimit or value
        maxLimit = maxLimit or value
        if excl:
            self.assertTrue(minLimit < value < maxLimit)
        else:
            self.assertTrue(minLimit <= value <= maxLimit)

    # Calls getNextAndCompare multiple times to make sure the generated value
    # is indeed fixed.
    def checkFixed(self, paramId, expected, iterations=10):
        self.space.setFixed(paramId, expected)  # Set fixed value.
        for i in range(iterations):
            self.getNextAndCompare(paramId, expected)

    # Keep fetching up to iterations new values and return as soon as a unique
    # one is encountered. Generating identical values constitutes failure.
    def checkFixedOff(self, paramId, iterations=10):
        self.space.setFixed(paramId, None)  # Set fixed status off.
        values = []
        for i in range(iterations):
            value = self.space.next(paramId)
            if len(values) > 0 and value not in values:
                return
            else:
                values.append(value)
        # Should have found a unique value and returned by now.
        self.fail("Unexpectedly got the same value %d times." % (iterations))

    # Check dimensions and length of multidimensional arrays recursively.
    def compareDimensions(self, dimensions, array):
        if len(dimensions) < 1:
            return
        else:
            length = dimensions[0]
            rest = dimensions[1:]
            self.assertEquals(length, len(array))
            # Check each element, not just the first one.
            for element in array:
                self.compareDimensions(rest, element)

    def firstParamTest(self, param, params):
        value = param.getSomeSharedPrimitiveSub()
        # If the parameter is of this type, then the value was set by the
        # constructor (using the hard-coded value). None of the others take a
        # constructor argument for this parameter, so in all other cases it
        # was initialized using the first element of actualParams argument.
        if isinstance(param, YetAnotherSecondChoice):
            self.assertEquals(42, value)
        else:
            self.assertEquals(params[0], value)

    def secondParamTest(self, param, params):
        if not isinstance(param, YetAnotherThirdChoice):
            return
        # We always expect the parameter to have been initialized by the
        # constructor using the second element of the actualParams argument.
        value = param.getSomeChoiceSpecificPrimitiveSub()
        self.assertEquals(params[1], value)


if __name__ == '__main__':
    unittest.main()
