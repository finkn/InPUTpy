from inputpy.factories import XMLFactory
from inputpy.exceptions import InPUTException
from test import *
from inputpy import q as Q
import unittest

DESIGN_SPACE_FILE = "testSpace.xml"
space = None

class TestDesignSpace(unittest.TestCase):

    def setUp(self):
        global space
        self.space = XMLFactory.getDesignSpace(DESIGN_SPACE_FILE)
        space = self.space

    def tearDown(self):
        global space
        del space
        del self.space

    @unittest.skip("Not implemented yet.")
    def testDesignSpaceWithMappingAsInputStreams(self):
        self.fail("Not implemented yet.")

    @unittest.skip("Not implemented yet.")
    def testDesignSpaceFromFile(self):
        self.tearDown()
        space = DesignSpace(DESIGN_SPACE_FILE)

    @unittest.skip("Not implemented yet.")
    def testDesignSpaceFromInputStream(self):
        self.fail("Not implemented yet.")

    def testNextPrimitive(self):
        params = (
            SOME_BOOLEAN, SOME_INTEGER, SOME_SHORT, SOME_LONG,
            SOME_DOUBLE, SOME_FLOAT, SOME_DECIMAL,
        )
        for param in params:
            self.getNextAndCompare(param)

    def testNextString(self):
        paramId = 'SomeStringCustomizedByTheUser'
        expected = paramId
        anotherParamId = 'AnotherStringCustomizedByTheUser'
        arrayParamId = 'SomeStringArrayCustomizedByTheUser'
        expectedAlternatives = (
            "someFile.xml", "someFile.txt", "anotherFile.xml"
        )
        # Test the first parameter.
        value = space.next(paramId)
        self.assertEqual(expected, value)
        # Test the next one. The value should be one of the alternatives.
        value = space.next(anotherParamId)
        self.assertTrue(value in expectedAlternatives)

        # Test an array of strings.
        values = space.next(arrayParamId)
        self.assertEqual(10, len(values))
        self.assertEqual(5, len(values[0]))
        # Every element is expected to have the same value: same as the id.
        for array in values:
            for element in array:
                self.assertEqual(arrayParamId, element)

    def testNextStructural(self):
        paramIds = (
            SOME_STRUCTURAL, #ANOTHER_STRUCTURAL,
            SOME_STRUCTURAL_PARENT, ANOTHER_STRUCTURAL_PARENT,
        )
        for param in paramIds:
            self.getNextAndCompare(param)

    # The Java version has a single testNextArray test.
    # That test has been split into the individual cases below.
    @unittest.skip("This test has been superseded.")
    def testNextArray(self):
        self.fail("This test has been superseded.")

    # Replaces testNextArray.
    def testNextPrimitiveArrayOfUnspecifiedSize(self):
        paramId = "SomePrimitiveArrayOfUnspecifiedSize"
        expectedLength = 1
        array = space.next(paramId)
        self.assertEqual(expectedLength, len(array))

    # Replaces testNextArray.
    def testNextPrimitiveArrayOfSpecifiedSize(self):
        paramId = "SomePrimitiveArrayOfSpecifiedSize"
        expectedLength = 42
        array = space.next(paramId)
        self.assertEqual(expectedLength, len(array))

    # Replaces testNextArray.
    def testNextStructuralMultidimensionalArrayOfUnspecifiedSize(self):
        paramId = "SomeStructuralArrayOfUnspecifiedSize"
        expectedLength = 1
        array = space.next(paramId)
        self.assertEqual(expectedLength, len(array))

    # Replaces testNextArray.
    def testNextPrimitiveMultidimensionalArray(self):
        paramId = "SomeLargePrimitiveArray"
        expectedLengthD0 = 10
        expectedLengthD1 = 1
        expectedLengthD2 = 10
        expectedLengthD3 = 1
        array = space.next(paramId)
        self.assertEqual(expectedLengthD0, len(array))
        self.assertEqual(expectedLengthD1, len(array[0]))
        self.assertEqual(expectedLengthD2, len(array[0][0]))
        self.assertEqual(expectedLengthD3, len(array[0][0][0]))

    # The Java version has a single testNextNegative test.
    # That test has been split into the individual cases below.
    # However, the casting test has been skipped because Python is kewl.
    @unittest.skip("This test has been superseded.")
    def testNextNegative(self):
        self.fail("This test has been superseded.")

    # Replaces testNextNegative.
    def testNextWithUnknownParameterShouldReturnNone(self):
        paramId = "ParamThatDoesNotExist"
        self.assertIsNone(space.next(paramId))

    # Replaces testNextNegative.
    def testNextWithNoneParameterShouldReturnNone(self):
        self.assertIsNone(space.next(None))

    # The Java version has a single testNextSubParameter test.
    # That test has been split into the individual cases below.
    @unittest.skip("This test has been superseded.")
    def testNextSubParameter(self):
        self.fail("This test has been superseded.")

    # Replaces testNextSubParameter.
    def testNextPrimitiveSubParameter(self):
        paramId = SOME_STRUCTURAL_PARENT + "." + SOME_SHARED_PRIMITIVE_SUB
        self.getNextAndCompare(paramId)

    # Replaces testNextSubParameter.
    @unittest.skip("Not implemented yet.")
    def testNextStructuralSubParameter(self):
        paramId = 'AnotherStructuralParent.AndYetAnotherSecondChoice.SomeChoiceSpecificStructuralSub.AlsoSingleChoicesAreValid'
        self.getNextAndCompare(paramId)

    # Replaces testNextSubParameter.
    def testNextChoiceParameter(self):
        paramId = ANOTHER_STRUCTURAL_PARENT + "." + AND_YET_ANOTHER_SECOND_CHOICE
        self.getNextAndCompare(paramId)

    # Test test.
    @unittest.skip("Already verified, temporarily disabled.")
    def testCompareToRange(self):
        value = space.next("whatever")
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
    def testNextRestrictedParemeterWithSingleInclusiveRange(self):
        paramId = "SomeRestrictedPrimitive"
        minLimit = -42
        maxLimit = 42
        iterations = 10
        for i in range(iterations):
            value = space.next(paramId)
            self.compareToRange(value, minLimit, maxLimit)

    # Replaces testNextRestriction.
    def testNextRestrictedParameterWithMultipleExclusiveRanges(self):
        paramId = "AnotherRestrictedPrimitive"
        firstMin = 0.1
        firstMax = 0.4
        secondMin = 0.8
        secondMax = 0.9
        iterations = 10
        for i in range(iterations):
            value = space.next(paramId)
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
    #@unittest.skip("Not implemented yet.")
    def testNextRestrictedParameterWithSingleExclusiveRange(self):
        paramId = "SomeVeryRestrictedPrimitive"
        minLimit = 0.42222222222
        maxLimit = 0.422222222221
        iterations = 10
        for i in range(iterations):
            value = space.next(paramId)
            self.compareToRange(value, minLimit, maxLimit, True)

    @unittest.skip("This test has been superseded.")
    def testNextFixed(self):
        self.fail("This test has been superseded.")

    # Replaces testNextFixed.
    def testNextFixedPrimitive(self):
        paramId = "SomeFixed"
        expected = 42
        value = space.next(paramId)
        self.assertEqual(expected, value)

    # Replaces testNextFixed.
    #@unittest.skip("Not implemented yet.")
    def testNextFixedArray(self):
        #paramId = someFixedArray
        paramId = "SomeFixedArray"
        expected = 42
        value = space.next(paramId)
        # Expecting array length and all element values to be 42.
        self.assertEqual(expected, len(value))
        for element in value:
            self.assertEqual(expected, element)

    def testNextEmptyDesign(self):
        designId = "designId"
        design = space.nextEmptyDesign(designId)
        self.assertEqual(designId, design.getId())

        for paramId in space.getSupportedParamIds():
            self.assertIsNone(design.getValue(paramId))

    def testNextReadOnlyDesign(self):
        designId = "designId"
        readOnly = True
        paramId = SOME_BOOLEAN
        design = space.nextDesign(designId, readOnly)
        # Trying to set a value for a read-only design should fail.
        with self.assertRaises(InPUTException):
            design.setValue(paramId, False)

    def compareLength(self, expected, data):
        self.assertEqual(expected, len(data))

    @unittest.skip("Not implemented yet.")
    def testNextWithDimensions(self):
        self.fail("Not implemented yet.")

    # Randomize lengths and/or number of dimensions in future versions.
    @unittest.skip("Not implemented yet.")
    def testNextWithMultidimensionalPrimitiveArray(self):
        paramId = "SomeBoolean"
        dimensions = (3, 4, 1)
        someBooleans = space.next(paramId, dimensions)
        self.compareDimensions(dimensions, someBooleans)

    @unittest.skip("Not implemented yet.")
    def testNextWithMultidimensionalStructuralArray(self):
        paramId = someStructural
        dimensions = (3, 4, 1)
        someStructural = space.next(paramId, dimensions)
        self.compareDimensions(dimensions, someStructural)

    @unittest.skip("Not implemented yet.")
    def testNegativeNextWithDimensions(self):
        self.fail("Not implemented yet.")

    @unittest.skip("Not implemented yet.")
    def testNextInjectCustomizedParameters(self):
        childId = "AnotherSharedPrimitiveSub"
        parentId = "SomeStructuralParent"
        iterations = 20
        expected = 24
        subParams = {
            childId: expected,
            "SomeThingThatShouldNotHaveAnyImpact": "Foobar",
        }

        for i in range(iterations):
            parent = space.next(parentId, subParams)
            # This is slightly paranoid. The expected value is already known
            # because it was put into the subParams dictionary. Get it back
            # from the dictionary anyway to make sure that the dictionary
            # wasn't changed by the call to next().
            initialized = subParams[childId]
            self.assertEqual(expected, initialized)
            # Now check that the child parameter was initialized to the value
            # that was set in the dictionary.
            value = parent.getAnotherSharedPrimitiveSub()
            self.assertEqual(initialized, value)

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
            parent = space.next(parentId, subParams, actualParams)
            # This is slightly paranoid. The expected value is already known
            # because it was put into the subParams dictionary. Get it back
            # from the dictionary anyway to make sure that the dictionary
            # wasn't changed by the call to next().
            initialized = subParams[childId]
            self.assertEqual(expected, initialized)
            # Now check that the child parameter was initialized to the value
            # that was set in the dictionary.
            value = parent.getAnotherSharedPrimitiveSub()
            self.assertEqual(initialized, value)

            # This part is unique compared with the previous test.
            value = parent.getSomeSharedPrimitiveSub()
            if isinstance(parent, YetAnotherSecondChoice):
                # This type uses a hard-coded argument to super().
                # It should ignore any extra parameters.
                self.assertEqual(42, value)
            else:
                # The other types use constructor arguments. They should be
                # overwritten by the values given in actualParams.
                self.assertEqual(actualParams[0], value)

    @unittest.skip("Not implemented yet.")
    def testNextInjectCustomizedParametersWithDimensions(self):
        self.fail("Not implemented yet.")

    @unittest.skip("Not implemented yet.")
    def testNextParameterConstructorOverwrite(self):
        actualParams = (14, 10.0)
        actualParamsWithBlank = (Q.BLANK, 10.0)
        iterations = 10
        paramId = "SomeStructuralParent"

        params = actualParams
        for i in range(iterations):
            param = space.next(paramId, params)
            self.firstParamTest(param, params)
            self.secondParamTest(param, params)

        params = actualParamsWithBlank
        for i in range(iterations):
            param = space.next(paramId, params)
            self.secondParamTest(param, params)

    def testIsFile(self):
        self.assertTrue(space.isFile())

    def testGetFileName(self):
        self.assertEqual(DESIGN_SPACE_FILE, space.getFileName())

    def testGetId(self):
        self.assertEqual("testSpace", space.getId())

    def testGetSupportedParamIds(self):
        positive = ("SomeStructural", "SomeFloat", "SomeDecimal",)
        negative = ("IDontExist", "somedecimal", None,)
        supported = space.getSupportedParamIds()
        for paramId in positive:
            self.assertTrue(paramId in supported)
        for paramId in negative:
            self.assertFalse(paramId in supported)

    def testRelativeNumericConsistency(self):
        iterations = 10
        someLongId = "SomeLong"
        aBiggerLongId = "ABiggerLong"
        aSmallerLongId = "ASmallerLong"
        aStrangeLongId = "AStrangeLong"
        for i in range(iterations):
            design = space.nextDesign("someId")
            someLong = design.getValue(someLongId)
            aBiggerLong = design.getValue(aBiggerLongId)
            aSmallerLong = design.getValue(aSmallerLongId)
            aStrangeLong = design.getValue(aStrangeLongId)

            # ??? What do these comparisons mean?
            self.assertTrue(aBiggerLong > someLong)
            self.assertTrue(someLong >= aSmallerLong)
            value = someLong / aSmallerLong - aBiggerLong
            self.assertTrue(aStrangeLong >= value)

    @unittest.skip("Not implemented yet.")
    def testCustomizableInput(self):
        self.fail("Not implemented yet.")

    @unittest.skip("Not implemented yet.")
    def testComplexStructural(self):
        paramId = "SomeComplexStructural"
        value = space.next(paramId)
        cls = SecondSingleComplexChoice
        # The order of the choices has been fixed, so TheSecondSingleChoice
        # comes first, and then TheSingleChoice (which isn't the same type).
        self.assertIsInstance(value.getEntry(0), cls)
        self.assertNotIsInstance(value.getEntry(1), cls)

    @unittest.skip("Not implemented yet.")
    def testSetFixedNegative(self):
        self.fail("Not implemented yet.")

    def testSetFixedPrimitive(self):
        # Randomize the expected values in the future.
        params = {
            SOME_INTEGER: 2,
            SOME_BOOLEAN: True,
        }

        for (paramId, expected) in params.items():
            self.checkFixed(paramId, expected)  # Use default iterations.

    def testSetFixedToNoneShouldTurnOffFixedStatus(self):
        params = (SOME_INTEGER, SOME_BOOLEAN)
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
        value = space.next(paramId)
        msg = 'got wrong value for %s' % (paramId)
        if expected is None:
            self.assertIsNotNone(value, msg=msg)
        else:
            self.assertEqual(expected, value, msg=msg)

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
        space.setFixed(paramId, expected)  # Set fixed value.
        for i in range(iterations):
            self.getNextAndCompare(paramId, expected)

    # Keep fetching up to iterations new values and return as soon as a unique
    # one is encountered. Generating identical values constitutes failure.
    def checkFixedOff(self, paramId, iterations=10):
        space.setFixed(paramId, None)  # Set fixed status off.
        values = []
        for i in range(iterations):
            value = space.next(paramId)
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
            self.assertEqual(length, len(array))
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
            self.assertEqual(42, value)
        else:
            self.assertEqual(params[0], value)

    def secondParamTest(self, param, params):
        if not isinstance(param, YetAnotherThirdChoice):
            return
        # We always expect the parameter to have been initialized by the
        # constructor using the second element of the actualParams argument.
        value = param.getSomeChoiceSpecificPrimitiveSub()
        self.assertEqual(params[1], value)


if __name__ == '__main__':
    unittest.main()
