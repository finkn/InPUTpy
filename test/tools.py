"""
test.tools

Tools that are useful for writing unit tests for InPUT.

Wherever possible, the test functions return as soon as a result is
available. This means that the iterations can usually be set quite high
without incurring any undue performance costs.

Functions with shortcuts: (exit as soon as possible)
- assertVariability (when a unique value is encountered)
- assertConstancy (when a unique value is encountered)
- assertMatchingArrayDimensions (when an array size is off)
- assertGeneratesAny (when any of the expected values is encountered)
- assertGeneratesAll (when all expected values have been encountered)
- assertGeneratesOnly (when an unexpected value is encountered)

Functions without shortcuts: (will always execute all the iterations)
- checkAnyValueMatches
- checkAllValuesMatch

Nonsensical values for iterations are not allowed.
An example would be checking for variability by generating 1 value.

The assertGeneratesAll function uses a default number of iterations that
is proportional to the number of expected values.

:copyright: (c) 2013 by Christoffer Fink.
:license: MIT. See LICENSE for details.
"""

import warnings

DEFAULT_ITERATIONS = 10

def assertVariability(f, iterations=DEFAULT_ITERATIONS):
    """ Assert that f will generate at least one unique value. """
    assert iterations > 1, '1 iteration makes no sense!'
    values = []
    for i in range(iterations):
        value = f()
        if value not in values and len(values) > 0:
            return True     # Found a new value.
        else:
            values.append(value)
    msg = 'Only generated %s for %i iterations' % (value, iterations)
    raise AssertionError(msg)

def assertConstancy(f, iterations=DEFAULT_ITERATIONS):
    """ Assert that f will only generate a constant value. """
    assert iterations > 1, '1 iteration makes no sense!'
    values = []
    for i in range(iterations):
        value = f()
        if value not in values and len(values) > 0:
            msg = 'Generated a unique value after %i iterations' % (iterations)
            raise AssertionError(msg)
        else:
            values.append(value)
    return True             # No variation after N iterations.


def assertMatchingArrayDimensions(sizes, array):
    """
    Assert that the array dimensions match the given sizes.
    The sizes are listed in order of nesting, which implies that the
    sub-arrays on each level must be uniformly sized.
    """
    size = sizes[0]
    if size != len(array):
        msg = '%i does not match length of %s' % (size, array)
        raise AssertionError(msg)
    if len(sizes) == 1:
        return True         # No more dimensions. Done.
    for element in array:
        # Check sub-arrays recursively.
        assertMatchingArrayDimensions(sizes[1:], element)
    return True


# Note that these two functions can be used in two different ways, simply
# by flipping the order of their arguments. The values can either be
# matched against expected values, or the other way around. Both are useful.

# TODO:
# These two still need to be replaced assert versions (or possibly removed).
def checkAnyValueMatches(values, expected):
    """
    Return whether any of the values match an expected value.
    The return value is True if and only if there exists some value v
    such that v is one of the expected values.
    """
    warnings.warn('use the assert version instead', DeprecationWarning)
    return any([v in expected for v in values])

def checkAllValuesMatch(values, expected):
    """
    Return whether all of the values match an expected value.
    The return value is True if and only if there does not exist some
    value v such that v is not one of the expected values.
    """
    warnings.warn('use the assert version instead', DeprecationWarning)
    return all([v in expected for v in values])


def assertGeneratesAny(f, expected, iterations=DEFAULT_ITERATIONS):
    """ Assert that f generates at least one expected value. """
    for i in range(iterations):
        if f() in expected:
            return True
    msg = 'Generated none of %s after %i iterations' % (expected, iterations)
    raise AssertionError(msg)

def assertGeneratesAll(f, expected, iterations=None):
    """
    Assert that f generates all expected values.
    If given, iterations must be >= the number of expected values.
    """
    if iterations is None:
        iterations = len(expected) * DEFAULT_ITERATIONS
    else:
        msg = 'Must generate at least as many values as are expected'
        assert iterations >= len(expected), msg

    expected = list(expected)   # Defensive copy.
    for i in range(iterations):
        v = f()
        if v in expected:
            expected.remove(v)
        if len(expected) == 0:
            return True
    msg = '%s still missing after %i iterations' % (expected, iterations)
    raise AssertionError(msg)

def assertGeneratesOnly(f, expected, iterations=DEFAULT_ITERATIONS):
    """ Assert that only expected values are generated by f. """
    for i in range(iterations):
        v = f()
        if v not in expected:
            raise AssertionError('%s not in %s' % (v, expected))
    return True


def generatorFromDesignSpace(space, paramId):
    """
    Return a function that will return a new value for the parameter.
    """
    return lambda: space.next(paramId)

def finiteGeneratorFromSeq(seq):
    """
    Return a function that will return the next item in the list.
    When all items have been returned, subsequent attempts to generate
    a value will raise an IndexError.
    """
    seq = list(seq) # Defensive copy.
    seq.reverse()
    return lambda: seq.pop()

def generatorFromSeq(seq):
    """
    Return a function that will return the next item in the sequence.
    When all items have been returned, the sequence starts over.
    The returned function is an infinite generator.
    """
    seq = list(seq) # Defensive copy.
    seq.reverse()
    def gen():
        x = seq.pop()
        seq.insert(0, x)
        return x
    return gen
